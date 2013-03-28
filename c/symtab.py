from pycparser import c_ast
from backend import function

#This class walks the AST keeping a stack of dictionaries corresponding to 
#C scopes, then whenever it encounters a use of an ID or decl with an init it attempts to lookup
#the id in the stack of scopes and then stores a dict of IDnodes : Symbols



class Symbol(object):
    
    def __init__(self,name,t):
        self.name = name
        self.type = t
    def __repr__(self):
        return "%s Symbol: %s"%(self.__class__.__name__,self.name)

class Global(Symbol):
    pass

class Param(Symbol):
    pass

class Local(Symbol):
    def __init__(self,name,t):
        Symbol.__init__(self,name,t)
        self.slot = function.StackSlot(4)


GLOBAL = 0
PARAM = 1
LOCAL = 2

declclasses = [Global,Param,Local]

class SymTab(c_ast.NodeVisitor):
    def __init__(self):
        self._symbols = {}
        self._scopes = []
        self._scopeState = GLOBAL
    
    def _pushScope(self):
        self._scopes.append({})
        
    def _popScope(self):
        self._scopes.pop()
    
    def _addSymbol(self,sym):
        self._scopes[-1][sym.name] = sym
    
    def _lookupSymbol(self,name):
        for scope in reversed(self._scopes):
            if name in scope:
                return scope[name]
        raise Exception("undefined variable %s"%name)
        
    def lookupID(self,node):
        return self._symbols[node]
    
    def visit_FileAST(self,node):
        self._scopeState = GLOBAL
        self._pushScope()
        self.generic_visit(node)
        self._popScope()
        assert(len(self._scopes) == 0)

    def visit_FuncDef(self,node):
        self._pushScope()
        self.generic_visit(node)
        self._popScope()
        self._scopeState = GLOBAL
    
    def visit_ParamList(self,node):
        self._scopeState = PARAM
        self.generic_visit(node)
        
    def visit_Decl(self,decl):
        declClass = declclasses[self._scopeState]
        sym = declClass(decl.name,decl.type)
        self._addSymbol(sym)
        self._symbols[decl] = sym
        self.generic_visit(decl)
        
    def visit_Compound(self,compound):
        self._scopeState = LOCAL
        self._pushScope()
        self.generic_visit(compound)
        self._popScope()
        
    def visit_ID(self,node):
        sym = self._lookupSymbol(node.name)
        self._symbols[node] = sym
    



