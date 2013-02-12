from pycparser import c_ast

from backend import module
from backend import function
from backend import basicblock
from backend import ir

import symtab

class IRGenerator(c_ast.NodeVisitor):
    
    def __init__(self,symtab):
        self.module = None
        self.curFunction = None
        self.curBasicBlock = None
        self.symtab = symtab
    
    def visit_FileAST(self,node):
        self.module = module.Module()
        self.generic_visit(node)
        
    def visit_FuncDef(self,node):
        self.curFunction = function.Function(node.decl.name)
        self.module.addFunction(self.curFunction)
        self.curBasicBlock = basicblock.BasicBlock()
        self.curFunction.setEntryBlock(self.curBasicBlock)
        self.generic_visit(node)
    
    def visit_FuncDecl(self,node):
        pass
    
    def visit_BinaryOp(self,node):
        lv = self.visit(node.left)
        rv = self.visit(node.right)
        
        if rv.isLVal():
            rv = self.genDeref(rv)
        
        if node.op == '=':
            if lv.isLVal():
                op = self.Store(lv,rv)
                self.curBasicBlock.append(op)
                result = self.genDeref(lv)
                return result
            else:
                raise Exception("attemping to assign to a non lvalue!")
        else:
            if lv.isLVal():
                lv = self.genDeref(lv)
            
        
        result = ir.I32()
        self.curBasicBlock.append(ir.Binop(node.op,result,lv,rv))
        return result
    
    def visit_Decl(self,node):
        if node.init:
            sym = self.symtab.lookupID(node)
            v = ir.I32()
            v.incPCount()
            v.setLVal()
            if type(sym) == symtab.Global:
                op = ir.LoadGlobal(v,sym)
            elif type(sym) == symtab.Param:
                op = ir.LoadParam(v,sym)
            elif type(sym) == symtab.Local:
                op = ir.LoadLocal(v,sym)
            else:
                raise Exception("unknown symbol type")
            self.curBasicBlock.append(op)
            initializer = self.visit(node.init)
            if initializer.isLVal():
                initializer = self.genDeref(initializer)
            
            op = ir.Store(v,initializer)
            self.curBasicBlock.append(op)
            
    def visit_Constant(self,node):
        
        if node.type == 'int':
            var = ir.I32()
            const = ir.ConstantI32(node.value)
            op = ir.LoadConstant(var,const)
            self.curBasicBlock.append(op)
            return var
        else:
            raise Exception('unimplemented constant load : %s' % node.coord)
    
    def visit_If(self,node):
        
        trueblock = basicblock.BasicBlock()
        
        falseblock = None
        if node.iffalse:
            falseblock = basicblock.BasicBlock()
        nxt = basicblock.BasicBlock()
        
        v = self.visit(node.cond)
        if v.isLVal():
            v = self.genDeref(v)
        
        if node.iffalse:
            br = ir.Branch(v,trueblock,falseblock)
        else:
            br = ir.Branch(v,trueblock,nxt)
        self.curBasicBlock.append(br)
        self.curBasicBlock = trueblock
        self.visit(node.iftrue)
        if not trueblock[-1].isTerminator():
            trueblock.append(ir.Jmp(nxt))

        if node.iffalse:
            self.curBasicBlock = falseblock
            self.visit(node.iffalse)
            if not falseblock[-1].isTerminator():
                trueblock.append(ir.Jmp(nxt))
        
        self.curBasicBlock = nxt
    
    def visit_ID(self,node):
        
        sym = self.symtab.lookupID(node)
        v = ir.I32()
        v.incPCount()
        v.setLVal()
        if type(sym) == symtab.Global:
            op = ir.LoadGlobal(v,sym)
        elif type(sym) == symtab.Param:
            op = ir.LoadParam(v,sym)
        elif type(sym) == symtab.Local:
            op = ir.LoadLocal(v,sym)
        else:
            raise Exception("unknown symbol type")
        self.curBasicBlock.append(op)
        return v
        
        
    def visit_Return(self,ret):
        val = self.visit(ret.expr)
        if val.isLVal():
            val = self.genDeref(val)
        retop = ir.Ret(val)
        self.curBasicBlock.append(retop)
    
    def genDeref(self,val):
        newV = ir.I32()
        assert(val.getPCount() > 0)
        newV.setPCount(val.getPCount()-1)
        self.curBasicBlock.append(ir.Deref(newV,val))
        return newV
        
    
    def getModule(self):
        return self.module
    