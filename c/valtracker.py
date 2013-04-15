



class ValTracker(object):
    def __init__(self,lval,t,reg):
        self.lval =  lval
        self.type = t
        self.reg = reg
    
    def newVal(self):
        newType = self.type.copy()
