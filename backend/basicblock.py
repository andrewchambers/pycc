
blockCounter = 0

class BasicBlock(object):
    
    def __init__(self):
        global blockCounter
        blockCounter += 1
        self.opcodes = []
        self.name = ".L%d" % blockCounter
    
    def __getitem__(self,k):
        return self.opcodes[k]
    
    def append(self,op):
        self.opcodes.append(op)
    
    def __len__(self):
        return len(self.opcodes)
    
    def __iter__(self):
        return self.opcodes.__iter__()
    
    def getName(self):
        return self.name
    
    def __repr__(self):
        return self.getName()