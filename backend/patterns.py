import ir

class TypePattern(object):
    
    def __init__(self,t):
        self.t = t
    
    def match(self,node):
        
        if len(node.instr.assigned) != 1:
            return False
        
        if type(node.instr.assigned[0]) != self.t:
            return False
        
        return True
    
    def replace(self,node,newinstr):
        newinstr.read.append(node.instr.assigned[0])
        

I32 = TypePattern(ir.I32)
I8 = TypePattern(ir.I8)
Pointer = TypePattern(ir.Pointer)


class Set(object):

    def __init__(self,opattern,pattern):
        self.opattern = opattern
        self.pattern = pattern
    
    def match(self,node):
        
        if self.opattern.match(node) == False:
            return False
        
        if self.pattern.match(node) == False:
            return False
        
        return True
    
    def replace(self,node,newinstr):
        newinstr.assigned = [node.instr.assigned[0]]
        node.instr = newinstr
        self.pattern.replace(node,newinstr)

class Unop(object):
    def __init__(self,op,pattern):
        self.pattern = pattern
        self.op = op
    
    def match(self,node):
        
        if len(node.instr.read) != 1:
            return False
        
        if type(node.instr) != ir.Unop:
            return False
        
        if node.instr.op != self.op:
            return False
            
        if self.pattern.match(node.children[0][1]) == False:
            return False
        
        return True
    
    def replace(self,node,newinstr):
        self.pattern.replace(node.children[0][1],newinstr)


class Binop(object):
    def __init__(self,op,lpattern,rpattern):
        self.lpattern = lpattern
        self.rpattern = rpattern
        self.op = op
    
    def match(self,node):
        
        
        if len(node.instr.read) != 2:
            return False
        
        if type(node.instr) != ir.Binop:
            return False
        
        if node.instr.op != self.op:
            return False
            
        if self.lpattern.match(node.children[0][1]) == False:
            return False
        
        if self.rpattern.match(node.children[1][1]) == False:
            return False
            
        return True
    
    def replace(self,node,newinstr):
        
        self.lpattern.replace(node.children[0][1],newinstr)
        self.rpattern.replace(node.children[1][1],newinstr)

class LoadLocalAddr(object):
    
    def match(self,node):
        
        if len(node.instr.read) != 0:
            return False
        
        if type(node.instr) != ir.LoadLocalAddr:
            return False
            
        return True
    
    def replace(self,node,newinstr):
        pass

class LoadParamAddr(object):
    
    def match(self,node):
        
        if len(node.instr.read) != 0:
            return False
        
        if type(node.instr) != ir.LoadParamAddr:
            return False
            
        return True
    
    def replace(self,node,newinstr):
        pass

class LoadGlobalAddr(object):
    
    def match(self,node):
        
        if len(node.instr.read) != 0:
            return False
        
        if type(node.instr) != ir.LoadGlobalAddr:
            return False
            
        return True
    
    def replace(self,node,newinstr):
        pass

class LoadConstant(object):
    
    def match(self,node):
        
        if len(node.instr.read) != 0:
            return False
        
        if type(node.instr) != ir.LoadConstant:
            return False
            
        return True
    
    def replace(self,node,newinstr):
        pass

class Move(object):
    
    def __init__(self,pattern):
        self.pattern = pattern
    
    def match(self,node):
        
        if len(node.instr.read) != 1:
            return False
        
        if type(node.instr) != ir.Move:
            return False
            
        if self.pattern.match(node) == False:
            return False
            
        return True
    
    def replace(self,node,newinstr):
        self.pattern.replace(node.children[0][1],newinstr)

class Store(object):
    
    def __init__(self,ppattern,vpattern):
        self.ppattern = ppattern #pointer pattern
        self.vpattern = vpattern #value pattern
    
    def match(self,node):
        
        if len(node.instr.read) != 2:
            return False
        
        if type(node.instr) != ir.Store:

            return False
        
        if self.ppattern.match(node.children[0][1]) == False:
            return False
        
        if self.vpattern.match(node.children[1][1]) == False:
            return False 
        
        return True
    
    def replace(self,node,newinstr):
        node.instr = newinstr
        self.ppattern.replace(node.children[0][1],newinstr)
        self.vpattern.replace(node.children[1][1],newinstr)

class Deref(object):
    
    def __init__(self,ppattern):
        self.ppattern = ppattern #pointer pattern
    
    def match(self,node):
        
        if len(node.instr.read) != 1:
            return False
        
        if type(node.instr) != ir.Deref:
            return False
        
        if self.ppattern.match(node.children[0][1]) == False:
            return False
        
        
        return True
    
    def replace(self,node,newinstr):
        self.ppattern.replace(node.children[0][1],newinstr)


class Branch(object):
    
    def __init__(self,pattern):
        self.pattern = pattern
    
    def match(self,node):
        
        if len(node.instr.read) != 1:
            return False
        
        if type(node.instr) != ir.Branch:
            return False
        
        if self.pattern.match(node.children[0][1]) == False:
            return False
        
        
        return True
    
    def replace(self,node,newinstr):
        node.instr = newinstr
        self.pattern.replace(node.children[0][1],newinstr)
        
class Jmp(object):
    
    
    def match(self,node):
        
        if len(node.instr.read) != 0:
            return False
        
        if type(node.instr) != ir.Jmp:
            return False
        
        return True
    
    def replace(self,node,newinstr):
        node.instr = newinstr
        
        
        
        
