from backend import  ir

from backend import standardmachine
from backend import machineinstruction

from backend.instructionselector import *
import backend.selectiondag as seldag

import x86md


#used for small assembly snippets
#that need to branch that dont currently
#introduce a basic block
branchcounter = 0
def newLocalLabel():
    global branchcounter
    branchcounter += 1
    return ".__l%d"%branchcounter


class X86Push(machineinstruction.MI):
    
    def asm(self):
        return "push %%%s"%(self.read[0])

class X86Nop(machineinstruction.MI):
    def asm(self):
        return "nop"

class X86Call(machineinstruction.MI):
    def __init__(self,label):
        machineinstruction.MI.__init__(self)
        self.label = label
    
    def isCall(self):
        return True
    
    def asm(self):
        return "call %s" % self.label

class X86Ret(machineinstruction.MI):
    def asm(self):
        return "ret"

class X86Enter(machineinstruction.MI):
    def __init__(self,stackSize):
        machineinstruction.MI.__init__(self)
        self.stackSize = stackSize
    def asm(self):
        ret = "pushl %ebp\nmovl %esp,%ebp"
        if self.stackSize:
              ret += "\nsubl $%s,%%esp" % self.stackSize
        return ret

class X86Leave(machineinstruction.MI):
    def __init__(self, stackSize):
        machineinstruction.MI.__init__(self)
        self.stackSize = stackSize
    def asm(self):
        if self.stackSize:
            ret = "addl $%s,%%esp\n"% self.stackSize
        else:
            ret = ""
        ret += "popl %ebp" 
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
            return "mov -%d(%%ebp), %%%s"%(self.slot.offset,self.assigned[0])
        else:
            return "mov -XXX(%%ebp), %%%s"%(self.assigned[0])
    
    def getStackSlots(self):
        return [self.slot]

class X86StackLoadI8(machineinstruction.MI):
    def __init__(self,reg,slot):
        machineinstruction.MI.__init__(self)
        self.slot = slot
        self.assigned = [reg]

    def asm(self):
        
        if self.slot.offset != None:
            return "mov -%d(%%ebp), %%%s"%(self.slot.offset,self.assigned[0])
        else:
            return "mov -XXX(%%ebp), %%%s"%(self.assigned[0])
    
    def getStackSlots(self):
        return [self.slot]    


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
        
    def getStackSlots(self):
        return [self.slot]        


class X86StackSaveI8(machineinstruction.MI):
    def __init__(self,reg, slot):
        machineinstruction.MI.__init__(self)
        self.slot = slot
        self.read = [reg]
    
    def asm(self):
        if self.slot.offset != None:
            return "mov %%%s,-%d(%%ebp)"%(self.read[0],self.slot.offset)
        else:
            return "mov %%%s,-XXX(%%ebp)"%(self.read[0])
        
    def getStackSlots(self):
        return [self.slot]    


matchableInstructions = x86md.matchableInstructions

class GR32(standardmachine.Register):
    types = [ir.I32,ir.Pointer]
    
class GR8(standardmachine.Register):
    types = [ir.I8]

registers = [
    GR32('eax',),
    GR32('ebx'),
    GR32('ecx'),
    GR32('edx'),
    GR8('al'),
    GR8('bl'),
    GR8('cl'),
    GR8('ah'),
    GR8('bh'),
    GR8('ch'),
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
                
                if True:#len(n.children[0][1].parents) > 1:
                    a,b = n.instr.assigned[0],n.instr.read[0]
                    copy = seldag.Node(ir.Move(a,b))
                    n.instr.read[0] = a
                    copy.children.append(n.children[0])
                    n.children[0] = (0,copy)
                elif len(n.children[0][1].parents) == 1:
                    n.instr.read[0] = n.instr.assigned[0]
                    n.children[0][1].instr.assigned[0] = n.instr.assigned[0] 
                else:
                    raise Exception("bug! unreachable!")
        
        dag.recalculateParents()
        dag.sanityCheck()
    
    def blockFixups(self,block):
        self.muldivFixups(block)
        self.shiftFixups(block)
    
    def muldivFixups(self,block):
        idx = 0
        blocklen = len(block)
        while idx < blocklen:
            instr = block[idx]
            if type(instr) in [x86md.X86IMulI32,x86md.X86IDivI32,x86md.X86IModI32]:
                if type(instr.read[0]) == ir.I32:
                    print instr.assigned,instr.read
                    eax = getRegisterByName('eax')
                    edx = getRegisterByName('edx')
                    
                    if type(instr) == x86md.X86IModI32:
                        resultReg = edx
                    else:
                        resultReg = eax
                    
                    mov1 = x86md.X86MovI32()
                    mov2 = x86md.X86MovI32()
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
                    #print instr.assigned,instr.read
                else:
                    raise Exception("unsupported type for mul fixups")
            idx += 1

    def shiftFixups(self,block):
        idx = 0
        blocklen = len(block)
        while idx < blocklen:
            instr = block[idx]
            if type(instr) in [x86md.X86SHLI32,x86md.X86SHRI32]:
                if type(instr.read[1]) == ir.I32:
                    mov1 = x86md.X86MovI32()
                    r = getRegisterByName('ecx')
                else:
                    raise Exception("unsupported type for shift fixups")
                
                mov1.read = [instr.read[1]]
                mov1.assigned = [r]
                instr.read[1] = r
                block.insert(idx,mov1)
                idx += 1
                blocklen += 1

            idx += 1
    
        
    
    def pushArgument(self,arg):
        if type(arg) in [ir.Pointer,ir.I32]:
            pinstr = X86Push()
            pinstr.read = [arg]
            return [pinstr]
        else:
            raise Exception("x86 cannot handle an argument of this type %s" % arg)
    
    def getReturnReg(self,arg):
        if type(arg) in [ir.Pointer,ir.I32]:
            return getRegisterByName('eax')
        elif type(arg) == ir.I8:
            return getRegisterByName('al')
        else:
            raise Exception("x86 cannot handle a return of this type %s" % arg)
    
    def getRetInstruction(self,instr):
        return X86Ret()
        
    def getCallInstruction(self,instr):
        return X86Call(instr.label)
    
    def getStackClearingInstruction(self,amount):
        return X86StackFree(amount)
    
    def getCopyInstruction(self,toReg,fromReg):
        
        if type(fromReg) in [ir.Pointer,ir.I32] or type(toReg) in [ir.Pointer,ir.I32]:
            ret = x86md.X86MovI32()
            ret.read = [fromReg]
            ret.assigned = [toReg]
            return ret
        elif type(fromReg) in [ir.I8] or type(toReg) in [ir.I8]:
            ret = x86md.X86MovI8()
            ret.read = [fromReg]
            ret.assigned = [toReg]
            return ret
        else:
            raise Exception("unable to deduce copy for %s %s"%(toReg,fromReg))
    
    
    def getEpilog(self,stackSize):
        return [X86Leave(stackSize)]
    
    def getProlog(self,stackSize):
        return [X86Enter(stackSize)]
    
    def getMatchableInstructions(self):
        return matchableInstructions
        
    def getRegisters(self):
        return registers
    
    def getSaveRegisterInstruction(self,reg,ss):
        if type(reg) in [ir.Pointer,ir.I32] or reg.canContain(ir.Pointer) or reg.canContain(ir.I32):
            return X86StackSaveI32(reg,ss)
        elif type(reg) in [ir.I8] or reg.canContain(ir.I8):
            return X86StackSaveI8(reg,ss)
        else:
            raise Exception("unsupported save register type %s" % reg)
        
    def getLoadRegisterInstruction(self,reg,ss):
        if type(reg) in [ir.Pointer,ir.I32] or reg.canContain(ir.Pointer) or reg.canContain(ir.I32):
            return X86StackLoadI32(reg,ss)
        elif type(reg) in [ir.I8] or reg.canContain(ir.I8):
            return X86StackLoadI8(reg,ss)
        else:
            raise Exception("unsupported load register type %s" % reg)
        
    
            


