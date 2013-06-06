from backend import  ir

from backend import standardmachine
from backend import machineinstruction

from backend.instructionselector import *
from backend.selectiondag import *

#used for small assembly snippets
#that need to branch that dont currently
#introduce a basic block
branchcounter = 0
def newLocalLabel():
    global branchcounter
    branchcounter += 1
    return ".__l%d"%branchcounter


class X86BasicBinop(machineinstruction.MI):
    
    twoaddress = True

    @classmethod
    def match(cls,dag,node):
        
        if type(node.instr) != ir.Binop or node.instr.op != cls.op:
            return None
        
        if len(node.ins) != 2:
            return None
        
        if type(node.instr.read[0]) not in cls.allowedtypes:
            return None
        
        if type(node.instr.read[1]) not in cls.allowedtypes:
            return None
        
        if type(node.instr.assigned[0]) not in cls.allowedtypes:
            return None
        
        if cls.twoaddress:
            if node.instr.assigned[0] != node.instr.read[0]:
                return None
        
        def repl():
            m = cls()
            m.assigned = node.instr.assigned
            m.read = node.instr.read
            node.instr = m
        
        return InstructionMatch(repl,1)

class X86BasicUnop(machineinstruction.MI):
    
    @classmethod
    def match(cls,dag,node):
        
        if type(node.instr) != ir.Unop or node.instr.op != cls.op:
            return None
        
        if len(node.ins) != 1:
            return None
        
        if type(node.instr.read[0]) not in cls.allowedtypes:
            return None
        
        if type(node.instr.assigned[0]) not in cls.allowedtypes:
            return None
        
        
        def repl():
            m = cls()
            m.assigned = node.instr.assigned
            m.read = node.instr.read
            node.instr = m
        
        return InstructionMatch(repl,1)

class X86BasicUnopI32(X86BasicUnop):
    allowedtypes = (ir.Pointer,ir.I32)

class X86BasicBinopI32(X86BasicBinop):
    allowedtypes = (ir.Pointer,ir.I32)

class X86Sext(X86BasicUnop):
    op = 'sx'
    allowedtypes = [ir.I32,ir.I8]
    def asm(self):
        return "movsx %{0},%{1}".format(self.read[0],self.assigned[0])

class X86Zext(X86BasicUnop):
    op = 'zx'
    allowedtypes = [ir.I32,ir.I8]

    def asm(self):
        return "movzx %{0},%{1}".format(self.read[0],self.assigned[0])


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
    
    def getPreClobberedRegisters(self):
        return [getRegisterByName('edx')]
    
    def asm(self):
        return "cdq; idiv %%%s"%(self.read[1])

class X86IModI32(X86BasicBinopI32):
    op = '%'
    
    def getPreClobberedRegisters(self):
        return [getRegisterByName('edx')]
    
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

class X86Comparison(X86BasicBinop):
    twoaddress = False
    allowedtypes = [ir.Pointer,ir.I8,ir.I32]

    def __init__(self):
        X86BasicBinop.__init__(self)
        self.branch  = newLocalLabel() 
        self.exit    = newLocalLabel()

    def asm(self):
        ret = \
        "cmp %{2},%{1}\n" + \
        "{jmpinstr} {branch}\n" + \
        "xor %{0},%{0}\n" + \
        "jmp {exit}\n" + \
        "{branch}:\n" + \
        "xor %{0},%{0}\n" + \
        "inc %{0}\n" + \
        "{exit}:"
        
        ret = ret.format(   self.assigned[0],self.read[0],
                            self.read[1],jmpinstr=self.jmpinstr,
                            branch=self.branch,exit=self.exit)
        return ret


class X86Eq(X86Comparison):
    jmpinstr = 'je'
    op = '=='

class X86Ne(X86Comparison):
    op = '!='
    jmpinstr = 'jne'

class X86Gt(X86Comparison):
    op = '>'
    jmpinstr = 'jg'    
 
class X86Lt(X86Comparison):
    op = '<'
    jmpinstr = 'jl'    
    

class X86LoadConstant(machineinstruction.MI):
    
    def __init__(self,const):
        machineinstruction.MI.__init__(self)
        self.const = const
    
    @classmethod
    def match(cls,dag,node):
        
        if type(node.instr) != ir.LoadConstant:
            return None
        
        if len(node.ins) != 0:
            return None
        
        if type(node.instr.assigned[0]) not in  [ir.I32,ir.I8]:
            return None
        
        def repl():
            ld = X86LoadConstant(node.instr.const)
            ld.assigned = node.instr.assigned
            ld.read = node.instr.read
            node.instr = ld
        
        return InstructionMatch(repl,1)

    def asm(self):
        return "mov $%d,%%%s"%(self.const.value,self.assigned[0])

class X86Mov(machineinstruction.MI):
    
    def isMove(self):
        return True
    
    @classmethod
    def match(cls,dag,node):
        
        if type(node.instr) != ir.Move:
            return None
        
        if len(node.ins) != 1:
            return None
            
        if type(node.instr.read[0]) not in (ir.I8,ir.I32,ir.Pointer):
            return None
        
        if type(node.instr.assigned[0]) not in (ir.I8,ir.I32,ir.Pointer):
            return None
        
        #assert(type(node.instr.read[0]) == type(node.instr.assigned[0]))
        
        def repl():
            mov = X86Mov()
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



class X86Load(machineinstruction.MI):
    
    @classmethod
    def match(cls,dag,node):
        
        if type(node.instr) != ir.Deref:
            return None
        
        if len(node.ins) != 1:
            return None
        
        if type(node.instr.assigned[0]) not in (ir.I32,ir.I8,ir.Pointer):
            return None
        
        if type(node.instr.read[0]) != ir.Pointer:
            return None

        def repl():
            ld = X86Load()
            ld.read = node.instr.read
            ld.assigned = node.instr.assigned
            node.instr = ld
            
        return InstructionMatch(repl,1)

    def asm(self):
        return "mov (%%%s),%%%s"%(self.read[0],self.assigned[0])

class X86Store(machineinstruction.MI):
    
    @classmethod
    def match(cls,dag,node):
        
        if type(node.instr) != ir.Store:
            return None
        
        if len(node.ins) != 2:
            return None
        
        if type(node.instr.read[0]) != ir.Pointer:
            return None
        
        if type(node.instr.read[1]) not in (ir.I32,ir.I8,ir.Pointer):
            return None
        
        
        def repl():
            st = X86Store()
            st.read = node.instr.read
            st.assigned = node.instr.assigned
            node.instr = st
            
        return InstructionMatch(repl,1)

    def asm(self):
        return "mov %%%s, (%%%s)"%(self.read[1],self.read[0])

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
        
        if self.slot.offset != None:
            return "mov -%d(%%ebp), %%%s "%(self.slot.offset,self.assigned[0])
        else:
            return "mov -XXX(%%ebp), %%%s "%(self.assigned[0])
    
        
        


class X86StackSaveI32(machineinstruction.MI):
    def __init__(self,reg, slot):
        machineinstruction.MI.__init__(self)
        self.slot = slot
        self.read = [reg]
    
    def asm(self):
        if self.slot.offset != None:
            return "mov %%%s,-%d(%%ebp)"%(self.read[0],self.slot.offset)
        else:
            return "mov %%%s,-XXX(%%ebp)"%(self.read[0])
        
        


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
    X86Mov,
    X86Load,
    X86LoadConstant,
    X86LoadParamAddr,
    X86LoadLocalAddr,
    X86LoadGlobalAddr,
    #X86StoreLocalI32,
    X86Store,
    X86Eq,
    X86Ne,
    X86Gt,
    X86Lt,
    X86NotI32,
    X86Sext,
    X86Zext,
#   X86PushI32,
]


registers = [
    standardmachine.Register('eax',[ir.I32,ir.Pointer]),
    standardmachine.Register('ebx',[ir.I32,ir.Pointer]),
    standardmachine.Register('ecx',[ir.I32,ir.Pointer]),
    standardmachine.Register('edx',[ir.I32,ir.Pointer]),
    standardmachine.Register('edi',[ir.I32,ir.Pointer]),
    standardmachine.Register('esi',[ir.I32,ir.Pointer]),
    standardmachine.Register('al',[ir.I8]),
    standardmachine.Register('bl',[ir.I8]),
    standardmachine.Register('cl',[ir.I8]),
    standardmachine.Register('ah',[ir.I8]),
    standardmachine.Register('bh',[ir.I8]),
    standardmachine.Register('ch',[ir.I8]),
]

interferes = {
    'eax' : ['al','ah'],
    'ebx' : ['bl','bh'],
    'ecx' : ['cl','ch'],
    'al'  : ['eax'],
    'bl'  : ['ebx'],
    'cl'  : ['ecx'],
    'ah'  : ['eax'],
    'bh'  : ['ebx'],
    'ch'  : ['ecx'],
}

def getRegisterByName(n):
    for r in registers:
        if r.name == n:
            return r
    raise Exception("bad register %s"%n)

for k in interferes:
    interferes[k] = list(map(lambda n : getRegisterByName(n) ,interferes[k]))


#XXX needs to be refactored to no longer be a god object
#need to separate responsibilities

class X86(standardmachine.StandardMachine):
    
    def getInterferenceSet(self,reg):
        return interferes.get(reg.name,set([]))

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
                    
                    mov1 = X86Mov()
                    mov2 = X86Mov()
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
                    mov1 = X86Mov()
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
                if len(instr.read):
                    if type(instr.read[0]) == ir.I32:
                        eax = getRegisterByName('eax')
                        mov = X86Mov()
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
        
        if type(fromReg) in [ir.Pointer,ir.I32,ir.I8]:
            ret = X86Mov()
            ret.read = [fromReg]
            ret.assigned = [toReg]
            return ret
        else:
            raise Exception("XXXXXX")
    
    #XXX decprecate this infavour of the above?
    def getCopyFromPhysicalInstruction(self,virt,reg):
        
        if type(virt) in [ir.Pointer,ir.I32,ir.I8]:
            ret = X86Mov()
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
            


