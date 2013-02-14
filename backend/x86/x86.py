from backend import  ir

from backend import standardmachine
from backend import machineinstruction

from backend.instructionselector import *


class MovI32(machineinstruction.MI):
    
    pattern = Set(ir.I32,ir.I32)
    
class AddI32(machineinstruction.MI):
    
    pattern = Set(ir.I32,Add(ir.I32,ir.I32))


class LoadI32(machineinstruction.MI):
    
    pattern = Set(ir.I32,LoadConstant())

class X86(standardmachine.StandardMachine):
    
    def getInstructions(self):
        pass
