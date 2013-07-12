from pycparser import c_ast

from backend import module
from backend import function
from backend import basicblock
from backend import ir

from valtracker import ValTracker

import types
import cstrings

import operatorgen

class Symbol(object):
    
    def __init__(self,name,t):
        self.name = name
        self.type = t
    def __repr__(self):
        return "%s Symbol: %s"%(self.__class__.__name__,self.name)

class GlobalSym(Symbol):
    def __init__(self,name,t):
        Symbol.__init__(self,name,t)

class ParamSym(Symbol):
    def __init__(self,name,t):
        Symbol.__init__(self,name,t)
        sz = t.getSize()
        if sz % 4:
            sz += 4 -(sz % 4)
        self.slot = function.StackSlot(sz)

class LocalSym(Symbol):
    def __init__(self,name,t):
        Symbol.__init__(self,name,t)
        sz = t.getSize()
        if sz % 4:
            sz += 4 -(sz % 4)
        self.slot = function.StackSlot(sz)


class SymbolTable(object):
    
    def __init__(self):
        self.scopes = []
    
    def isGlobalScope(self):
        assert(len(self.scopes)) > 0
        return len(self.scopes) == 1

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
    
    def assertNonVoid(self,v):
        if type(v.type) == types.Void:
            raise Exception("value void!")

    def visit_FileAST(self,ast):
        
        self.typeTab = types.TypeTable()
        self.symTab = SymbolTable()
        self.symTab.pushScope()
        self.module = module.Module()
        self.gotojumps = set()
        self.labelTable = {}
        self.curBreakTargets = []
        self.curContinueTargets = []
        
        for ext in ast.ext:
            if type(ext) == c_ast.FuncDef:
                self.visit_FuncDef(ext)
            elif type(ext) == c_ast.Decl:
                self.visit_Decl(ext)
            elif type(ext) == c_ast.Typedef:
                self.visit_typeDef(ext)
            else:
                raise Exception("unhandled ast node type  %s" % str(ext))
        
        self.symTab.popScope()
    
    def visit_Cast(self,cast):
        totype = types.parseTypeDecl(self.typeTab,cast.to_type)
        return operatorgen.genCast(self.curBasicBlock,self.inFunctionDispatch(cast.expr),totype)
    
    def visit_typeDef(self,td):
        t = types.parseTypeDecl(self.typeTab,td.type)
        self.typeTab.registerType(td.name,t,isTypedef=True)
        
 
    def visit_DeclList(self,decllist):
        if decllist.decls:
            for decl in decllist.decls:
                self.inFunctionDispatch(decl)
    
    def isGlobalScope(self):
        return self.symTab.isGlobalScope()

    def visit_Decl(self,decl):
        t = types.parseTypeDecl(self.typeTab,decl.type)
        isstaticvar = 'static' in decl.storage
        if self.isGlobalScope() or isstaticvar:
            sym = GlobalSym(decl.name,t)
        else:
            sym = LocalSym(decl.name,t)
        self.symTab.addSymbol(sym)
        if not self.isGlobalScope() and not isstaticvar:
            if decl.init:
                if type(decl.type) == c_ast.ArrayDecl:
                    raise Exception("cannot currently handle Array initializers")
                elif type(decl.type) == c_ast.PtrDecl:
                    raise Exception("cannot currently handle Pointer initializers")
                initializer = self.inFunctionDispatch(decl.init)
                self.assertNonVoid(initializer)
                if not t.strictTypeMatch(initializer.type):
                    initializer = operatorgen.genCast(self.curBasicBlock,initializer,t)
                v = ir.Pointer()
                op = ir.LoadLocalAddr(v,sym)
                self.curBasicBlock.append(op)

                if initializer.lval:
                    initializer = self.genDeref(initializer)
                op = ir.Store(v,initializer.reg)
                self.curBasicBlock.append(op)
    
    def visit_FuncDef(self,funcdef):
        functype = types.parseTypeDecl(self.typeTab,funcdef.decl)
        self.symTab.addSymbol(GlobalSym(funcdef.decl.name,functype))
        self.curFunction = function.Function(funcdef.decl.name)
        self.curFunctionType = functype
        self.module.addFunction(self.curFunction)
        self.curBasicBlock = basicblock.BasicBlock()
        self.curFunction.setEntryBlock(self.curBasicBlock)
        self.symTab.pushScope()
        
        if funcdef.decl.type.args:
            for param in funcdef.decl.type.args.params:
                t = types.parseTypeDecl(self.typeTab,param)
                if type(t) not in [types.Pointer,types.Int,types.Char]:
                    raise Exception("cant handle type %s as a param yet" % t)
                
                sym = ParamSym(param.name,t)
                self.symTab.addSymbol(sym)
                self.curFunction.addArgumentSlot(sym.slot)
        
        self.symTab.pushScope()
        self.inFunctionDispatch(funcdef.body)
        self.symTab.popScope()
        self.symTab.popScope()
        
        if self.curBasicBlock.unsafeEnding():
            retval = ir.I32()
            self.curBasicBlock.append(ir.LoadConstant(retval,ir.ConstantI32(0)))
            self.curBasicBlock.append(ir.Ret(retval))
    
    def inFunctionDispatch(self,node):
        
        if node == None:
            pass
        elif type(node) == c_ast.Compound:
            self.visit_Compound(node)
        elif type(node) == c_ast.Decl:
            self.visit_Decl(node)
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
        elif type(node) == c_ast.Cast:
            return self.visit_Cast(node)
        elif type(node) == c_ast.Label:
            return self.visit_Label(node)
        elif type(node) == c_ast.Goto:
            return self.visit_Goto(node)
        elif type(node) == c_ast.For:
            return self.visit_For(node)
        elif type(node) == c_ast.While:
            return self.visit_While(node)
        elif type(node) == c_ast.Break:
            return self.visit_Break(node)
        elif type(node) == c_ast.Continue:
            return self.visit_Continue(node)
        elif type(node) == c_ast.FuncCall:
            return self.visit_FuncCall(node)
        elif type(node) == c_ast.DeclList:
            return self.visit_DeclList(node)
        elif type(node) == c_ast.StructRef:
            return self.visit_StructRef(node)
        else:
            raise Exception("unhandled ast node type  %s" % str(node))
    
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
        if self.curBasicBlock.unsafeEnding():
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
        
    def visit_FuncCall(self,node):
        funcSym = self.symTab.lookupSymbol(node.name.name)
        funcType = funcSym.type
        finalArgs = []
        if node.args:
            processingVarArgs = False
            for i,arg in enumerate(node.args.exprs):
                finalArg = self.inFunctionDispatch(arg)
                
                self.assertNonVoid(finalArg)
                
                if not processingVarArgs:
                    if type(funcType.args[i]) == types.VarArgType:
                        processingVarArgs = True
                
                if not processingVarArgs:
                    if not finalArg.type.strictTypeMatch(funcType.args[i]):
                        raise Exception("type mismatch in funcall %s %s incompatible with %s" % (funcSym.name,finalArg.type.type,funcType.args[i].type))

                if finalArg.type.isInt:
                    finalArg = operatorgen.promoteToInt(self.curBasicBlock,finalArg)
                
                finalArg = operatorgen.removeLValness(self.curBasicBlock,finalArg);
                
                finalArgs.append(finalArg)
                
                
                
        else:
            if len(funcType.args) != 0:
                raise Exception(("calling function %s with no args when it" \
                        + " requires args") % funcSym.name)

        retType = funcType.rettype.clone()
        retV = ValTracker(False,retType,None)
        retV.createVirtualReg()
        callinst = ir.Call(node.name.name)
        callinst.read = list(map(lambda v : v.reg,finalArgs))
        if retV.reg != None:
            callinst.assigned = [retV.reg]
        else:
            callinst.assigned = []
        self.curBasicBlock.append(callinst)
        return retV
    
    def visit_If(self,node):
        
        v = self.inFunctionDispatch(node.cond)
        self.assertNonVoid(v)
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

    def visit_While(self,node):
        
        cnd = basicblock.BasicBlock()
        nxt = basicblock.BasicBlock()
        body = basicblock.BasicBlock()
        
        self.curBreakTargets.append(nxt)
        self.curContinueTargets.append(cnd)
        
        if self.curBasicBlock.unsafeEnding():
            self.curBasicBlock.append(ir.Jmp(cnd))
        self.curBasicBlock = cnd
        
        v = self.inFunctionDispatch(node.cond)
        self.assertNonVoid(v)
        if v.lval:
            v = self.genDeref(v)
        
        if self.curBasicBlock.unsafeEnding():
            self.curBasicBlock.append(ir.Branch(v.reg,body,nxt))
        
        self.curBasicBlock = body
        
        self.inFunctionDispatch(node.stmt)
        
        if self.curBasicBlock.unsafeEnding():
            self.curBasicBlock.append(ir.Jmp(cnd))
        self.curBreakTargets.pop()
        self.curContinueTargets.pop()
        
        self.curBasicBlock = nxt
        
    
    def visit_Continue(self,node):
        if self.curBasicBlock.unsafeEnding():
            j = ir.Jmp(self.curContinueTargets[-1])
            self.gotojumps.add(j)
            self.curBasicBlock.append(j)
        self.curBasicBlock = basicblock.BasicBlock()
    
    def visit_Break(self,node):
        if self.curBasicBlock.unsafeEnding():
            j = ir.Jmp(self.curBreakTargets[-1])
            self.gotojumps.add(j)
            self.curBasicBlock.append(j)
        self.curBasicBlock = basicblock.BasicBlock()
    
    def visit_For(self,node):
        
        lcmp = basicblock.BasicBlock()
        lcode = basicblock.BasicBlock()
        lend = basicblock.BasicBlock()
        
        self.curBreakTargets.append(lend)
        self.curContinueTargets.append(lend)
        
        if node.init:
            self.inFunctionDispatch(node.init)
            
        if self.curBasicBlock.unsafeEnding():
            self.curBasicBlock.append(ir.Jmp(lcmp))
        
        self.curBasicBlock = lcmp
        
        if node.cond:
            v = self.inFunctionDispatch(node.cond)
            self.assertNonVoid(v)
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
        
        self.curBreakTargets.pop()
        self.curContinueTargets.pop()

    def visit_Compound(self,compound):
        self.symTab.pushScope()
        if compound.block_items != None:
            for block_item in compound.block_items:
                self.inFunctionDispatch(block_item)
        self.symTab.popScope()
    
    def visit_Constant(self,const):
        if const.type == 'int':
            #XXX
            t = types.Int()
            reg = ir.I32()
            const = ir.ConstantI32(const.value)
            op = ir.LoadConstant(reg,const)
            v = ValTracker(False,t,reg)
            self.curBasicBlock.append(op)
            return v
        elif const.type == 'string':
            t = types.Char()
            reg = ir.Pointer()
            v = ValTracker(False,types.Pointer(t),reg)
            rawdata = cstrings.parseCString(const.value)
            label = self.module.addReadOnlyData(rawdata)
            op = ir.LoadGlobalAddr(reg,GlobalSym(label,v.type.clone()))
            self.curBasicBlock.append(op)
            return v
        elif const.type == 'char':
            t = types.Char()
            v = ValTracker(False,t,None)
            v.createVirtualReg()
            const = ir.ConstantI8(cstrings.parseCChar(const.value))
            op = ir.LoadConstant(v.reg,const)
            self.curBasicBlock.append(op)
            return v
 
        else:
            raise Exception('unimplemented constant load : %s' % const.coord)
    
    def visit_Return(self,ret):
        if ret.expr == None:
            if type(self.curFunctionType.rettype) != types.Void:
                raise Exception("returning void in a non void function")
            retop = ir.Ret()
        else:
            val = self.inFunctionDispatch(ret.expr)
            self.assertNonVoid(val)
            if not val.type.strictTypeMatch(self.curFunctionType.rettype):
                val = operatorgen.genCast(self.curBasicBlock,val,self.curFunctionType.rettype)

            if val.lval:
                val = self.genDeref(val)
            retop = ir.Ret(val.reg)
        #print ("ret in %s" % self.curBasicBlock)
        self.curBasicBlock.append(retop)
    
    def visit_StructRef(self,node):
        
        field = node.field.name
        
        val = self.inFunctionDispatch(node.name)
        self.assertNonVoid(val) 
        if node.type == '->':
            if type(val.type) != types.Pointer and type(val.type.type) != types.Struct:
                raise Exception("cannot perform -> on a non struct pointer")
        elif node.type == '.':
            if type(val.type) != types.Struct:
                raise Exception("cannot perform . on a non struct")
        else:
            raise Exception("unreachable!")
        
        
        if node.type == '->':
            t,offset = val.type.type.getMemberInfo(field)
        else: # .
            t,offset = val.type.getMemberInfo(field)
        
        if not t:
            raise Exception("member %s does not exist" % field)
        
        if node.type == '->':
            
            if val.lval:
                val = self.genDeref(val)
        
        if offset == 0:
            return ValTracker(True,t,val.reg)
        
        ret = ValTracker(True,t,ir.Pointer())
        
        constOffset = ir.I32()
        
        self.curBasicBlock.append(ir.LoadConstant(constOffset,ir.ConstantI32(offset)))
        self.curBasicBlock.append(ir.Binop('+',ret.reg,val.reg,constOffset))
        return ret
        
        
        
    def visit_Binop(self,node):
        
        lv = self.inFunctionDispatch(node.left)
        self.assertNonVoid(lv)
        # a short circuit binop requires some branches
        if node.op in ['&&', '||']:
            if lv.lval:
                lv = self.genDeref(lv)
            
            # lets just copy the input type for now,
            # it should probably do a cast or something
            constZero = lv.clone()
            result1 = lv.clone()
            result2 = lv.clone()
            result3 = lv.clone()
            
            compareResult = lv.clone()
            
            self.curBasicBlock.append(ir.LoadConstant(constZero.reg,ir.ConstantI32(0)))
            self.curBasicBlock.append(ir.Binop('!=',compareResult.reg,lv.reg,constZero.reg))
            ifZero = basicblock.BasicBlock()
            ifNotZero = basicblock.BasicBlock()
            next = basicblock.BasicBlock()
            
            self.curBasicBlock.append(ir.Branch(compareResult.reg,ifNotZero,ifZero))
            
            if node.op == '&&':
                shortCircuit = ifZero
                other = ifNotZero
                shortCircuitResult = 0
            else:
                shortCircuit = ifNotZero
                other = ifZero
                shortCircuitResult = 1
            
            
            self.curBasicBlock = shortCircuit
            self.curBasicBlock.append(ir.LoadConstant(result1.reg,ir.ConstantI32(shortCircuitResult)))
            if self.curBasicBlock.unsafeEnding():
                self.curBasicBlock.append(ir.Jmp(next))
            
            self.curBasicBlock = other
            rv = self.inFunctionDispatch(node.right)
            self.assertNonVoid(rv)
            if rv.lval:
                rv = self.genDeref(rv)
            
            #create some new virtual registers
            constZero = lv.clone()
            
            self.curBasicBlock.append(ir.LoadConstant(constZero.reg,ir.ConstantI32(0)))
            self.curBasicBlock.append(ir.Binop('!=',result2.reg,rv.reg,constZero.reg))
            
            result2Reaching = self.curBasicBlock
            
            if self.curBasicBlock.unsafeEnding():
                self.curBasicBlock.append(ir.Jmp(next))
            
            self.curBasicBlock = next
            self.curBasicBlock.append(ir.Phi(result3.reg,[(result2.reg,result2Reaching),(result1.reg,shortCircuit)]))
            
            return result3
            
        else: # a normal binop
            rv = self.inFunctionDispatch(node.right)
            self.assertNonVoid(lv)
            self.assertNonVoid(rv)
            return operatorgen.genBinop(self.curBasicBlock,node.op,lv,rv)
    
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
        self.assertNonVoid(v)
        
        idx = self.inFunctionDispatch(node.subscript)
        self.assertNonVoid(idx)
        if idx.lval:
            idx = self.genDeref(idx)
        
        if type(v.type) == types.Array:
            ret = v.index()
            
            const = ir.I32()
            offset = ir.I32() #XXX
            
            self.curBasicBlock.append(ir.LoadConstant(const,ir.ConstantI32(ret.type.getSize())))
            self.curBasicBlock.append(ir.Binop('*',offset,idx.reg,const))
            self.curBasicBlock.append(ir.Binop('+',ret.reg,v.reg,offset))
            return ret
        elif type(v.type) == types.Pointer:
            if v.lval:
               v = self.genDeref(v)
            ret = v.deref()
            ret.lval = True
            ret.createVirtualReg()
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
        self.assertNonVoid(lv)
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
            lv.type = types.Pointer(lv.type)
            return lv
        
        elif node.op == '*':
            print lv.type
            if lv.lval:
                lv = self.genDeref(lv)
            print lv.type
            lv.type = lv.type.type
            lv.lval = True
            return lv
        elif node.op == '!':
            if lv.lval:
                lv = self.genDeref(lv)
            ret = lv.clone()
            constzero = type(ret.reg)()
            self.curBasicBlock.append(ir.LoadConstant(constzero,ir.ConstantI32(0)))
            self.curBasicBlock.append(ir.Binop('==',ret.reg,lv.reg,constzero))
            return ret
        else:
            raise Exception("bug - unhandle unary op %s" % node.op)

    def visit_Assignment(self,node):
        
        lv = self.inFunctionDispatch(node.lvalue)
        rv = self.inFunctionDispatch(node.rvalue)
        self.assertNonVoid(lv)
        self.assertNonVoid(rv)
        if type(lv.type) == types.Array:
            raise Exception('cannot assign to an array')
        
        if rv.lval:
            rv = self.genDeref(rv)
        
        if not lv.type.strictTypeMatch(rv.type):
            rv = operatorgen.genCast(self.curBasicBlock,rv,lv.type)
        
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


