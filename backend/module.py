

class Module(object):
    def __init__(self):
        self.data = []
        self.functions = []
    def addFunction(self,f):
        self.functions.append(f)
    def __iter__(self):
        return self.functions.__iter__()