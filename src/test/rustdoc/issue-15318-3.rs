// Copyright 2015 The Rust Project Developers. See the COPYRIGHT
// file at the top-level directory of this distribution and at
// http://rust-lang.org/COPYRIGHT.
//
// Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
// http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
// <LICENSE-MIT or http://opensource.org/licenses/MIT>, at your
// option. This file may not be copied, modified, or distributed
// except according to those terms.

// @has issue_15318_3/primitive.pointer.html

/// dox
#[doc(primitive = "pointer")]
pub mod ptr {}

/* !search-index
{
    "issue_15318_3": {
        "issue_15318_3::pointer": [
            "Primitive",
            "dox"
        ],
        "issue_15318_3::ptr": [
            "Module",
            "dox"
        ]
    }
}
*/
