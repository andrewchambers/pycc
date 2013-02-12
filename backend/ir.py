
counter = 0

class Variable(object):
    def __init__(self):
        global counter
        counter += 1
        self.name = "v%d"%counter
        self.lval = False
        self.pcount = 0
    def incPCount(self):
        self.pcount += 1
        
    def setPCount(self,count):
        self.pcount = count
    
    def getPCount(self):
        return self.pcount
    
    def isLVal(self):
        return self.lval
    
    def setLVal(self,lval=True):
        self.lval = lval
    def __repr__(self):
        tstr = "%s" % self.__class__.__name__
        if self.lval:
            tstr += " lval"
        stars = "*"* self.pcount
        return "(%s%s) %s" %(stars,tstr,self.name)
    
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
        self._outnodes = []
        self._innodes = []
        self._assigned = []
        self._read = []
    
    def getAssignedVars(self):
        return self._assigned
    
    def getReadVars(self):
        return self._read
    
    def setAssignedVars(self,vs):
        self._assigned = vs
    
    def setReadVars(self,vs):
        self._read = vs
        
    def isTerminator(self):
        return False
    
    def getSuccessors(self):
        return []
    
    def getOutNodes(self):
        return self._outnodes
        
    def getInNodes(self):
        return self._innodes
        
    def addOutNode(self,n):
        self._outnodes.append(n)
        
    def addInNode(self,n):
        self._innodes.append(n)

class Dummy(Instruction):
    def __init__(self,v):
        Instruction.__init__(self)
        self.setAssignedVars([v])

class Binop(Instruction):
    def __init__(self,op,res,l,r):
        Instruction.__init__(self)
        self.op = op
        self.res = res
        self.l = l
        self.r = r
        self.setAssignedVars([res])
        self.setReadVars([l,r])
    def __repr__(self):
        return "%s = %s %s %s"%(self.res,self.l,self.op,self.r)

class LoadGlobal(Instruction):
    def __init__(self,result,sym):
        Instruction.__init__(self)
        self.res = result
        self.sym = sym
        self.setAssignedVars([res])
    def __repr__(self):
        return "%s = LoadGlobal %s" % (self.res,self.sym.name)


class LoadParam(Instruction):
    def __init__(self,result,sym):
        Instruction.__init__(self)
        self.res = result
        self.sym = sym
        self.setAssignedVars([res])
    def __repr__(self):
        return "%s = LoadParam %s" % (self.res,self.sym.name)

class LoadLocal(Instruction):
    def __init__(self,result,sym):
        Instruction.__init__(self)
        self.res = result
        self.sym = sym
    def __repr__(self):
        return "%s = LoadLocal %s" % (self.res,self.sym.name)
        
        
class LoadConstant(Instruction):
    def __init__(self,var,const):
        Instruction.__init__(self)
        self.var = var
        self.const = const
    def __repr__(self):
        return "%s = LoadConstant %s" % (self.var,self.const)
        
class Deref(Instruction):
    def __init__(self,out,p):
        Instruction.__init__(self)
        self.p = p
        self.out = out
    def __repr__(self):
        return "%s = *%s"%(self.out,self.p)
    
class Store(Instruction):
    def __init__(self,p,val):
        Instruction.__init__(self)
        self.p = p
        self.val = val
    
    def __repr__(self):
        return "*%s = %s"%(self.p,self.val)
    
        
class Terminator(Instruction):
    def isTerminator(self):
        return True
        
class Ret(Terminator):
    def __init__(self,v):
        Terminator.__init__(self)
        self.v = v
    
    def __repr__(self):
        return "ret %s" % self.v
    
        
class Branch(Terminator):
    def __init__(self,v,t,f):
        Terminator.__init__(self)
        self.v = v
        self.t = t
        self.f = f
        
    def __repr__(self):
        return "if %s goto %s else %s" %(self.v,self.t,self.f)

    def getSuccessors(self):
        return [self.t,self.f]
    
        
class Jmp(Terminator):
    def __init__(self,dest):
        Terminator.__init__(self)
        self.dest = dest
    
    def __repr__(self):
        return "jmp %s" % self.dest
    
    def getSuccessors(self):
        return [self.dest]
        

class Move(Instruction):
    def __init__(self,l,r):
        Instruction.__init__(self)
        self.l = l
        self.r = r
        
    def __repr__(self):
        return "%s = Move %s" % (self.l,self.r)
        