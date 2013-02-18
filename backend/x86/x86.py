from backend import  ir

from backend import standardmachine
from backend import machineinstruction

from backend.instructionselector import *
from backend.selectiondag import *


class MultI32(machineinstruction.MI):
    
    @staticmethod
    def match(dag,node):
        
        if type(node.instr) != ir.Binop or node.instr.op != '*':
            return None
        
        if len(node.ins) != 2:
            return None
        
        if type(node.instr.read[0]) != ir.I32:
            return None
        
        if type(node.instr.read[1]) != ir.I32:
            return None
        
        if type(node.instr.assigned[0]) != ir.I32:
            return None
        
        def repl():
            m = MultI32()
            m.assigned = node.instr.assigned
            m.read = node.instr.read
            node.instr = m
        
        return InstructionMatch(repl,1)

    def asm(self):
        return "mul %s %s %s"%(self.assigned[0],self.read[0],self.read[1])

class X86LoadConstantI32(machineinstruction.MI):
    
    def __init__(self,const):
        self.const = const
    
    @staticmethod
    def match(dag,node):
        
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
        return "mov %s,%d"%(self.assigned[0],self.const.value)

class X86MovI32(machineinstruction.MI):

    @staticmethod
    def match(dag,node):
        
        if type(node.instr) != ir.Move:
            return None
        
        if len(node.ins) != 1:
            return None
        
        if type(node.instr.read[0]) != ir.I32:
            return None
        
        if type(node.instr.assigned[0]) != ir.I32:
            return None
        
        def repl():
            mov = X86MovI32()
            mov.assigned = node.instr.assigned
            mov.read = node.instr.read
            node.instr = mov
        
        return InstructionMatch(repl,1)

    def asm(self):
        return "mov %s,%s"%(self.assigned[0],self.read[0])


class AddI32(machineinstruction.MI):
    
    
    @staticmethod
    def match(dag,node):
        
        
        if type(node.instr) != ir.Binop or node.instr.op != '+':
            return None
        
        if len(node.ins) != 2:
            return None
        
        if type(node.instr.assigned[0]) != ir.I32:
            return None
        
        if node.instr.assigned[0] != node.instr.read[0]:
            return None
        
        def repl():
            add = AddI32()
            add.assigned = node.instr.assigned
            add.read = node.instr.read
            node.instr = add
        
        return InstructionMatch(repl,1)

    def asm(self):
        return "add %s,%s"%(self.assigned[0],self.read[0])

class X86LoadLocalAddr(machineinstruction.MI):
    
    
    @staticmethod
    def match(dag,node):
        
        if type(node.instr) != ir.LoadLocalAddr:
            return None
        
        
        def repl():
            lla = X86LoadLocalAddr()
            lla.assigned = node.instr.assigned
            node.instr = lla
        
        return InstructionMatch(repl,1)

    def asm(self):
        return "mov %s, ebp + XXX "%(self.assigned[0])

class X86LoadI32(machineinstruction.MI):
    
    @staticmethod
    def match(dag,node):
        
        if type(node.instr) != ir.Deref:
            return None
        
        if len(node.ins) != 1:
            return None
        
        if type(node.instr.assigned[0]) != ir.I32:
            return None
        
        def repl():
            ld = X86LoadI32()
            ld.read = node.instr.read
            ld.assigned = node.instr.assigned
            node.instr = ld
            
        return InstructionMatch(repl,1)

    def asm(self):
        return "mov %s, [%s]"%(self.assigned[0],self.read[0])

class X86StoreI32(machineinstruction.MI):
    
    @staticmethod
    def match(dag,node):
        
        if type(node.instr) != ir.Store:
            return None
        
        if len(node.ins) != 2:
            return None
        
        if type(node.instr.read[0]) != ir.I32:
            return None
        
        def repl():
            st = X86StoreI32()
            st.read = node.instr.read
            st.assigned = node.instr.assigned
            node.instr = st
            
        return InstructionMatch(repl,1)

    def asm(self):
        return "mov [%s], %s"%(self.read[0],self.read[1])


instructions = [
    AddI32,
    MultI32,
    X86MovI32,
    X86LoadI32,
    X86LoadConstantI32,
    X86LoadLocalAddr,
    X86StoreI32,
]


registers = [
    standardmachine.Register('eax',[ir.I32]),
    standardmachine.Register('ebx',[ir.I32]),
    standardmachine.Register('ecx',[ir.I32]),
    standardmachine.Register('edx',[ir.I32]),
]

def getRegisterByName(n):
    for r in registers:
        if r.name == n:
            return r
    raise Exception("bad register %s"%n)

class X86(standardmachine.StandardMachine):
    
    def getInstructions(self):
        return instructions
        
    def getRegisters(self):
        return registers
        
    def applyDagFixups(self,dag):
        print("x86 fixups")
        newnodes = []
        for n in dag.nodes:
            if type(n.instr) == ir.Binop and n.instr.op == '+':
                print("fixing up binop in DAG")
                copy = SDNode(ir.Move(n.instr.assigned[0],n.instr.read[0]))
                copy.ins = [n.ins[0]]
                n.ins[0].outs[0] = copy
                copy.outs = [n]
                n.instr.read[0] = copy.instr.assigned[0]
                n.ins[0] = copy
                newnodes.append(copy)
        dag.nodes += newnodes
    
    
    def callingConventions(self):
        newnodes = []
        for n in dag.nodes:
            if type(n.instr) == ir.Ret:
                movins = X86MovI32()
                eax = getRegisterByName('eax')
                movins.assigned = [eax]
                n.instr.assigned = eax
                movins.read = n.instr.read
                copy = SDNode(movins)
                copy.ins = n.ins[0].outs
                n.ins[0].outs = [copy]
                copy.outs = n.outs
                n.ins = movins.outs
                
    
