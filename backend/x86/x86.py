from backend import  ir

from backend import standardmachine
from backend import machineinstruction

from backend.instructionselector import *


class MovI32(machineinstruction.MI):
    
    
    
    @staticmethod
    def match(node):
        
        if type(node) != ir.Move:
            return None
        
        if len(node.read) != 1:
            return None
        
        if type(node.read[0]) != ir.I32:
            return None
        
        if len(node.assigned) != 1:
            return None
        
        if type(node.assigned[0]) != ir.I32:
            return None
        
        
        mov = MovI32()
        mov.assigned = node.assigned
        mov.read = node.read
        
        return InstructionMatch([mov],[node],1)
    
class AddI32(machineinstruction.MI):
    
    @staticmethod
    def match(node):
        
        if type(node) != ir.Binop or node.op != '+':
            return None
        
        if len(node.read) != 2:
            return None
        
        if type(node.read[0]) != ir.I32:
            return None
        
        if type(node.read[1]) != ir.I32:
            return None
        
        if len(node.assigned) != 1:
            return None
        
        if type(node.assigned[0]) != ir.I32:
            return None
        
        if node.assigned[0] != node.read[0] or node.assigned[0] != node.read[1]:
            return None
        
        add.assigned = node.assigned
        add.read = node.read
        
        return InstructionMatch([add],[node],1)
    
    
    
    def asm(self):
        
        if self.read[0] == self.assigned[0]:
            l,r = self.read[0],self.read[1]
        elif self.read[1] == self.assigned[0]:
            r,l = self.read[0],self.read[1]
        else:
            raise Exception("unreachable")
        
        return "add %s,%s" %(l,r)
        
class LoadI32(machineinstruction.MI):
    
    @staticmethod
    def match(node):
        
        if type(node) != ir.Deref:
            return None
        
        if len(node.read) != 2:
            return None
        
        if type(node.read[0]) != ir.I32:
            return None
        
        if node.pcount == 0:
            return None
        
        if type(node.read[1]) != ir.I32:
            return None
        
        if len(node.assigned) != 1:
            return None
        
        if type(node.assigned[0]) != ir.I32:
            return None
        
        
        add = AddI32()
        add.assigned = node.assigned
        add.read = node.read
        
        return InstructionMatch([add],[node],1)

class MultI32(machineinstruction.MI):
    
    @staticmethod
    def match(node):
        
        if type(node) != ir.Binop or node.op != '*':
            return None
        
        if len(node.read) != 2:
            return None
        
        if type(node.read[0]) != ir.I32:
            return None
        
        if type(node.read[1]) != ir.I32:
            return None
        
        if len(node.assigned) != 1:
            return None
        
        if type(node.assigned[0]) != ir.I32:
            return None
        
        
        mult = MultI32()
        mult.assigned = node.assigned
        mult.read = node.read
        
        return InstructionMatch([mult],[node],1)


class X86LoadLocalI32(machineinstruction.MI):
    
    @staticmethod
    def match(node):
        
        if type(node) != ir.Deref:
            return None
        
        if len(node.read) != 1:
            return None
        
        if len(node.assigned) != 1:
            return None
        
        if type(node.assigned[0]) != ir.I32:
            return None
        
        ld = X86LoadConstantI32()
        ld.assigned = node.assigned
        ld.read = node.read
        
        return InstructionMatch([ld],[node],1)


class X86LoadConstantI32(machineinstruction.MI):
    
    @staticmethod
    def match(node):
        
        if type(node) != ir.LoadConstant:
            return None
        
        if len(node.read) != 0:
            return None
        
        if len(node.assigned) != 1:
            return None
        
        if type(node.assigned[0]) != ir.I32:
            return None
        
        ld = X86LoadConstantI32()
        ld.assigned = node.assigned
        ld.read = node.read
        
        return InstructionMatch([ld],[node],1)


instr = [
    MovI32,
    AddI32,
    MultI32,
    X86LoadConstantI32,
]

class X86(standardmachine.StandardMachine):
    
    def getInstructions(self):
        return instr
