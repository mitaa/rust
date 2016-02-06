// Copyright 2015 The Rust Project Developers. See the COPYRIGHT
// file at the top-level directory of this distribution and at
// http://rust-lang.org/COPYRIGHT.
//
// Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
// http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
// <LICENSE-MIT or http://opensource.org/licenses/MIT>, at your
// option. This file may not be copied, modified, or distributed
// except according to those terms.

// @has macros/macro.my_macro!.html //pre 'macro_rules! my_macro {'
// @has - //pre '() => { ... };'
// @has - //pre '($a:tt) => { ... };'
// @has - //pre '($e:expr) => { ... };'
#[macro_export]
macro_rules! my_macro {
    () => [];
    ($a:tt) => ();
    ($e:expr) => {};
}

/* !search-index
{
    "macros": {
        "macros::my_macro!": [
            "Macro"
        ]
    }
}
*/
