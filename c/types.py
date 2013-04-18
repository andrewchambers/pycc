
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


class TypeTable(object):
    
    def __init__(self):
         
         self.types = {}
         self.registerType('int', Int)
    
    def lookupType(self,name):
        
        ret = self.types[name]()
        return ret
        
    def registerType(self,name,t):
        
        if name in self.types:
            raise Exception("type %s already defined!" % name)
        
        self.types[name] = t
