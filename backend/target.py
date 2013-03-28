

class Target(object):
    
    def translate(self,args,module,ofile):
        
        self.args = args
        for f in module:
            self.translateFunction(f,ofile)
    
    def translateFunction(self,f,ofile):
        pass
