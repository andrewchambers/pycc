from pycparser import c_ast
from backend import function

import types

#This class walks the AST keeping a stack of dictionaries corresponding to 
#C scopes, then whenever it encounters a use of an ID or decl with an init it attempts to lookup
#the id in the stack of scopes and then stores a dict of IDnodes : Symbols







