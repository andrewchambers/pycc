
counter = 0

class Variable(object):
    def __init__(self):
        global counter
        counter += 1
        self.name = "v%d"%counter
        self.lval = False
        self.pcount = 0
    
    def isPhysicalRegister(self):
        return False
    
    def __repr__(self):
        tstr = "%s" % self.__class__.__name__
        if self.lval:
            tstr += " lval"
        stars = "*"* self.pcount
        return "(%s%s) %s" %(tstr,stars,self.name)
    
class I32(Variable):
    pass

class Constant(object):
    def __repr__(self):
        return "%s"%self.value

class ConstantI32(Constant):
    def __init__(self,v):
        self.value = int(v)

class Instruction(object):
    
    def __init__(self):
        self.assigned = []
        self.read = []
        self.successors = []
    
    def getDagDisplayText(self):
        return self.__class__.__name__
        
    def isTerminator(self):
        return False
    
    def isBranch(self):
        return len(self.getSuccessors()) > 0
    
    def getSuccessors(self):
        return self.successors
        
    def swapSuccessor(self,old,new):
        for k,v in enumerate(self.successors):
            if v is old:
                self.successors[k] = new
    
    def readsMem(self):
        return False
    
    def writesMem(self):
        return False
        
    def isMD(self):
        return False
        

class Binop(Instruction):
    def __init__(self,op,res,l,r):
        Instruction.__init__(self)
        self.op = op
        self.assigned = [res]
        self.read = [l,r]
    
    def getDagDisplayText(self):
        return self.op.replace(">","GT").replace("<","LT")
    
    def __repr__(self):
        
        return "%s = %s %s %s"%(self.assigned[0],self.read[0],self.op,
                                    self.read[1])

class Call(Instruction):
    def __repr__(self):
        return "call"

class LoadGlobalAddr(Instruction):
    def __init__(self,res,sym):
        Instruction.__init__(self)
        self.sym = sym
        self.assigned = [res]
    def __repr__(self):
        return "%s = LoadGlobalAddr %s" % (self.assigned[0],self.sym.name)


class LoadParamAddr(Instruction):
    def __init__(self,res,sym):
        Instruction.__init__(self)
        self.sym = sym
        self.assigned = [res]
    def __repr__(self):
        return "%s = LoadParamAddr %s" % (self.assigned[0],self.sym.name)

class LoadLocalAddr(Instruction):
    def __init__(self,res,sym):
        Instruction.__init__(self)
        self.assigned = [res]
        self.sym = sym
    def __repr__(self):
        return "%s = LoadLocalAddr %s" % (self.assigned[0],self.sym.name)
        
        
class LoadConstant(Instruction):
    def __init__(self,res,const):
        Instruction.__init__(self)
        self.assigned = [res]
        self.const = const
    def __repr__(self):
        return "%s = LoadConstant %s" % (self.assigned[0],self.const)
        
class Deref(Instruction):
    def __init__(self,out,p):
        Instruction.__init__(self)
        self.assigned = [out]
        self.read = [p]
    def __repr__(self):
        return "%s = *%s"%(self.assigned[0],self.read[0])
    
    def readsMem(self):
        return True
    
class Store(Instruction):
    def __init__(self,p,val):
        Instruction.__init__(self)
        self.read = [p,val]
    
    def __repr__(self):
        return "*%s = %s"%(self.read[0],self.read[1])
    
    def writesMem(self):
        return True
        
class Terminator(Instruction):
    def isTerminator(self):
        return True
        
class Ret(Terminator):
    def __init__(self,v):
        Terminator.__init__(self)
        self.read = [v]
    
    def __repr__(self):
        return "ret %s" % self.read[0]
    
        
class Branch(Terminator):
    def __init__(self,v,t,f):
        Terminator.__init__(self)
        self.read = [v]
        self.successors = [t,f]
        
    def __repr__(self):
        return "if %s goto %s else %s" %(self.read[0],self.successors[0],self.successors[1])
    
        
class Jmp(Terminator):
    def __init__(self,dest):
        Terminator.__init__(self)
        self.successors = [dest]
        
    def __repr__(self):
        return "jmp %s" % self.successors[0]
        
class Identity(Instruction):
    def __init__(self,v):
        Instruction.__init__(self)
        self.read = []
        self.assigned = [v]

class Move(Instruction):
    def __init__(self,l,r):
        Instruction.__init__(self)
        self.read = [r]
        self.assigned = [l]
        
    def __repr__(self):
        return "%s = Move %s" % (self.assigned[0],self.read[0])
