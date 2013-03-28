
blockCounter = 0

class BasicBlock(object):
    
    def __init__(self):
        global blockCounter
        blockCounter += 1
        self.opcodes = []
        self.name = "Block%d" % blockCounter
    
    def __getitem__(self,k):
        return self.opcodes[k]
    
    def __setitem__(self,k,v):
        self.opcodes[k] = v
    
    def prepend(self,op):
        self.opcodes.insert(0,op)
    
    def append(self,op):
        self.opcodes.append(op)
    
    def __len__(self):
        return len(self.opcodes)
    
    def __iter__(self):
        return self.opcodes.__iter__()
    
    def __repr__(self):
        return self.name
    
    def unsafeEnding(self):
        if len(self) == 0 or (not self[-1].isTerminator() and not self[-1].isBranch()):
            return True
        return False
    
    
    def getReachableBlocks(self):
        def generator():
            visited = set()
            stack = [self]
            while (len(stack)):
                curblock = stack.pop()
                if curblock in visited:
                    continue
                visited.add(curblock)
                yield curblock
                if len(curblock):
                    for b in curblock[-1].getSuccessors():
                        stack.append(b)
        return generator()
    
    
