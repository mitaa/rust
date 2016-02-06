#!/usr/bin/env python
#
# Copyright 2013-2016 The Rust Project Developers. See the COPYRIGHT
# file at the top-level directory of this distribution and at
# http://rust-lang.org/COPYRIGHT.
#
# Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
# http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
# <LICENSE-MIT or http://opensource.org/licenses/MIT>, at your
# option. This file may not be copied, modified, or distributed
# except according to those terms.

from __future__ import print_function

import sys
import os
import json
import re
import argparse


ERRS = []

class Error(Exception):
    pass
class InvalidType(Error):
    pass

def stderr(*args, **kwargs):
    kwargs.update({ "file": sys.stderr })
    print(*args, **kwargs)

def record_errs(*errs):
    global ERRS
    ERRS += errs

def abort_on_errs():
    if ERRS:
        for err in ERRS:
            stderr(err)
        stderr("\nEncountered {} syntax errors".format(len(ERRS)))
        raise SystemExit(1)

class IndexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Item):
            return obj._encode()
        return json.JSONEncoder.default(self, obj)

class Item:
    _index_map = {}
    _ref_map = {}
    _re_fn = re.compile(r"(?P<type>\w+)(\((?P<inputs>.+)\) ?((->)? ?(?P<outputs>\w+))?)?")

    @classmethod
    def from_index(klass, crate, data):
        try:
            item = klass._index_map[data[0]]()
        except KeyError as e:
            path = data[2] or crate._items[-1].path
            if data[4]:
                try:
                    path += "::" + crate.paths[data[4]][1]
                except IndexError:
                    path += "::<anon>"
            path += "::" + data[1]
            raise InvalidType("{} -> invalid type index `{}`".format(path, e))

        item._init_from_index(crate, data)
        return item

    def _init_from_index(self, crate, data):
        self._name = data[1]
        self._parent_idx = data[4]

        self.path = data[2] or crate._items[-1].path
        self.description = data[3]
        self.fn_inputs = tuple()
        self.fn_outputs = None
        assert self.path

        if data[5]:
            self.fn_inputs = tuple(map(lambda i: i["name"], data[5]["inputs"]))
            self.fn_outputs = (data[5]["output"] or {}).get("name", None)

    def finalize_index(self, crate):
        if self._parent_idx is not None:
            self.path += "::" + crate.paths[self._parent_idx][1]
        self.path += "::" + self._name

    @classmethod
    def from_ref(klass, path, data):
        match = klass._re_fn.match(data[0])
        ty = match.group("type")

        try:
            item = klass._ref_map[ty]()
        except KeyError as e:
            raise InvalidType("{} -> invalid type `{}`".format(path, e))
        item._init_from_ref(path, data, match)
        return item

    def _init_from_ref(self, path, data, extra):
        self._name = path.split("::")[-1]
        self.path = path
        self.description = "" if len(data) == 1 else data[1]
        inputs = extra.group("inputs")
        self.fn_inputs = tuple(inp.strip() for inp in inputs.split(",")) if inputs else tuple()
        self.fn_outputs = extra.group("outputs")

    def __eq__(self, other):
        return (self.typename, self.path, self.fn_inputs, self.fn_outputs) == \
               (other.typename, other.path, other.fn_inputs, other.fn_outputs)

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return str(self._encode())

    def _encode(self):
        if isinstance(self, (TyFn, TyMethod, TyTyMethod)):
            sig = "{}({})".format(self.typename, ", ".join(self.fn_inputs))
            if self.fn_outputs:
                sig += " -> {}".format(self.fn_outputs)
            head = sig
        else:
            head = self.typename

        return [head, self.description] if self.description else [head]

    def diff(self, other, diff):
        """Emit a diff of `self` and `other`, and return `(insertions, deletions)`."""
        if self != other:
            print("- {} {}".format(self.path, self), file=diff)
            print("+ {} {}".format(other.path, other), file=diff)
            return (1, 1)
        else:
            return (0, 0)

def itemtype(idx, tydesc):
    class SpecificItem(Item):
        pass

    SpecificItem.typename = tydesc
    assert idx not in Item._index_map
    Item._index_map[idx] = SpecificItem
    Item._ref_map[tydesc] = SpecificItem
    return SpecificItem

TyMod               = itemtype(0, "Module")
TyCrate             = itemtype(1, "ExternCrate")
TyUse               = itemtype(2, "Import")
TyStruct            = itemtype(3, "Struct")
TyEnum              = itemtype(4, "Enum")
TyFn                = itemtype(5, "Function")
TyTypeDef           = itemtype(6, "Typedef")
TyStatic            = itemtype(7, "Static")
TyTrait             = itemtype(8, "Trait")
TyImpl              = itemtype(9, "Impl")
TyTyMethod          = itemtype(10, "TyMethod")
TyMethod            = itemtype(11, "Method")
TyStructField       = itemtype(12, "StructField")
TyVariant           = itemtype(13, "Variant")
TyMacro             = itemtype(14, "Macro")
TyPrimitive         = itemtype(15, "Primitive")
TyAssociatedType    = itemtype(16, "AssociatedType")
TyConst             = itemtype(17, "Constant")
TyAssociatedConst   = itemtype(18, "AssociatedConst")

class Index(dict):
    def diff(self, other, diff):
        """Emit a diff of `self` and `other`, and return `(insertions, deletions)`."""
        insertions = 0
        deletions = 0

        self_keys = iter(sorted(self.keys()))
        other_keys = iter(sorted(other.keys()))

        try:
            other_key = next(other_keys)
        except StopIteration:
            other_key = None

        for key in self_keys:
            while other_key < key and other_key is not None:
                print("+ {}".format(other_key), file=diff)
                del other[other_key]
                insertions += 1
                try:
                    other_key = next(other_keys)
                except StopIteration:
                    other_key = None
                    break

            if key == other_key:
                add, rm = self.pop(key).diff(other.pop(other_key), diff)
                insertions += add
                deletions += rm

                try:
                    other_key = next(other_keys)
                except StopIteration:
                    other_key = None
            else:
                print("- {}".format(key), file=diff)
                del self[key]
                deletions += 1

        insertions += len(other.keys())
        deletions += len(self.keys())
        diff_keys = sorted([("-", k) for k in self.keys()] +\
                           [("+", k) for k in other.keys()], key=lambda a:a[1])
        for mode, key in diff_keys:
            print("{} {}".format(mode, key), file=diff)

        return (insertions, deletions)


class Crate(Index):
    @classmethod
    def from_index(klass, raw_data):
        crate = klass()
        crate.paths = tuple((Item._index_map[idx], name) for (idx, name) in raw_data["paths"])
        crate._items = []

        for raw_item in raw_data["items"]:
            try:
                crate._items += [Item.from_index(crate, raw_item)]
            except Error as e:
                record_errs(e)

        for item in crate._items:
            item.finalize_index(crate)
            crate[item.path] = item

        del crate._items
        return crate

    @classmethod
    def from_ref(klass, raw_items):
        crate = klass()

        for path, data in raw_items.items():
            try:
                crate[path] = Item.from_ref(path, data)
            except Error as e:
                record_errs(e)
        return crate

    def __eq__(self, other):
        for path, item in self.items():
            other_item = other.get(path)
            if other_item is None or other_item != item:
                return False
        return True

def index_load(fpath):
    with open(fpath, "r") as fp:
        return index_loads(fp.read())
index_load._format = "search-index"

def index_loads(src):
    index = Index()
    for crateline in src.splitlines()[1:-1]:
        _, cratename, rest = crateline.split("'", 2)
        crateitems = json.loads(rest.split("=", 1)[1].strip()[:-1])
        index[cratename] = Crate.from_index(crateitems)
    return index

def ref_load(fpath):
    with open(fpath, "r") as fp:
        return ref_loads(fp.read())
ref_load._format = "reference-index"

def ref_loads(src):
    match = RE_REF.search(src)
    if match is not None:
        index = Index()
        ref = match.groups()[0].strip()
        for (cratename, data) in json.loads(ref).items():
            index[cratename] = Crate.from_ref(data)
        return index
    raise SyntaxError("can't find embedded reference-index")

DIFF_MSG = """
{} insertions(+), {} deletions(-)

Error -> distinct search-index"""

def try_load(path, loaders):
    errs = []
    temp = "{} -> failed to parse as `{}`:\n\t{}"
    for loader in loaders:
        try:
            return loader(path)
        except Exception as err:
            errs += [temp.format(path, loader._format, err)]
    record_errs(*errs)
    abort_on_errs()

def dumps(index, indent=4):
    return json.dumps(index, cls=IndexEncoder, indent=indent, sort_keys=True)

RE_REF = re.compile(r"/\*\s?!search-index\s(.*)\*/", flags=re.MULTILINE|re.DOTALL)
REF_FENCE = "/* !search-index\n{}\n*/"

def dump_index(args):
    index = try_load(args.index_path, (index_load, ref_load))
    abort_on_errs()
    print(REF_FENCE.format(dumps(index, indent=args.indent)))

def check_index(args):
    index = try_load(args.check_index, (index_load, ref_load))
    ref = try_load(args.base_index, (ref_load, index_load))
    abort_on_errs()
    insertions, deletions = ref.diff(index, sys.stderr)

    if insertions or deletions:
        stderr(DIFF_MSG.format(insertions, deletions))
        raise SystemExit(1)

def update_ref(args):
    source = try_load(args.source, (index_load, ref_load))
    abort_on_errs()
    with open(args.destination, "r") as fp:
        template = fp.read()
        new, n = RE_REF.subn(REF_FENCE.format(dumps(source)), template)
    if n != 1:
        stderr("Error -> less or more than a single embedded reference-index")
        raise SystemExit(1)

    root, fname = os.path.split(args.destination)
    bak_path = os.path.join(root, "." + fname + ".bak")
    os.rename(args.destination, bak_path)
    try:
        fp = open(args.destination, "w")
        fp.writelines([line.rstrip() + '\n' for line in new.splitlines()])
        os.remove(bak_path)
    except Exception as e:
        os.remove(args.destination)
        os.rename(bak_path, args.destination)
        stderr("Error -> failed writing new reference-index:\n\t{}".format(e))
        raise SystemExit(1)

def create_parser():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()

    dump = sub.add_parser("dump", help="dump a {search, reference}-index as reference-index")
    dump.add_argument("index_path", metavar="index-filepath")
    dump.add_argument("--indent", type=int, default=4)
    dump.set_defaults(func=dump_index)

    check = sub.add_parser("check", help="check a {search, reference}-index against another one")
    check.add_argument("check_index", metavar="check-index")
    check.add_argument("base_index", metavar="base-index")
    check.set_defaults(func=check_index)

    update = sub.add_parser("update",
                            help="overwrite a reference-index from a {search, reference}-index")
    update.add_argument("source")
    update.add_argument("destination")
    update.set_defaults(func=update_ref)
    return parser

if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args(sys.argv[1:])
    args.func(args)
