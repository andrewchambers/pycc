import ir

class I32(object):
    
    def match(self,node):
        
        if len(node.instr.assigned) != 1:
            return False
        
        if node.instr.assigned[0] != ir.I32:
            return False
        
        return True
    
    def replace(self,node,newinstr):
        newinstr.read.append(node.instr.assigned[0])

class Set(object):

    def __init__(self,opattern,pattern):
        self.opattern = opattern
        self.pattern = pattern
    
    def match(self,node):
        
        if self.opattern.match(node) == False:
            return False
        
        if self.pattern.match(node):
            return True
    
    def replace(self,node,newinstr):
        newinstr.assigned[0] = newinstr
        node.instr = newinstr


def Binop(object):
    def __init__(self,op,lpattern,rpattern):
        self.lpattern = lpattern
        self.rpattern = rpattern
        self.op = op
    
    def match(self,node):
        
        #Set checks return type
        
        if len(node.read) != 2:
            return False
        
        if type(node.instr) != ir.Binop:
            return False
        
        if len(node.parents) != 1:
            return False
        
        if node.instr.op != self.op:
            return False
            
        if self.lpattern.match(node.children[0]) == False:
            return False
        
        if self.rpattern.match(node.children[1]) == False:
            return False
            
        return True
    
    def replace(self,node,newinstr):
        self.lpattern.replace(node,newinstr)
        self.rpattern.replace(node,newinstr)
