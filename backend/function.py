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
        self.localsSize = 0
        self.argumentslots = []
    
    def createAndAddSpillSlot(self,size):
        ss = StackSlot(size)
        self.addStackSlot(ss)
        return ss
    
    def addArgumentSlot(self,ss):
        if ss not in self.argumentslots:
            self.argumentslots.append(ss)
    
    def addStackSlot(self,ss):
        #XXX probably pretty inefficient
        if ss not in self.stackslots:
            self.stackslots.append(ss)
    
    def resolveArguments(self):
        offset = 0
        for slot in self.argumentslots:
            slot.offset = offset
            offset += slot.size
        self.paramsSize = offset
    
    def resolveStack(self):
        offset = 0
        for slot in self.stackslots:
            slot.offset = offset
            offset += slot.size
        self.localsSize = offset
    
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
