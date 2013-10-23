cc
==

goal is fully compliant c99 compiler in python/pypy. 


status -- missing floating point,bitfield and union support, currently refactoring global initialisers, so feature is disabled,
The diagnostics for the compiler need improvement to be truly useable.

The compiler is buggy and incomplete but some of its code including its register allocator and some SSA algorithms are 
useful imo.

email me at andrewchamberss@gmail.com for more info about issues and implementation details.


To run the tests you must first have gcc installed aswell as py.test. 
To run the tests run the command:
>py.test
