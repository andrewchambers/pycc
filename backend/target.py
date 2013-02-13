

class Target(object):
    
    def translate(self,module,ofile):
        for f in module:
            self.translateFunction(f,ofile)
    
    def translateFunction(self,f,ofile):
        pass
