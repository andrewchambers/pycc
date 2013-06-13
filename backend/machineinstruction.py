
from ir import Instruction

class MI(Instruction):
    
    def asm(self):
        args = self.assigned + self.read
        return self.asmstr.format(*args,instr=self)
    
    def getDagDisplayText(self):
        return str(self)
    
    def isMD(self):
        return True
    
    def __repr__(self):
        return self.asm()
