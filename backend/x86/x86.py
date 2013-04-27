from backend import  ir

from backend import standardmachine
from backend import machineinstruction

from backend.instructionselector import *
from backend.selectiondag import *


class X86BasicBinopI32(machineinstruction.MI):
    
    @classmethod
    def match(cls,dag,node):
        
        if type(node.instr) != ir.Binop or node.instr.op != cls.op:
            return None
        
        if len(node.ins) != 2:
            return None
        
        if type(node.instr.read[0]) not in (ir.I32,ir.Pointer):
            return None
        
        if type(node.instr.read[1]) not in (ir.I32,ir.Pointer):
            return None
        
        if type(node.instr.assigned[0]) not in (ir.I32,ir.Pointer):
            return None
        
        if node.instr.assigned[0] != node.instr.read[0]:
            return None
        
        def repl():
            m = cls()
            m.assigned = node.instr.assigned
            m.read = node.instr.read
            node.instr = m
        
        return InstructionMatch(repl,1)

class X86BasicUnopI32(machineinstruction.MI):
    
    @classmethod
    def match(cls,dag,node):
        
        if type(node.instr) != ir.Unop or node.instr.op != cls.op:
            return None
        
        if len(node.ins) != 1:
            return None
        
        if type(node.instr.read[0]) not in (ir.I32,ir.Pointer):
            return None
        
        if type(node.instr.assigned[0]) not in (ir.I32,ir.Pointer):
            return None
        
        
        def repl():
            m = cls()
            m.assigned = node.instr.assigned
            m.read = node.instr.read
            node.instr = m
        
        return InstructionMatch(repl,1)

class X86NotI32(X86BasicUnopI32):
    op = '!'
    
    def asm(self):
        if self.read[0] == self.assigned[0]:
            ret =  "subl $1,%{0}; adcl %{0},%{0}; andl $1,%{0}"
            return ret.format(self.assigned[0])
        else:
            o = self.assigned[0]
            ret = "movl %{1},%{0}; " + \
                  "addl $-1,%{1}; " + \
                  "sbbl %{1},%{0};"
            return ret.format(self.assigned[0],self.read[0])
             
        

class X86IMultI32(X86BasicBinopI32):
    op = '*'
    
    def asm(self):
        return "imul %%%s"%(self.read[1])

class X86IDivI32(X86BasicBinopI32):
    
    op = '/'
    
    def asm(self):
        return "cdq; idiv %%%s"%(self.read[1])

class X86IModI32(X86BasicBinopI32):
    op = '%'
    def asm(self):
        return "cdq; idiv %%%s"%(self.read[1])


class X86SubI32(X86BasicBinopI32):
    op = '-'
    def asm(self):
        return "sub %%%s,%%%s"%(self.read[1],self.assigned[0])

class X86SHLI32(X86BasicBinopI32):
    op = '<<'
    def asm(self):
        return "shl %%cl,%%%s"%(self.assigned[0])

class X86SHRI32(X86BasicBinopI32):
    op = '>>'
    def asm(self):
        return "shr %%cl,%%%s"%(self.assigned[0])

class X86AddI32(X86BasicBinopI32):
    op = '+'
    def asm(self):
        return "add %%%s,%%%s"%(self.read[1],self.assigned[0])

class X86XorI32(X86BasicBinopI32):
    op = '^'
    def asm(self):
        return "xor %%%s,%%%s"%(self.read[1],self.assigned[0])
        
class X86OrI32(X86BasicBinopI32):
    op = '|'
    def asm(self):
        return "or %%%s,%%%s"%(self.read[1],self.assigned[0])

class X86AndI32(X86BasicBinopI32):
    op = '&'
    def asm(self):
        return "and %%%s,%%%s"%(self.read[1],self.assigned[0])

class X86EqI32(X86BasicBinopI32):
    op = '=='
    
    def asm(self):
        
        if self.read[1] == self.assigned[0]:
            return "movl $1, %%%s" % self.read[1]
            
        args = {'r' : self.read[1] ,'w' : self.assigned[0]}
        ret =  \
        "xorl %%%(r)s, %%%(w)s; " + \
        "shrl $1,%%%(w)s; " + \
        "adcl $-1,%%%(w)s; " + \
        "shrl $31,%%%(w)s;"
        
        return ret % args

class X86NeI32(X86BasicBinopI32):
    op = '!='
    
    def asm(self):
        
        if self.read[1] == self.assigned[0]:
            return "movl $0, %%%s" % self.read[1]
        
        args = {'r' : self.read[1] ,'w' : self.assigned[0]}
        ret =  \
        "subl %%%(r)s,%%%(w)s; " + \
        "adcl $-1,%%%(w)s; " + \
        "adcl %%%(w)s,%%%(w)s; " + \
        "andl $1,%%%(w)s"
        
        return ret % args

class X86GtI32(X86BasicBinopI32):
    op = '>'
    def asm(self):
        
        if self.read[1] == self.assigned[0]:
            return "movl $0, %%%s" % self.read[1]
        
        args = {'r' : self.read[1] ,'w' : self.assigned[0]}
        
        
        ret =  \
        "pushl %%%(r)s; " + \
        "xorl %%%(w)s,%%%(r)s; " + \
        "andl %%%(r)s,%%%(w)s; " + \
        "sarl $1,%%%(r)s; " + \
        "sbbl %%%(r)s,%%%(w)s; " + \
        "shrl $31,%%%(w)s; " + \
        "xorl $1,%%%(w)s; " + \
        "popl %%%(r)s"
        
        return ret % args
    
class X86LtI32(X86BasicBinopI32):
    op = '<'
    def asm(self):
        
        if self.read[1] == self.assigned[0]:
            return "movl $0, %%%s" % self.read[1]
        
        args = {'r' : self.read[1] ,'w' : self.assigned[0]}
        
        ret =  \
        "pushl %%%(r)s; " + \
        "xorl %%%(w)s,%%%(r)s; " + \
        "andl %%%(r)s,%%%(w)s; " + \
        "sarl $1,%%%(r)s; " + \
        "sbbl %%%(r)s,%%%(w)s; " + \
        "shrl $31,%%%(w)s; " + \
        "popl %%%(r)s"
        
        return ret % args
    

class X86LoadConstantI32(machineinstruction.MI):
    
    def __init__(self,const):
        machineinstruction.MI.__init__(self)
        self.const = const
    
    @classmethod
    def match(cls,dag,node):
        
        if type(node.instr) != ir.LoadConstant:
            return None
        
        if len(node.ins) != 0:
            return None
        
        if type(node.instr.assigned[0]) != ir.I32:
            return None
        
        def repl():
            ld = X86LoadConstantI32(node.instr.const)
            ld.assigned = node.instr.assigned
            ld.read = node.instr.read
            node.instr = ld
        
        return InstructionMatch(repl,1)

    def asm(self):
        return "mov $%d,%%%s"%(self.const.value,self.assigned[0])

class X86MovI32(machineinstruction.MI):
    
    def isMove(self):
        return True
    
    @classmethod
    def match(cls,dag,node):
        
        if type(node.instr) != ir.Move:
            return None
        
        if len(node.ins) != 1:
            return None
            
        if type(node.instr.read[0]) not in (ir.I32,ir.Pointer):
            return None
        
        if type(node.instr.assigned[0]) not in (ir.I32,ir.Pointer):
            return None
        
        
        def repl():
            mov = X86MovI32()
            mov.assigned = node.instr.assigned
            mov.read = node.instr.read
            node.instr = mov
        
        return InstructionMatch(repl,1)

    def asm(self):
        return "mov %%%s,%%%s"%(self.read[0],self.assigned[0])

class X86LoadLocalAddr(machineinstruction.MI):
    
    @classmethod
    def match(cls,dag,node):
        
        if type(node.instr) != ir.LoadLocalAddr:
            return None
        
        
        def repl():
            lla = X86LoadLocalAddr()
            lla.assigned = node.instr.assigned
            lla.sym = node.instr.sym
            node.instr = lla
            
        
        return InstructionMatch(repl,1)

    def asm(self):
        r = self.assigned[0]
        offset = self.sym.slot.offset
        if offset == None:
            offsetStr = "XXX"
        else:
            offsetStr = str( (offset) ) 
        return "mov %%ebp, %%%s; sub $%s, %%%s"%(r,offsetStr,r)


class X86LoadGlobalAddr(machineinstruction.MI):
    
    @classmethod
    def match(cls,dag,node):
        
        if type(node.instr) != ir.LoadGlobalAddr:
            return None
        
        
        def repl():
            lla = X86LoadGlobalAddr()
            lla.assigned = node.instr.assigned
            lla.sym = node.instr.sym
            node.instr = lla
            
        
        return InstructionMatch(repl,1)

    def asm(self):
        r = self.assigned[0]
        return "leal %s, %%%s"%(self.sym.name,r)


class X86LoadParamAddr(machineinstruction.MI):
    
    
    @classmethod
    def match(cls,dag,node):
        
        if type(node.instr) != ir.LoadParamAddr:
            return None
        
        
        def repl():
            lla = X86LoadParamAddr()
            lla.assigned = node.instr.assigned
            lla.sym = node.instr.sym
            node.instr = lla
            
        
        return InstructionMatch(repl,1)

    def asm(self):
        r = self.assigned[0]
        offset = self.sym.slot.offset
        if offset == None:
            offsetStr = "XXX"
        else:
            offsetStr = str( ( 8 + offset) ) 
        return "mov %%ebp, %%%s; add $%s, %%%s"%(r,offsetStr,r)



class X86LoadI32(machineinstruction.MI):
    
    @classmethod
    def match(cls,dag,node):
        
        if type(node.instr) != ir.Deref:
            return None
        
        if len(node.ins) != 1:
            return None
        
        if type(node.instr.assigned[0]) not in (ir.I32,ir.Pointer):
            return None
        
        def repl():
            ld = X86LoadI32()
            ld.read = node.instr.read
            ld.assigned = node.instr.assigned
            node.instr = ld
            
        return InstructionMatch(repl,1)

    def asm(self):
        return "movl (%%%s),%%%s"%(self.read[0],self.assigned[0])

class X86StoreI32(machineinstruction.MI):
    
    @classmethod
    def match(cls,dag,node):
        
        if type(node.instr) != ir.Store:
            return None
        
        if len(node.ins) != 2:
            return None
        
        if type(node.instr.read[0]) != ir.Pointer:
            return None
        
        if type(node.instr.read[1]) not in (ir.I32,ir.Pointer):
            return None
        
        
        def repl():
            st = X86StoreI32()
            st.read = node.instr.read
            st.assigned = node.instr.assigned
            node.instr = st
            
        return InstructionMatch(repl,1)

    def asm(self):
        return "movl %%%s, (%%%s)"%(self.read[1],self.read[0])

class X86PushI32(machineinstruction.MI):
    
    def asm(self):
        return "push %%%s"%(self.read[0])


        
class X86Jmp(machineinstruction.MI):
    
    def asm(self):
        return "jmp .%s"%(self.getSuccessors()[0].name)


class X86Branch(machineinstruction.MI):
    
    def asm(self):
        
        if self.successors[0] != None and self.successors[1] == None:
            return "test %%%s,%%%s; jnz .%s"%(self.read[0],self.read[0],self.successors[0])
        elif self.successors[0] == None and self.successors[1] != None:
            return "test %%%s,%%%s; jz .%s"%(self.read[0],self.read[0],self.successors[1])
        else:
            return "test %%%s,%%%s; jnz .%s; jmp .%s"%(self.read[0],self.read[0],self.successors[0],self.successors[1])

class X86Nop(machineinstruction.MI):
    def asm(self):
        return "nop"

class X86Ret(machineinstruction.MI):
    def asm(self):
        return "ret"

class X86Call(machineinstruction.MI):
    def __init__(self,label):
        machineinstruction.MI.__init__(self)
        self.label = label
    
    def isCall(self):
        return True
    
    def asm(self):
        return "call %s" % self.label

class X86Enter(machineinstruction.MI):
    def __init__(self,stackSize):
        machineinstruction.MI.__init__(self)
        self.stackSize = stackSize
    def asm(self):
        ret = "pushl %ebp; movl %esp,%ebp;"
        if self.stackSize:
              ret += "subl $%s,%%esp;" % self.stackSize
        return ret

class X86Leave(machineinstruction.MI):
    def __init__(self, stackSize):
        machineinstruction.MI.__init__(self)
        self.stackSize = stackSize
    def asm(self):
        if self.stackSize:
            ret = "addl $%s,%%esp;"% self.stackSize
        else:
            ret = ""
        ret += "popl %ebp;" 
        return ret

class X86StackFree(machineinstruction.MI):
    def __init__(self, amount):
        machineinstruction.MI.__init__(self)
        self.amount = amount
    def asm(self):
        return "add $%d,%%esp"%self.amount

class X86StackLoadI32(machineinstruction.MI):
    def __init__(self,reg,slot):
        machineinstruction.MI.__init__(self)
        self.slot = slot
        self.assigned = [reg]

    def asm(self):
        return "mov -%d(%%ebp), %%%s "%(self.slot.offset,self.assigned[0])
        


class X86StackSaveI32(machineinstruction.MI):
    def __init__(self,reg, slot):
        machineinstruction.MI.__init__(self)
        self.slot = slot
        self.read = [reg]
    
    def asm(self):
        return "mov %%%s,-%d(%%ebp)"%(self.read[0],self.slot.offset)


matchableInstructions = [
    X86AddI32,
    X86SubI32,
    X86SHLI32,
    X86SHRI32,
    X86IMultI32,
    X86IDivI32,
    X86IModI32,
    X86AndI32,
    X86XorI32,
    X86OrI32,
    X86MovI32,
    X86LoadI32,
    X86LoadConstantI32,
    X86LoadParamAddr,
    X86LoadLocalAddr,
    X86LoadGlobalAddr,
    #X86StoreLocalI32,
    X86StoreI32,
    X86EqI32,
    X86NeI32,
    X86GtI32,
    X86LtI32,
    X86NotI32,
#   X86PushI32,
]


registers = [
    standardmachine.Register('eax',[ir.I32,ir.Pointer]),
    standardmachine.Register('ebx',[ir.I32,ir.Pointer]),
    standardmachine.Register('ecx',[ir.I32,ir.Pointer]),
    standardmachine.Register('edx',[ir.I32,ir.Pointer]),
    standardmachine.Register('edi',[ir.I32,ir.Pointer]),
    standardmachine.Register('esi',[ir.I32,ir.Pointer]),
    
]

def getRegisterByName(n):
    for r in registers:
        if r.name == n:
            return r
    raise Exception("bad register %s"%n)

class X86(standardmachine.StandardMachine):
    
    def dagFixups(self,dag):
        print("x86 dag fixups")
        newnodes = []
        for n in dag.nodes:
            binops = [
              '==' , '>' , '<' , '<=' , '>=' , '!=', 
              '+','*','-','<<','>>','/', '%', '|' , '&' , '^' ,
            ]
            if type(n.instr) == ir.Binop and (n.instr.op in binops ):
                print("fixing up binop in DAG")
                #add a,b,c
                # -------
                #copy a,b
                #add a,a,c
                copy = SDNode()
                copy.instr = ir.Move(None,None)
                
                a = n.outs[0].var
                b = n.ins[0].var
                
                oldedge = n.ins[0].edge
                port = oldedge.tail
                oldedge.remove()
                e1 = SDDataEdge(n.ins[0],copy.outs[0])
                e2 = SDDataEdge(copy.ins[0],port)
                e1.var = a
                e2.var = b
                
                newnodes.append(copy)
                    
        for n in newnodes:
            dag.nodes.append(n)
    
    def blockFixups(self,block):
        self.muldivFixups(block)
        self.shiftFixups(block)
        self.retFixups(block)
    
    def muldivFixups(self,block):
        idx = 0
        blocklen = len(block)
        while idx < blocklen:
            instr = block[idx]
            if type(instr) in [X86IMultI32,X86IDivI32,X86IModI32]:
                if type(instr.read[0]) == ir.I32:
                    
                        
                    eax = getRegisterByName('eax')
                    edx = getRegisterByName('edx')
                    
                    if type(instr) == X86IModI32:
                        resultReg = edx
                    else:
                        resultReg = eax
                    
                    mov1 = X86MovI32()
                    mov2 = X86MovI32()
                    mov1.read = [instr.read[0]]
                    mov1.assigned = [eax]
                    mov2.read = [resultReg]
                    mov2.assigned = [instr.assigned[0]]
                    instr.read[0] = eax
                    instr.assigned = [eax,edx]
                    block.insert(idx,mov1)
                    block.insert(idx + 2,mov2)
                    idx += 2
                    blocklen += 2
                else:
                    print("unsupported type for mul fixups")
            idx += 1

    def shiftFixups(self,block):
        idx = 0
        blocklen = len(block)
        while idx < blocklen:
            instr = block[idx]
            if type(instr) in [X86SHLI32,X86SHRI32]:
                if type(instr.read[1]) == ir.I32:
                    ecx = getRegisterByName('ecx')
                    mov1 = X86MovI32()
                    mov1.read = [instr.read[1]]
                    mov1.assigned = [ecx]
                    instr.read[1] = ecx
                    block.insert(idx,mov1)
                    idx += 1
                    blocklen += 1
                else:
                    print("unsupported type for mul fixups")
            idx += 1

    def retFixups(self,block):
        idx = 0
        blocklen = len(block)
        while idx < blocklen:
            instr = block[idx]
            if type(instr) == ir.Ret:
                if type(instr.read[0]) == ir.I32:
                    eax = getRegisterByName('eax')
                    mov = X86MovI32()
                    mov.read = [instr.read[0]]
                    mov.assigned = [eax]
                    instr.read[0] = eax
                    block.insert(idx,mov)
                    idx += 1
                    blocklen += 1
                else:
                    print("unsupported type for ret")
            idx += 1
        
    
    def pushArgument(self,arg):
        if type(arg) in [ir.Pointer,ir.I32]:
            pinstr = X86PushI32()
            pinstr.read = [arg]
            return [pinstr]
        else:
            raise Exception("x86 cannot handle an argument of this type %s" % arg)
    
    def getReturnReg(self,arg):
        if type(arg) in [ir.Pointer,ir.I32]:
            return getRegisterByName('eax')
        else:
            raise Exception("x86 cannot handle a return of this type %s" % arg)
    
    
    def getCallInstruction(self,instr):
        
        if type(instr) == ir.Call:
            return X86Call(instr.label)
        else:
            print(instr)
            raise Exception("XXXX")
    
    def getStackClearingInstruction(self,amount):
        return X86StackFree(amount)
    
    def getCopyInstruction(self,toReg,fromReg):
        
        if type(fromReg) in [ir.Pointer,ir.I32]:
            ret = X86MovI32()
            ret.read = [fromReg]
            ret.assigned = [toReg]
            return ret
        else:
            raise Exception("XXXXXX")
    
    #XXX decprecate this infavour of the above?
    def getCopyFromPhysicalInstruction(self,virt,reg):
        
        if type(virt) in [ir.Pointer,ir.I32]:
            ret = X86MovI32()
            ret.read = [reg]
            ret.assigned = [virt]
            return ret
        else:
            raise Exception("XXXXXXXXX")
    
    def getEpilog(self,stackSize):
        return [X86Leave(stackSize)]
    
    def getProlog(self,stackSize):
        return [X86Enter(stackSize)]
    
    def getMatchableInstructions(self):
        return matchableInstructions
        
    def getRegisters(self):
        return registers
    
    def getSaveRegisterInstruction(self,reg,ss):
        if type(reg) in [ir.Pointer,ir.I32] or reg.canContain(ir.Pointer) or reg.canContain(ir.ir.I32):
            return X86StackSaveI32(reg,ss)
        else:
            raise Exception("unsupported save register type %s" % reg)
        
    def getLoadRegisterInstruction(self,reg,ss):
        if type(reg) in [ir.Pointer,ir.I32] or reg.canContain(ir.Pointer) or reg.canContain(ir.ir.I32):
            return X86StackLoadI32(reg,ss)
        else:
            raise Exception("unsupported load register type %s" % reg)
        
    
    def terminatorSelection(self,instr):
        
        if type(instr) == ir.Jmp:
            
            next = instr.getSuccessors()[0]
            if next == None:
                return None
            newJump = X86Jmp()
            newJump.setSuccessors(instr.getSuccessors())
            return newJump
            
            
        elif type(instr) == ir.Branch:
            
            trueBlock,falseBlock = instr.getSuccessors()
            if trueBlock == None and falseBlock == None:
                return None
            
            newBranch = X86Branch()
            newBranch.setSuccessors(instr.getSuccessors())
            newBranch.read = instr.read
            return newBranch
        
        elif type(instr) == ir.Ret:
            return X86Ret()
        else:
            raise Exception("unreachable branch selection - %s" % instr)
            


