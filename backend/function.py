
class Function(object):
    def __init__(self,name):
        self.name = name
        self.entry = None
    
    def setEntryBlock(self,entry):
        self.entry = entry
    
    def getName(self):
        return self.name
    
    def __iter__(self):
        def generator():
            stack = [self.entry]
            while (len(stack)):
                curblock = stack.pop()
                if not len(curblock):
                    continue
                yield curblock
                for b in curblock[-1].getSuccessors():
                    stack.append(b)
        
        return generator().__iter__()