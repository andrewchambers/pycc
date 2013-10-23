


# XXX the data needs to be completely reworked to match the C data and const initializers
# things like label + constant and other considerations


class Module(object):
    def __init__(self):
        #array of [labels],content
        self.rwdata = []
        self.rodata = []
        #zeroed data
        #array of [labels],lengths
        self.rwzdata = []
        
        self.functionDict = {}
        self.functions = []
        self.dataLabelCounter = 0
    
    #packs similar constant strings
    #together, shifts data that is all null to
    #zero section
    def packData(self):
        #first migrate all zeroed data to zero sections
        newrwdata = []
        for labels,data in self.rwdata:
            if data == len(data) * '\x00':
                self.rwzdata.append([labels,len(data)])
            else:
                newrwdata.append([labels,data])
        self.rwdata = newrwdata
        
        #pack ro section
        #first sort them by the data array
        self.rodata.sort(key=lambda x : x[1])
        i = 0
        while i + 1 < len(self.rodata):
            if self.rodata[i][1]  == self.rodata[i+1][1]:
                #merge labels that have the same data
                self.rodata[i][0] += self.rodata[i+1][0]
                del self.rodata[i+1]
                continue
            i += 1
            
                    
        
        
    def _getNewDataLabel(self):
        self.dataLabelCounter += 1
        return "._data%d" % self.dataLabelCounter
    
    def addFunction(self,f):
        self.functions.append(f)
        if f.name in self.functionDict:
            raise RuntimeError("Multiple functions called %s"
                                " being added to module"%f.name)
        self.functionDict[f.name] = f
        
    def getFunction(self,name):
        return self.functionDict.get(name,None)
    
    def __iter__(self):
        return self.functions.__iter__()
    
    #add data to section
    def addZeroInitData(self,sz,label=None):
        if label == None:
            label = self._getNewDataLabel()
        self.rwzdata.append([[label],sz])
        return label
        
    def addReadOnlyData(self,d,label=None):
        if label == None:
            label = self._getNewDataLabel()
        self.rodata.append([[label],d])
        return label
        
    def addReadWriteData(self,d,label=None):
        if label == None:
            label = self._getNewDataLabel()
        self.rwdata.append([[label],d])
        return label
        
