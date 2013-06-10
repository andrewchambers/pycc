

counter = 0

class VirtualRegister(object):
    
    def __init__(self):
        global counter
        counter += 1
        self.name = "v%d"%counter
    
    def isPhysical(self):
        return False
    
    def __repr__(self):
        tstr = "%s" % self.__class__.__name__
        return "(%s) %s" %(tstr,self.name)
    
    def getSize(self):
        raise Exception("no size avaliable")
    
class I32(VirtualRegister):
    
    def getSize(self):
        return 4

class I8(VirtualRegister):
    
    def getSize(self):
        return 1

class Pointer(VirtualRegister):
    
    def getSize(self):
        return 4

class Constant(object):
    def __repr__(self):
        return "%s"%self.value

class ConstantI32(Constant):
    def __init__(self,v):
        self.value = int(v)

class ConstantI8(Constant):
    def __init__(self,v):
        self.value = int(v)
    

class Instruction(object):
    
    def __init__(self):
        self.assigned = []
        self.read = []
        self.successors = []
        
    def getTemplateLookupStr(self):
        classname = self.__class__.__name__
        try:
            op = self.op
        except:
            op = ''
        
        ass = reduce(lambda x,y : x + y.__class__.__name__,self.assigned,'')
        read = reduce(lambda x,y : x + y.__class__.__name__,self.read,'')
        ret = classname + ' ' + op + ' ' + ass
        if len(read) != 0:
            ret +=  "_" + read
        return ret
        
    def getDagDisplayText(self):
        return self.__class__.__name__
        
    def isTerminator(self):
        return False
    
    def isBranch(self):
        return len(self.getSuccessors()) > 0
    
    def swapVar(self,old,new):
        for arr in [self.read,self.assigned]:
            for k,v in enumerate(arr):
                if v is old:
                    arr[k] = new
    
    def swapRead(self,old,new):
        for k,v in enumerate(self.read):
            if v is old:
                self.read[k] = new
                    
    def swapAssigned(self,old,new):
        for k,v in enumerate(self.assigned):
            if v is old:
                self.assigned[k] = new
    
    
    def asm(self):
        return "#%s" % str(self)
    
    def getSuccessors(self):
        return self.successors
        
    def setSuccessors(self,new):
        self.successors = new
        
    def swapSuccessor(self,old,new):
        for k,v in enumerate(self.successors):
            if v is old:
                self.successors[k] = new
    
    def readsMem(self):
        return False
    
    def writesMem(self):
        return False
    
    #is Machine Dependant, i.e. Not an ir instruction
    def isMD(self):
        return False
    
    def isMove(self):
        return False
    
    def isCall(self):
        return False
    
    #these registers are clobbered after they are used as input
    
    def getClobberedRegisters(self):
        return []
    
    #these registers are clobbered before they can be used as input
    
    def getPreClobberedRegisters(self):
        return []

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

class Unop(Instruction):
    def __init__(self,op,res,arg):
        self.op = op
        self.assigned = [res]
        self.read = [arg]
    
    def __repr__(self):
        return "%s = %s %s"%(self.assigned[0],self.op,self.read[0])

class Call(Instruction):
    def __init__(self,label):
        Instruction.__init__(self)
        self.label = label
        
    def __repr__(self):
        return "%s = call %s %s"%(self.assigned[0],self.label,self.read)

    def isCall(self):
        return True
        
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
        if self.sym.slot.offset == None:
            offset = self.sym.name
        else:
            offset = self.sym.slot.offset
            
        return "%s = LoadLocalAddr %s" % (self.assigned[0],offset)
    
    def getSlot(self):
        return self.sym.slot
    
        
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
    def __init__(self,v=None):
        Terminator.__init__(self)
        if v != None:
            self.read = [v]
        else:
            self.read = []
    
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
        self.assigned = [v]

class Phi(Instruction):
    def __init__(self,lhs,args):
        Instruction.__init__(self)
        args = list(args)
        self.read = []
        self.blocks = []
        for v,block in args:
            self.read.append(v)
            self.blocks.append(block)
        self.assigned = [lhs]
    
    def __repr__(self):
        return "%s = Phi %s" % (self.assigned[0], zip(self.read,self.blocks))

class Move(Instruction):
    def __init__(self,l,r):
        Instruction.__init__(self)
        self.read = [r]
        self.assigned = [l]
    
    def isMove(self):
        return True
    
    def __repr__(self):
        return "%s = Move %s" % (self.assigned[0],self.read[0])
