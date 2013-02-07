
class BasicBlock(object):
    
    def __init__(self):
        self.opcodes = []
    def appendOpcode(self,op):
        self.opcodes.append(op)
