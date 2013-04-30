
from ir import Instruction

class MI(Instruction):
    
    needsTwoAddressFixup = False
    
    
    def asm(self):
        return self.__class__.__name__
    
    def getDagDisplayText(self):
        return str(self)
    
    def isMD(self):
        return True
    
    def __repr__(self):
        return self.asm()
