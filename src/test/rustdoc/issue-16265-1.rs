// Copyright 2015 The Rust Project Developers. See the COPYRIGHT
// file at the top-level directory of this distribution and at
// http://rust-lang.org/COPYRIGHT.
//
// Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
// http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
// <LICENSE-MIT or http://opensource.org/licenses/MIT>, at your
// option. This file may not be copied, modified, or distributed
// except according to those terms.

pub struct Foo;

// @has issue_16265_1/traits/index.html '[src]'
pub mod traits {
    impl PartialEq for super::Foo {
        fn eq(&self, _: &super::Foo) -> bool { true }
    }
}

/* !search-index
{
    "issue_16265_1": {
        "issue_16265_1::Foo": [
            "Struct"
        ],
        "issue_16265_1::Foo<Struct>::eq": [
            "Method(foo, foo) -> bool"
        ],
        "issue_16265_1::traits": [
            "Module"
        ]
    }
}
*/
