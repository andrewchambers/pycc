

class Module(object):
    def __init__(self):
        self.data = []
        self.functions = []
        self.dataLabelCounter = 0
    
    def _getNewDataLabel(self):
        self.dataLabelCounter += 1
        return "._data%d" % self.dataLabelCounter
    
    def addFunction(self,f):
        self.functions.append(f)
    
    def __iter__(self):
        return self.functions.__iter__()
    
    def addString(self,s):
        label = self._getNewDataLabel()
        self.data.append([label,s])
        return label
