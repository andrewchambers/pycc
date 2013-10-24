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

Operation:

pycparser parses the C code into an AST, which is then passed to the files  c/frontend.py -> c/irgen.py. irgen.py walks the
ast generating ir and handling scope and type changes with a scope/symbol/type stack as it goes.

After this ir is generated it is passed into backend/standardmachine.py this is subclassed by specific backends (x86 is the only existing one). standardmachine.py calls various optimizers and machine hooks including
a graph coloring register allocator and converting 3 argument instructions into 2 argument instructions when needed. The main entry point of the backend is backend/standardmachine.translateFunction. The resulting function is now entirely machine specific which is finally output to text assembly.

Instruction selection uses pattern classes which resembles gcc or llvm pattern based matches, but are implemented in python. For example https://github.com/andrewchambers/cc/blob/master/backend/x86/x86md.py contains the x86 instruction definitions.

I believe performance can be acceptable using the pypy JIT compiler, but only if the compiler runs as a server to allow the jit caches to warm up :). Ram usage is pretty massive hahaha.
