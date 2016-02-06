// Copyright 2015 The Rust Project Developers. See the COPYRIGHT
// file at the top-level directory of this distribution and at
// http://rust-lang.org/COPYRIGHT.
//
// Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
// http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
// <LICENSE-MIT or http://opensource.org/licenses/MIT>, at your
// option. This file may not be copied, modified, or distributed
// except according to those terms.

// aux-build:issue-22025.rs
// ignore-cross-compile

extern crate issue_22025;

pub use issue_22025::foo::{Foo, Bar};

/* !search-index
{
    "issue_22025": {
        "issue_22025::Bar": [
            "Struct"
        ],
        "issue_22025::Foo": [
            "Trait"
        ]
    }
}
*/
