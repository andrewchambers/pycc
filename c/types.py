
from backend import ir

class Type(object):
    pass

class Pointer(Type):
    def getSize(self):
        return 4
    
    def createVirtualReg(self):
        return ir.Pointer()
    
class Array(Type):
    pass


class Int(Type):
    
    def getSize(self):
        return 4
        
    def createVirtualReg(self):
        return ir.I32()


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
