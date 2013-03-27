import itertools


class StackSlot(object):
    
    def __init__(self,size):
        self.size = size
        self.offset = None
    

class Function(object):
    def __init__(self,name):
        self.name = name
        self.entry = None
        self.stackslots = []
    
    def addStackSlot(self,ss):
        #XXX probably pretty inefficient
        if ss not in self.stackslots:
            self.stackslots.append(ss)
    
    def resolveStack(self):
        offset = 0
        for slot in self.stackslots:
            slot.offset = offset
            offset += slot.size
    
    def setEntryBlock(self,entry):
        self.entry = entry
    
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
