
from ir import Instruction

class MI(Instruction):
    
    def asm(self):
        return self.__class__.__name__
    
    def getDagDisplayText(self):
        return self.asm()
    
    def isMD(self):
        return True
