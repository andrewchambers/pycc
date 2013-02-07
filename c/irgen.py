from pycparser import c_ast

from backend import module
from backend import function
from backend import basicblock
from backend import ir

class IRGenerator(c_ast.NodeVisitor):
    
    def __init__(self):
        self.module = None
        self.curfunction = None
    
    def visit_FileAST(self,node):
        self.module = module.Module()
        self.generic_visit(node)
        
    def visit_FuncDef(self,node):
        print('visiting a func def...')
        node.show()
        self.curFunction = function.Function()
        self.curBasicBlock = basicblock.BasicBlock()
        self.generic_visit(node)
    
    def visit_FuncDecl(self,node):
        print('visiting a func decl...')
    
    def visit_BinaryOp(self,node):
        print('visiting a binop...')
        node.show()
        lv = self.visit(node.left)
        rv = self.visit(node.right)
        result = ir.I32()
        self.curBasicBlock.appendOpcode(ir.Binop(op,result,lv,rv))
        return result
        
    def visit_Constant(self,node):
        
        if node.type == 'int':
            var = ir.I32()
            const = ir.ConstantI32(node.value)
            op = ir.LoadConstant(var,const)
            self.curBasicBlock.appendOpcode(op)
            return var
        else:
            raise Exception('unimplemented constant load : %s' % node.coord)
    
    def visit_ID(self,node):
        
        var = self.getScope().lookupName(node.name)
        return var
        
        
    def visit_Return(self,ret):
        print('visiting a return...')
        ret.show()
        self.generic_visit(ret)
    
    def getModule(self):
        return self.module
    
