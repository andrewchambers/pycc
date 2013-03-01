import itertools

class Function(object):
    def __init__(self,name):
        self.name = name
        self.entry = None
    
    def setEntryBlock(self,entry):
        self.entry = entry
    
    def getName(self):
        return self.name
    
    @property
    def variables(self):
        ret = set()
        for block in self:
            for instr in block:
                for v in itertools.chain(instr.read,instr.assigned):
                    ret.add(v)
        return ret
        
    @variables.setter
    def variables(self, value):
        raise Exception("bug - cannot set variables of a function")
        
    def __iter__(self):
        return self.entry.getReachableBlocks().__iter__()
