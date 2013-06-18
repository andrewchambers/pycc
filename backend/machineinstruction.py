
from ir import Instruction

class MI(Instruction):
    
    def __init__(self,node=None):
        Instruction.__init__(self)
    
    def asm(self):
        args = self.assigned + self.read
        return self.asmstr.format(*args,instr=self)
    
    def getDagDisplayText(self):
        return str(self)
    
    def isMD(self):
        return True
    
    def __repr__(self):
        return self.asm()
    
    @classmethod
    def match(cls,node):
        return cls.pattern.match(node)
    
    @classmethod
    def replace(cls,node,inst):
        cls.pattern.replace(node,inst)
