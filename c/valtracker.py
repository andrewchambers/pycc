
import types
from backend import ir



class ValTracker(object):
    def __init__(self,lval,t,reg):
        self.lval =  lval
        self.type = t
        self.reg = reg
    
    def clone(self):
        newType = self.type.clone()
        return ValTracker(self.lval,newType,newType.createVirtualReg())
    
    def deref(self):
        if type(self.type) != types.Pointer and not self.lval:
            raise Exception("cannot deref non pointer")
        
        ret = self.clone()
        ret.lval = False
        
        if not self.lval:
            ret.type = ret.type.type
        
        ret.createVirtualReg()
        
        return ret

    def index(self):
        
        if type(self.type) != types.Array and not self.lval:
            raise Exception("index non array")
        
        ret = self.clone()
        
        ret.type = ret.type.type
        
        ret.lval = True
        
        ret.createVirtualReg()
        
        return ret

    def addressOf(self):
        ret = self.clone()
        ret.type = types.Pointer(ret.type)
        return ret
    
    
    def createVirtualReg(self):
        if self.lval:
            self.reg = ir.Pointer()
        else:
            self.reg = self.type.createVirtualReg()
