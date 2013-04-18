from pycparser import c_ast

from backend import module
from backend import function
from backend import basicblock
from backend import ir

from valtracker import ValTracker

import types


class Symbol(object):
    
    def __init__(self,name,t):
        self.name = name
        self.type = t
    def __repr__(self):
        return "%s Symbol: %s"%(self.__class__.__name__,self.name)

class GlobalSym(Symbol):
    pass

class ParamSym(Symbol):
    pass

class LocalSym(Symbol):
    def __init__(self,name,t):
        Symbol.__init__(self,name,t)
        self.slot = function.StackSlot(t.getSize())


class SymbolTable(object):
    
    def __init__(self):
        self.scopes = []
    
    def pushScope(self):
        self.scopes.append({})
        
    def popScope(self):
        self.scopes.pop()
    
    def addSymbol(self,sym):
        self.scopes[-1][sym.name] = sym
    
    def lookupSymbol(self,name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise Exception("undefined variable %s"%name)

class IRGenerator(c_ast.NodeVisitor):
    
    def getModule(self):
        return self.module
    
    def visit_FileAST(self,ast):
        
        self.typeTab = types.TypeTable()
        self.symTab = SymbolTable()
        self.symTab.pushScope()
        self.module = module.Module()
        self.gotojumps = set()
        self.labelTable = {}
        
        for ext in ast.ext:
            if type(ext) == c_ast.FuncDef:
                self.visit_FuncDef(ext)
            elif type(ext) == c_ast.Decl:
                self.symTab.addSymbol(GlobalSym(ext.name,None))
            else:
                raise Exception("unhandled ast node type  %s" % str(ext))
        
        self.symTab.popScope()
        
    def visit_FuncDef(self,funcdef):
        
        self.symTab.addSymbol(GlobalSym(funcdef.decl.name,None))
        self.curFunction = function.Function(funcdef.decl.name)
        self.module.addFunction(self.curFunction)
        self.curBasicBlock = basicblock.BasicBlock()
        self.curFunction.setEntryBlock(self.curBasicBlock)
        self.symTab.pushScope()
        self.inFunctionDispatch(funcdef.body)
        self.symTab.popScope()
    
    def inFunctionDispatch(self,node):
        
        if node == None:
            pass
        elif type(node) == c_ast.Compound:
            self.visit_Compound(node)
        elif type(node) == c_ast.Decl:
            self.visit_inFunctionDecl(node)
        elif type(node) == c_ast.Return:
            self.visit_Return(node)
        elif type(node) == c_ast.Constant:
            return self.visit_Constant(node)
        elif type(node) == c_ast.BinaryOp:
            return self.visit_Binop(node)
        elif type(node) == c_ast.UnaryOp:
            return self.visit_UnaryOp(node)
        elif type(node) == c_ast.Assignment:
            return self.visit_Assignment(node)
        elif type(node) == c_ast.ArrayRef:
            return self.visit_ArrayRef(node)
        elif type(node) == c_ast.ID:
            return self.visit_ID(node)
        elif type(node) == c_ast.If:
            return self.visit_If(node)
        elif type(node) == c_ast.Label:
            return self.visit_Label(node)
        elif type(node) == c_ast.Goto:
            return self.visit_Goto(node)
        elif type(node) == c_ast.For:
            return self.visit_For(node)
        else:
            raise Exception("unhandled ast node type  %s" % str(node))
    
    def visit_inFunctionDecl(self,decl,depth=0):
        
        if type(decl.type) == c_ast.TypeDecl:
            
            t = self.typeTab.lookupType(decl.type.type.names[0])
            sym = LocalSym(decl.name,t)
            self.symTab.addSymbol(sym)
            self.curFunction.addStackSlot(sym.slot)
            if decl.init:
                initializer = self.inFunctionDispatch(decl.init)
                v = ir.Pointer()
                op = ir.LoadLocalAddr(v,sym)
                self.curBasicBlock.append(op)

                if initializer.lval:
                    initializer = self.genDeref(initializer)
                op = ir.Store(v,initializer.reg)
                self.curBasicBlock.append(op)
            
        elif type(decl.type) == c_ast.ArrayDecl:
            
            sym = LocalSym(decl.name,self._recursivelyCreateType(decl))
            self.symTab.addSymbol(sym)
            self.curFunction.addStackSlot(sym.slot)
            if decl.init != None:
                raise Exception("cannot currently handle Array initializers")
        
        elif type(decl.type) == c_ast.PtrDecl:
            
            sym = LocalSym(decl.name,self._recursivelyCreateType(decl))
            self.symTab.addSymbol(sym)
            self.curFunction.addStackSlot(sym.slot)
            if decl.init != None:
                raise Exception("cannot currently handle Pointer initializers")
            
        else:
            raise Exception("unhandled decl type")
    
    def _recursivelyCreateType(self,decl):
        
        if type(decl.type) == c_ast.ArrayDecl:
            dim = decl.type.dim
            if type(dim) != c_ast.Constant and dim.type != 'int':
                    raise Exception("cannot handle a non integer sized constant array")
            if type(decl.type.type) == c_ast.TypeDecl:
                return types.Array(self.typeTab.lookupType(decl.type.type.type.names[0]),int(dim.value))
            else:
                return types.Array(self._recursivelyCreateType(decl.type),int(dim.value))
        elif type(decl.type) == c_ast.PtrDecl:
            if type(decl.type.type) == c_ast.TypeDecl:
                return types.Pointer(self.typeTab.lookupType(decl.type.type.type.names[0]))
            else:
                return types.Pointer(self._recursivelyCreateType(decl.type))
        else:
            raise Exception("XXXX error creating type")
        
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
        
        self.inFunctionDispatch(node.stmt)
        

    def visit_If(self,node):
        
        v = self.inFunctionDispatch(node.cond)
        if v.lval:
            v = self.genDeref(v)
        
        trueblock = basicblock.BasicBlock()
        falseblock = basicblock.BasicBlock()
        nxt = basicblock.BasicBlock()
        br = ir.Branch(v.reg,trueblock,falseblock)
        
        self.curBasicBlock.append(br)
        self.curBasicBlock = trueblock
        self.inFunctionDispatch(node.iftrue)
        self.patchDanglingBlocks(trueblock,nxt)
        
        if node.iffalse:
            self.curBasicBlock = falseblock
            self.inFunctionDispatch(node.iffalse)
        
        self.patchDanglingBlocks(falseblock,nxt)
        self.curBasicBlock = nxt

    def visit_For(self,node):
        
        lcmp = basicblock.BasicBlock()
        lcode = basicblock.BasicBlock()
        lend = basicblock.BasicBlock()
        
        if node.init:
            self.inFunctionDispatch(node.init)
            
        if self.curBasicBlock.unsafeEnding():
            self.curBasicBlock.append(ir.Jmp(lcmp))
        
        self.curBasicBlock = lcmp
        
        if node.cond:
            v = self.inFunctionDispatch(node.cond)
            
            if v.lval:
                v = self.genDeref(v)
            
            br = ir.Branch(v.reg,lcode,lend)
            self.curBasicBlock.append(br)
        else:
            if self.curBasicBlock.unsafeEnding():
                self.curBasicBlock.append(ir.Jmp(lcode))
        
        self.curBasicBlock = lcode
        if node.stmt:
            self.inFunctionDispatch(node.stmt)
        if node.next:
            self.inFunctionDispatch(node.next)
        if self.curBasicBlock.unsafeEnding():
            self.curBasicBlock.append(ir.Jmp(lcmp))
        
        self.curBasicBlock = lend

    def visit_Compound(self,compound):
        self.symTab.pushScope()
        for block_item in compound.block_items:
            self.inFunctionDispatch(block_item)
        self.symTab.popScope()
    
    def visit_Constant(self,const):
        if const.type == 'int':
            t = self.typeTab.lookupType(const.type)
            reg = ir.I32()
            const = ir.ConstantI32(const.value)
            op = ir.LoadConstant(reg,const)
            v = ValTracker(False,t,reg)
            self.curBasicBlock.append(op)
            return v
        else:
            raise Exception('unimplemented constant load : %s' % node.coord)
    
    def visit_Return(self,ret):
        val = self.inFunctionDispatch(ret.expr)
        if val.lval:
            val = self.genDeref(val)
        retop = ir.Ret(val.reg)
        self.curBasicBlock.append(retop)

    def visit_Binop(self,node):
        
        lv = self.inFunctionDispatch(node.left)
        
        # a short circuit binop requires some branches
        if node.op in ['&&', '||']:
            constZero = ir.I32()
            result1 = ir.I32()
            result2 = ir.I32()
            result3 = ir.I32()
            
            compareResult = ir.I32()
            
            self.curBasicBlock.append(ir.LoadConstant(constZero,ir.ConstantI32(0)))
            self.curBasicBlock.append(ir.Binop('!=',compareResult,lv.reg,constZero))
            ifZero = basicblock.BasicBlock()
            ifNotZero = basicblock.BasicBlock()
            next = basicblock.BasicBlock()
            
            self.curBasicBlock.append(ir.Branch(compareResult,ifNotZero,ifZero))
            
            if node.op == '&&':
                shortCircuit = ifZero
                other = ifNotZero
                shortCircuitResult = 0
            else:
                shortCircuit = ifNotZero
                other = ifZero
                shortCircuitResult = 1
            
            
            self.curBasicBlock = shortCircuit
            self.curBasicBlock.append(ir.LoadConstant(result1,ir.ConstantI32(shortCircuitResult)))
            self.curBasicBlock.append(ir.Jmp(next))
            
            self.curBasicBlock = other
            rv = self.inFunctionDispatch(node.right)
            if lv.lval:
                rv = self.genDeref(rv)
            
            #create some new virtual registers
            constZero = ir.I32()
            
            self.curBasicBlock.append(ir.LoadConstant(constZero,ir.ConstantI32(0)))
            self.curBasicBlock.append(ir.Binop('!=',result2,rv.reg,constZero))
            self.curBasicBlock.append(ir.Jmp(next))
            
            self.curBasicBlock = next
            self.curBasicBlock.append(ir.Phi(result3,result2,result1))
            
            return result3
            
        else: # a normal binop
            rv = self.visit(node.right)
            
            if rv.lval:
                rv = self.genDeref(rv)
            
            if lv.lval:
                lv = self.genDeref(lv)
            
            
            ret = ValTracker(False,types.Int(),None)
            ret.createVirtualReg()
            self.curBasicBlock.append(ir.Binop(node.op,ret.reg,lv.reg,rv.reg))
            return ret
    
    def visit_ID(self,node):
        
        sym = self.symTab.lookupSymbol(node.name)
        
        reg = ir.Pointer()
        v = ValTracker(True,sym.type,reg)
        
        if type(sym) == GlobalSym:
            op = ir.LoadGlobalAddr(reg,sym)
        elif type(sym) == ParamSym:
            op = ir.LoadParamAddr(reg,sym)
        elif type(sym) == LocalSym:
            op = ir.LoadLocalAddr(reg,sym)
        else:
            raise Exception("unknown symbol type")
        self.curBasicBlock.append(op)
        
        return v
    
    def visit_ArrayRef(self,node):
        v = self.inFunctionDispatch(node.name)
        if type(v.type) == types.Array:
            
            idx = self.inFunctionDispatch(node.subscript)
            if idx.lval:
                idx = self.genDeref(idx)
            
            ret = v.index()
            
            const = ir.I32()
            offset = ir.I32() #XXX
            
            self.curBasicBlock.append(ir.LoadConstant(const,ir.ConstantI32(ret.type.getSize())))
            self.curBasicBlock.append(ir.Binop('*',offset,idx.reg,const))
            self.curBasicBlock.append(ir.Binop('+',ret.reg,v.reg,offset))
            return ret
            
        else:
            raise Exception("cannot perform an array index on %s %s" % (node,v.type))
    
    def genDeref(self,val):
        newV = val.deref()
        self.curBasicBlock.append(ir.Deref(newV.reg,val.reg))
        return newV
        
        
    def visit_UnaryOp(self,node):
        
        lv = self.inFunctionDispatch(node.expr)
        
        if node.op in ['++','--']:
            if not lv.lval:
                raise Exception("cant perform pre(%s) on a non lval" % node.op)
            
            val = self.genDeref(lv)
            constval = lv.type.createVirtualReg()
            result = lv.clone()
            result.lval = False
            result.createVirtualReg()
            self.curBasicBlock.append(ir.LoadConstant(constval,ir.ConstantI32(1)))
            self.curBasicBlock.append(ir.Binop(node.op[1],result.reg,val.reg,constval))
            self.curBasicBlock.append(ir.Store(lv.reg,result.reg))
            return result
        elif node.op in ['p++','p--']:
            
            if not lv.lval:
                raise Exception("cant perform post(%s) on a non lval" % node.op[1:])
            val = self.genDeref(lv)
            constval = lv.type.createVirtualReg()
            result = lv.clone()
            result.lval = False
            result.createVirtualReg()
            self.curBasicBlock.append(ir.LoadConstant(constval,ir.ConstantI32(1)))
            self.curBasicBlock.append(ir.Binop(node.op[1],result.reg,val.reg,constval))
            self.curBasicBlock.append(ir.Store(lv.reg,result.reg))
            return val
        
        elif node.op == '&':
            
            if not lv.lval:
                raise Exception("cannot get the address of a non lval")
            
            lv.lval = False
            return lv
        
        elif node.op == '*':
            if lv.lval:
                lv = self.genDeref(lv)
            lv.lval = True
            return lv
        else:
            raise Exception("bug - unhandle unary op %s" % node.op)

    def visit_Assignment(self,node):
        
        lv = self.inFunctionDispatch(node.lvalue)
        rv = self.inFunctionDispatch(node.rvalue)
        
        if type(lv.type) == types.Array:
            raise Exception('cannot assign to an array')
        
        if rv.lval:
            rv = self.genDeref(rv)
        
        if not lv.lval:
            raise Exception("attemping to assign to a non lvalue!")
        
        if node.op in ['+=','-=' ,'/=','^=','|=','&=','*=','%=']:
            val = lv.deref()
            result = lv.clone()
            result.lval = False
            result.createVirtualReg()
            self.curBasicBlock.append(ir.Deref(val.reg,lv.reg))
            self.curBasicBlock.append(ir.Binop(node.op[0],result.reg,val.reg,rv.reg))
        else:
            if node.op != '=' :
                raise Exception("Bug - unknown assignment op %s" % node.op)
            result = rv
                
        self.curBasicBlock.append(ir.Store(lv.reg,result.reg))
        return result

#class Symbol(object):
#    
#    def __init__(self,name,t):
#        self.name = name
#        self.type = t
#    def __repr__(self):
#        return "%s Symbol: %s"%(self.__class__.__name__,self.name)

#class Global(Symbol):
#    pass

#class Param(Symbol):
#    pass

#class Local(Symbol):
#    def __init__(self,name,t):
#        Symbol.__init__(self,name,t)
#        self.slot = function.StackSlot(t.getSize())


#GLOBAL = 0
#PARAM = 1
#LOCAL = 2

#declclasses = [Global,Param,Local]


#class IRGenerator(c_ast.NodeVisitor):
#    
#    def __init__(self):
#        self.module = None
#        self.curFunction = None
#        self.curBasicBlock = None
#        self.labelTable = {}
#        self.gotojumps = set()
#        self._symbols = {}
#        self._scopes = []
#        self._scopeState = GLOBAL
#        self._typeTable = types.TypeTable()
#    
#    def _pushScope(self):
#        self._scopes.append({})
#        
#    def _popScope(self):
#        self._scopes.pop()
#    
#    def _addSymbol(self,sym):
#        self._scopes[-1][sym.name] = sym
#    
#    def _lookupSymbol(self,name):
#        for scope in reversed(self._scopes):
#            if name in scope:
#                return scope[name]
#        raise Exception("undefined variable %s"%name)
#    
#    
#    def visit_ParamList(self,node):
#        self._scopeState = PARAM
#        self.generic_visit(node)
#        
#    def visit_Compound(self,compound):
#        self._scopeState = LOCAL
#        self._pushScope()
#        self.generic_visit(compound)
#        self._popScope()
#    
#    def patchDanglingBlocks(self,start,next):

#        def generator():
#            visited = set()
#            stack = [start]
#            while (len(stack)):
#                curblock = stack.pop()
#                if curblock in visited:
#                    continue
#                if curblock is next:
#                    continue
#                visited.add(curblock)
#                yield curblock
#                if len(curblock):
#                    if curblock[-1] not in self.gotojumps:
#                        for b in curblock[-1].getSuccessors():
#                            stack.append(b)
#        
#        for b in generator():
#            if len(b) == 0:
#                b.append(ir.Jmp(next))
#                continue
#            
#            if b[-1].isTerminator():
#                continue
#            
#            if len(b[-1].getSuccessors()) == 0:
#                b.append(ir.Jmp(next))
#                continue

#    def visit_FileAST(self,node):
#        self.module = module.Module()
#        self._scopeState = GLOBAL
#        self._pushScope()
#        self.generic_visit(node)
#        self._popScope()
#        self.generic_visit(node)
#        assert(len(self._scopes) == 0)
#        
#    def visit_FuncDef(self,node):
#        self.labelTable = {}
#        self.curFunction = function.Function(node.decl.name)
#        self.module.addFunction(self.curFunction)
#        self.curBasicBlock = basicblock.BasicBlock()
#        self.curFunction.setEntryBlock(self.curBasicBlock)
#        self._pushScope()
#        self.generic_visit(node)
#        self._popScope()
#        self._scopeState = GLOBAL
#    
#    def visit_FuncCall(self,node):
#        raise Exception("unimplemented")
#        op = ir.Call()
#        
#        for arg in node.args.exprs:
#            argvar = self.visit(arg)
#            op.read.append(argvar)
#        
#        ret = ir.I32()
#        op.assigned.append(ret)
#        self.curBasicBlock.append(op)
#        return ret
#        
#    
#    
#    def visit_Assignment(self,node):
#        
#        lv = self.visit(node.lvalue)
#        rv = self.visit(node.rvalue)
#        
#        if rv.lval:
#            rv = self.genDeref(rv)
#        
#        if not lv.lval:
#            raise Exception("attemping to assign to a non lvalue!")
#        
#        if node.op in ['+=','-=' ,'/=','^=','|=','&=','*=','%=']:
#            val = ir.I32()
#            result = ir.I32()
#            self.curBasicBlock.append(ir.Deref(val,lv))
#            self.curBasicBlock.append(ir.Binop(node.op[0],result,val,rv))
#        else:
#            if node.op != '=' :
#                raise Exception("Bug - unknown assignment op %s" % node.op)
#            result = rv
#                
#        self.curBasicBlock.append(ir.Store(lv,result))
#        return result

#    def visit_UnaryOp(self,node):
#        
#        lv = self.visit(node.expr)
#        
#        if node.op in ['++','--']:
#            if not lv.lval:
#                raise Exception("cant perform pre(%s) on a non lval" % node.op)
#            val = ir.I32()
#            constval = ir.I32()
#            result = ir.I32()
#            self.curBasicBlock.append(ir.Deref(val,lv))
#            self.curBasicBlock.append(ir.LoadConstant(constval,ir.ConstantI32(1)))
#            self.curBasicBlock.append(ir.Binop(node.op[0],result,val,constval))
#            self.curBasicBlock.append(ir.Store(lv,result))
#            return result
#        elif node.op in ['p++','p--']:
#            
#            if not lv.lval:
#                raise Exception("cant perform post(%s) on a non lval" % node.op[1:])
#            val = ir.I32()
#            constval = ir.I32()
#            result = ir.I32()
#            self.curBasicBlock.append(ir.Deref(val,lv))
#            self.curBasicBlock.append(ir.LoadConstant(constval,ir.ConstantI32(1)))
#            self.curBasicBlock.append(ir.Binop(node.op[1],result,val,constval))
#            self.curBasicBlock.append(ir.Store(lv,result))
#            return val
#        
#        elif node.op == '&':
#            
#            if not lv.lval:
#                raise Exception("cannot get the address of a non lval")
#            
#            lv.lval = False
#            return lv
#        
#        elif node.op == '*':
#            lv.lval = True
#            return lv
#        else:
#            raise Exception("bug - unhandle unary op %s" % node.op)
#                
#        

#    def visit_BinaryOp(self,node):
#        
#        lv = self.visit(node.left)
#        if lv.lval:
#            lv = self.genDeref(lv)
#        
#        # a short circuit binop requires some branches
#        if node.op in ['&&', '||']:
#            constZero = ir.I32()
#            result1 = ir.I32()
#            result2 = ir.I32()
#            result3 = ir.I32()
#            
#            compareResult = ir.I32()
#            
#            self.curBasicBlock.append(ir.LoadConstant(constZero,ir.ConstantI32(0)))
#            self.curBasicBlock.append(ir.Binop('!=',compareResult,lv,constZero))
#            ifZero = basicblock.BasicBlock()
#            ifNotZero = basicblock.BasicBlock()
#            next = basicblock.BasicBlock()
#            
#            self.curBasicBlock.append(ir.Branch(compareResult,ifNotZero,ifZero))
#            
#            if node.op == '&&':
#                shortCircuit = ifZero
#                other = ifNotZero
#                shortCircuitResult = 0
#            else:
#                shortCircuit = ifNotZero
#                other = ifZero
#                shortCircuitResult = 1
#            
#            
#            self.curBasicBlock = shortCircuit
#            self.curBasicBlock.append(ir.LoadConstant(result1,ir.ConstantI32(shortCircuitResult)))
#            self.curBasicBlock.append(ir.Jmp(next))
#            
#            self.curBasicBlock = other
#            rv = self.visit(node.right)
#            if lv.lval:
#                rv = self.genDeref(rv)
#            
#            #create some new virtual registers
#            constZero = ir.I32()
#            
#            self.curBasicBlock.append(ir.LoadConstant(constZero,ir.ConstantI32(0)))
#            self.curBasicBlock.append(ir.Binop('!=',result2,rv,constZero))
#            self.curBasicBlock.append(ir.Jmp(next))
#            
#            self.curBasicBlock = next
#            self.curBasicBlock.append(ir.Phi(result3,result2,result1))
#            
#            return result3
#            
#        else: # a normal binop
#            rv = self.visit(node.right)
#            
#            if rv.lval:
#                rv = self.genDeref(rv)
#            
#            if lv.lval:
#                lv = self.genDeref(lv)
#            
#            result = ir.I32()
#            self.curBasicBlock.append(ir.Binop(node.op,result,lv,rv))
#            return result
#    
#    
#    def visit_Decl(self,node):
#    
#        declClass = declclasses[self._scopeState]
#        #raise Exception(str(node.type) + str(dir(node)) + str(dir(node.type)))
#        t = self._typeTable.lookupType(node.type.type)
#        t = 'int'
#        sym = declClass(node.name,t)
#        self._addSymbol(sym)
#        
#    
#        #if node.init:
#        #    sym = self.symtab.lookupID(node)
#        #    v = ir.I32()
#        #    v.pcount += 1
#        #    v.lval = True
#        #    if type(sym) == symtab.Global:
#        #        op = ir.LoadGlobalAddr(v,sym)
#        #    elif type(sym) == symtab.Param:
#        #        op = ir.LoadParamAddr(v,sym)
#        #    elif type(sym) == symtab.Local:
#        #        self.curFunction.addStackSlot(sym.slot)
#        #        op = ir.LoadLocalAddr(v,sym)
#        #    else:
#        #        raise Exception("unknown symbol type")
#        #    self.curBasicBlock.append(op)
#        #    initializer = self.visit(node.init)
#        #    if initializer.lval:
#        #        initializer = self.genDeref(initializer)
#        #    
#        #    op = ir.Store(v,initializer)
#        #    self.curBasicBlock.append(op)
#        
#        self.generic_visit(node)
#            
#    def visit_Constant(self,node):
#        
#        if node.type == 'int':
#            reg = ir.I32()
#            
#            const = ir.ConstantI32(node.value)
#            op = ir.LoadConstant(reg,const)
#            self.curBasicBlock.append(op)
#            return reg
#        else:
#            raise Exception('unimplemented constant load : %s' % node.coord)
#    
#    def visit_Goto(self,node):
#        #XXX bug if redefined label
#        if node.name in self.labelTable:
#            nextblock = self.labelTable[node.name]
#        else:
#            nextblock = basicblock.BasicBlock()
#            self.labelTable[node.name] = nextblock
#        j = ir.Jmp(nextblock)
#        self.gotojumps.add(j)
#        self.curBasicBlock.append(j)
#        
#    def visit_Label(self,node):
#        
#        prevblock = self.curBasicBlock
#        
#        if node.name in self.labelTable:
#            nextblock = self.labelTable[node.name]
#        else:
#            nextblock = basicblock.BasicBlock()
#            self.labelTable[node.name] = nextblock
#        
#        
#        if prevblock.unsafeEnding():
#            prevblock.append(ir.Jmp(nextblock))
#            
#            
#        self.curBasicBlock = nextblock
#        
#        self.generic_visit(node)
#        
#        
#    def visit_If(self,node):
#        
#        v = self.visit(node.cond)
#        if v.lval:
#            v = self.genDeref(v)
#        
#        trueblock = basicblock.BasicBlock()
#        falseblock = basicblock.BasicBlock()
#        nxt = basicblock.BasicBlock()
#        br = ir.Branch(v,trueblock,falseblock)
#        
#        self.curBasicBlock.append(br)
#        self.curBasicBlock = trueblock
#        self.visit(node.iftrue)
#        
#        self.patchDanglingBlocks(trueblock,nxt)
#        
#        if node.iffalse:
#            self.curBasicBlock = falseblock
#            self.visit(node.iffalse)
#        
#        self.patchDanglingBlocks(falseblock,nxt)
#        
#        self.curBasicBlock = nxt
#        
#    def visit_For(self,node):
#        
#        lcmp = basicblock.BasicBlock()
#        lcode = basicblock.BasicBlock()
#        lend = basicblock.BasicBlock()
#        
#        if node.init:
#            self.visit(node.init)
#            
#        if self.curBasicBlock.unsafeEnding():
#            self.curBasicBlock.append(ir.Jmp(lcmp))
#        
#        self.curBasicBlock = lcmp
#        
#        if node.cond:
#            v = self.visit(node.cond)
#            
#            if v.lval:
#                v = self.genDeref(v)
#            
#            br = ir.Branch(v,lcode,lend)
#            self.curBasicBlock.append(br)
#        else:
#            if self.curBasicBlock.unsafeEnding():
#                self.curBasicBlock.append(ir.Jmp(lcode))
#        
#        self.curBasicBlock = lcode
#        if node.stmt:
#            self.visit(node.stmt)
#        if node.next:
#            self.visit(node.next)
#        if self.curBasicBlock.unsafeEnding():
#            self.curBasicBlock.append(ir.Jmp(lcmp))
#        
#        self.curBasicBlock = lend
#        
#        
#    def visit_ID(self,node):
#        
#        sym = self._lookupSymbol(node.name)
#        v = ir.I32()
#        v.pcount += 1
#        v.lval = True
#        if type(sym) == symtab.Global:
#            op = ir.LoadGlobalAddr(v,sym)
#        elif type(sym) == symtab.Param:
#            op = ir.LoadParamAddr(v,sym)
#        elif type(sym) == symtab.Local:
#            self.curFunction.addStackSlot(sym.slot)
#            op = ir.LoadLocalAddr(v,sym)
#        else:
#            raise Exception("unknown symbol type")
#        self.curBasicBlock.append(op)
#        return v
#        
#        
#    def visit_Return(self,ret):
#        val = self.visit(ret.expr)
#        if val.lval:
#            val = self.genDeref(val)
#        retop = ir.Ret(val)
#        self.curBasicBlock.append(retop)
#    
#    def genDeref(self,val):
#        newV = ir.I32()
#        assert(val.pcount > 0)
#        newV.pcount = val.pcount-1
#        self.curBasicBlock.append(ir.Deref(newV,val))
#        return newV
#        
#    def getModule(self):
#        return self.module
#    
