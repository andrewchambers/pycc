from pycparser import c_ast


#This class walks the AST keeping a stack of dictionaries corresponding to 
#C scopes, then whenever it encounters a use of an ID it attempts to lookup
#the id in the stack of scopes and then stores a dict of IDnodes : Symbols

class SymTab(c_ast.NodeVisitor):
    def __init__(self):
        self._symbols = {}
        self._scopes = []
    
    
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
    
    def visit_FuncDef(self,node):
        print("visiting paramlist")
        self._pushScope()
        self.generic_visit(node)
        self._popScope()
    
    def visit_ParamList(self,node):
        pass
        
    def visit_Decl(self,decl):
        sym = Local(decl.name,decl.type)
        self._addSymbol(sym)
        
    def visit_Compound(self,compound):
        self._pushScope()
        self.generic_visit(compound)
        self._popScope()
        
    def visit_ID(self,node):
        sym = self._lookupSymbol(node.name)
        self._symbols[node] = sym
    

class Symbol(object):
    
    def __init__(self,name,t):
        self.name = name
        self.type = t
    
class Param(Symbol):
    pass

class Local(Symbol):
    pass




