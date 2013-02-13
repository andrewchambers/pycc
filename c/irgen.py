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
        self.labelTable = {}
        self.gotojumps = set()
        self.symtab = symtab
    
    def patchDanglingBlocks(self,start,next):

        def generator():
            visited = set()
            stack = [start]
            while (len(stack)):
                curblock = stack.pop()
                if curblock in visited:
                    continue
                if curblock is next:
                    continue
                visited.add(curblock)
                yield curblock
                if len(curblock):
                    if curblock[-1] not in self.gotojumps:
                        for b in curblock[-1].getSuccessors():
                            stack.append(b)
        
        for b in generator():
            if len(b) == 0:
                b.append(ir.Jmp(next))
                continue
            
            if b[-1].isTerminator():
                continue
            
            if len(b[-1].getSuccessors()) == 0:
                b.append(ir.Jmp(next))
                continue

    def visit_FileAST(self,node):
        self.module = module.Module()
        self.generic_visit(node)
        
    def visit_FuncDef(self,node):
        self.labelTable = {}
        self.curFunction = function.Function(node.decl.name)
        self.module.addFunction(self.curFunction)
        self.curBasicBlock = basicblock.BasicBlock()
        self.curFunction.setEntryBlock(self.curBasicBlock)
        self.generic_visit(node)
    
    def visit_FuncDecl(self,node):
        pass
    
    
    def visit_Assignment(self,node):
        
        lv = self.visit(node.lvalue)
        rv = self.visit(node.rvalue)
        if rv.lval:
            rv = self.genDeref(rv)
        if lv.lval:
            op = ir.Store(lv,rv)
            self.curBasicBlock.append(op)
            result = self.genDeref(lv)
            return result
        else:
            raise Exception("attemping to assign to a non lvalue!")

    def visit_BinaryOp(self,node):
        
        lv = self.visit(node.left)
        rv = self.visit(node.right)
        
        if rv.lval:
            rv = self.genDeref(rv)

        if lv.lval:
            lv = self.genDeref(lv)
            
        
        result = ir.I32()
        self.curBasicBlock.append(ir.Binop(node.op,result,lv,rv))
        return result
    
    def visit_Decl(self,node):
        if node.init:
            sym = self.symtab.lookupID(node)
            v = ir.I32()
            v.pcount += 1
            v.lval = True
            if type(sym) == symtab.Global:
                op = ir.LoadGlobalAddr(v,sym)
            elif type(sym) == symtab.Param:
                op = ir.LoadParamAddr(v,sym)
            elif type(sym) == symtab.Local:
                op = ir.LoadLocalAddr(v,sym)
            else:
                raise Exception("unknown symbol type")
            self.curBasicBlock.append(op)
            initializer = self.visit(node.init)
            if initializer.lval:
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
    
    def visit_Goto(self,node):
        #XXX bug if redefined label
        if node.name in self.labelTable:
            nextblock = self.labelTable[node.name]
        else:
            nextblock = basicblock.BasicBlock()
            self.labelTable[node.name] = nextblock
        j = ir.Jmp(nextblock)
        self.gotojumps.add(j)
        self.curBasicBlock.append(j)
        
    def visit_Label(self,node):
        
        prevblock = self.curBasicBlock
        
        if node.name in self.labelTable:
            nextblock = self.labelTable[node.name]
        else:
            nextblock = basicblock.BasicBlock()
            self.labelTable[node.name] = nextblock
        
        
        if prevblock.unsafeEnding():
            prevblock.append(ir.Jmp(nextblock))
            
            
        self.curBasicBlock = nextblock
        
        self.generic_visit(node)
        
        
    def visit_If(self,node):
        
        v = self.visit(node.cond)
        if v.lval:
            v = self.genDeref(v)
        
        trueblock = basicblock.BasicBlock()
        falseblock = basicblock.BasicBlock()
        nxt = basicblock.BasicBlock()
        br = ir.Branch(v,trueblock,falseblock)
        
        self.curBasicBlock.append(br)
        self.curBasicBlock = trueblock
        self.visit(node.iftrue)
        
        self.patchDanglingBlocks(trueblock,nxt)
        
        if node.iffalse:
            self.curBasicBlock = falseblock
            self.visit(node.iffalse)
        
        self.patchDanglingBlocks(falseblock,nxt)
        
        self.curBasicBlock = nxt
        
    def visit_For(self,node):
        
        lcmp = basicblock.BasicBlock()
        lcode = basicblock.BasicBlock()
        lend = basicblock.BasicBlock()
        
        if node.init:
            self.visit(node.init)
            
        if self.curBasicBlock.unsafeEnding():
            self.curBasicBlock.append(ir.Jmp(lcmp))
        
        self.curBasicBlock = lcmp
        
        if node.cond:
            v = self.visit(node.cond)
            
            if v.lval:
                v = self.genDeref(v)
            
            br = ir.Branch(v,lcode,lend)
            self.curBasicBlock.append(br)
        else:
            if self.curBasicBlock.unsafeEnding():
                self.curBasicBlock.append(ir.Jmp(lcode))
        
        self.curBasicBlock = lcode
        if node.stmt:
            self.visit(node.stmt)
        if node.next:
            self.visit(node.next)
        if self.curBasicBlock.unsafeEnding():
            self.curBasicBlock.append(ir.Jmp(lcmp))
        
        self.curBasicBlock = lend
        
        
    def visit_ID(self,node):
        
        sym = self.symtab.lookupID(node)
        v = ir.I32()
        v.pcount += 1
        v.lval = True
        if type(sym) == symtab.Global:
            op = ir.LoadGlobalAddr(v,sym)
        elif type(sym) == symtab.Param:
            op = ir.LoadParamAddr(v,sym)
        elif type(sym) == symtab.Local:
            op = ir.LoadLocalAddr(v,sym)
        else:
            raise Exception("unknown symbol type")
        self.curBasicBlock.append(op)
        return v
        
        
    def visit_Return(self,ret):
        val = self.visit(ret.expr)
        if val.lval:
            val = self.genDeref(val)
        retop = ir.Ret(val)
        self.curBasicBlock.append(retop)
    
    def genDeref(self,val):
        newV = ir.I32()
        assert(val.pcount > 0)
        newV.pcount = val.pcount-1
        self.curBasicBlock.append(ir.Deref(newV,val))
        return newV
        
    def getModule(self):
        return self.module
    
