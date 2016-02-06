// Copyright 2015 The Rust Project Developers. See the COPYRIGHT
// file at the top-level directory of this distribution and at
// http://rust-lang.org/COPYRIGHT.
//
// Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
// http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
// <LICENSE-MIT or http://opensource.org/licenses/MIT>, at your
// option. This file may not be copied, modified, or distributed
// except according to those terms.

#![feature(deprecated)]

// @has deprecated/struct.S.html '//*[@class="stab deprecated"]' \
//      'Deprecated since 1.0.0: text'
#[deprecated(since = "1.0.0", note = "text")]
pub struct S;

/* !search-index
{
    "deprecated": {
        "deprecated::S": [
            "Struct"
        ]
    }
}
*/
