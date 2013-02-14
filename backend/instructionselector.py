from backend import ir

class InstructionMatcher(object):
    pass
    
class UniMatcher(InstructionMatcher):
    def __init__(self,t1):
        self.t1 = t1

class BiMatcher(InstructionMatcher):
    def __init__(self,t1,t2):
        self.t1 = t1
        self.t2 = t2
        
class TriMatcher(InstructionMatcher):
    def __init__(self,t1,t2,t3):
        self.t1 = t1
        self.t2 = t2
        self.t3 = t3

class Set(BiMatcher):
    
    def match(self,node):
        
        if len(node.assigned) != 1:
            return False
        
        if self.t1 != node.assigned[0]:
            return False
        
        return self.t2.match(node)

class LoadConstant(InstructionMatcher):
    
    def match(self,node):
        
        if type(node) != ir.LoadConstant:
            return False
            
        return True


class Add(BiMatcher):
    def match(self,node):
        
        if type(node) != ir.Binop:
            return False
            
        if node.op != '+':
            return False
            
        if not match(self.t1,0):
            return False
            
        if not match(self.t2,0):
            return False
        
        return True






class InstructionSelector(object):
    
    def select(self,target,dag):
        pass













