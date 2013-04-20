

class Target(object):
    
    def translate(self,args,module,ofile):
        
        self.args = args
        self.translateModule(module,ofile)
    
    def translateModule(self,module,ofile):
        pass
