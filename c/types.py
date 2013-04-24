
from backend import ir

class Type(object):
    pass

class Pointer(Type):
    
    def __init__(self,t):
        self.type = t
    
    def getSize(self):
        return 4
    
    def createVirtualReg(self):
        return ir.Pointer()
    
    def clone(self):
        return Pointer(self.type.clone())
    
    
class Array(Type):
    
    def __init__(self,t,length):
        self.type = t
        self.length = length
    
    def getSize(self):
        return self.type.getSize() * self.length
        
    def clone(self):    
        return Array(self.type.clone(),self.length)
        
    def createVirtualReg(self):
        return ir.Pointer()

class Int(Type):
    
    def getSize(self):
        return 4
        
    def createVirtualReg(self):
        return ir.I32()
    
    def clone(self):
        return Int()

class Char(Type):
    def getSize(self):
        return 1
        
    def createVirtualReg(self):
        return ir.I32()
    
    def clone(self):
        return Char()

class Struct(Type):

    def __init__(self,name):
        self.name = name
        self.members = []
    
    def getSize(self):
        size = 0
        for name,t in self.members:
            size += t.getSize()
        return size
    
    def getMemberInfo(self,name):
        
        offset = 0
        
        for memberName,t in self.members:
            if memberName == name:
                return (t,offset)
            offset += t.getSize()
        
        return (None,None)
    
    def addMember(self,name,t):
        self.members.append([name,t])
        
    def clone(self):
        
        ret = Struct(self.name)
        for name,t in self.members:
            ret.addMember(name,t.clone())
        
        return ret
        

class TypeTable(object):
    
    def __init__(self):
         
         self.types = {}
         self.registerType('int', Int())
         self.registerType('char', Char())
    
    def lookupType(self,name):
        
        ret = self.types[name].clone()
        return ret
        
    def registerType(self,name,t):
        
        if name in self.types:
            raise Exception("type %s already defined!" % name)
        
        self.types[name] = t
