import itertools


class StackSlot(object):
    
    def __init__(self,size):
        assert(size > 0)
        assert(size % 4 == 0)
        self.size = size
        self.offset = None
    

class Function(object):
    def __init__(self,name):
        self.name = name
        self.entry = None
        self.localsSize = 0
        self.argumentslots = []
    
    def createStackSlot(self,size):
        ss = StackSlot(size)
        return ss
    
    def addArgumentSlot(self,ss):
        if len(self.argumentslots) == 0:
            ss.offset = 0
        else:
            ss.offset = self.argumentslots[-1].offset + self.argumentslots[-1].size
        self.argumentslots.append(ss)
    
    def resolveStack(self):
        #XXX depends if stack grows up or down...
        offset = 0
        for slot in self.stackslots:
            offset += slot.size
            slot.offset = offset
        self.localsSize = offset
    
    def setEntryBlock(self,entry):
        self.entry = entry
    
    @property
    def stackslots(self):
        ret = []
        s = set()
        for block in self:
            for instr in block:
                for ss in instr.getStackSlots():
                    if ss not in s:
                        s.add(ss)
                        ret.append(ss)
        return ret
    
    @property
    def variables(self):
        ret = []
        s = set()
        for block in self:
            for instr in block:
                for v in itertools.chain(instr.read,instr.assigned):
                    if v not in s:
                        s.add(v)
                        ret.append(v)
        return ret
        
    @variables.setter
    def variables(self, value):
        raise Exception("bug - cannot set variables of a function")
        
    def __iter__(self):
        return self.entry.getReachableBlocks().__iter__()
