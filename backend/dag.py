import ir

class DAG(object):
    def __init__(self,block):
        self.nodes = set()
        self.inedges = {}
        self.outedges = {}
        self.initdag(block)
    
    def getNodes(self):
        return self.nodes
        
    def initdag(self,block):
        
        used = set()
        created = set()
        creators = {}
        
        for ins in block:
            self.addNode(ins)
            for v in ins.getAssignedVars():
                created.add(v)
                creators[v] = ins
            for v in ins.getReadVars():
                used.add(v)
            
        needsOriginNode =  used - created
        
        for v in needsOriginNode:
            dummy = ir.Dummy(v)
            self.addNode(dummy)
            creators[v] = ins
        
        for ins in self.getNodes():
            for v in ins.getReadVars():
                ins.addInNode(creators[v])
                creators[v].addOutNode(ins)
        
        
    def addNode(self,n):
        if n in self.nodes:
            raise Exception("node added to DAG twice")
        
        self.nodes.add(n)
        
    def addEdge(n1,n2,data):
        
        self.outedges[n1].append([n2,data])
        self.inedges[n2].append([n1,data])

