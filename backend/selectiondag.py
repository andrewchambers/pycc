import ir
import itertools


class SDNode(object):
    
    def __init__(self,instr):
        self.instr = instr
        self.ins = []
        self.outs = []


class SelectionDag(object):
    
    
    def recalculateEdges(self):
        
        creators = {}
        users = {}
        
        nodes = []
        edges = []
        controledges = []
        
        for i in self.nodes:
            nodes.append(i)
            for v in i.read:
                if not v in users:
                    users[v] = set()
                users[v].add(i)
        
        
        for i in self.nodes:
            for v in i.assigned:
                creators[v] = i
        
        alreadypresent = set(users.keys()) - set(creators.keys())
        
        
        for v in alreadypresent:
            i = ir.Identity(v)
            creators[v] = i
            nodes.insert(0,i)
        
        for k in users:
            for u in users[k]:
                edges.append([creators[k],u])
        
        lastMemWrite = None
        
        for i in self.nodes:
            if i.readsMem():
                if lastMemWrite != None:
                    controledges.append([lastMemWrite,i])
            
            if i.writesMem():
                lastMemWrite = i
        
        
        for n in nodes[:-1]:
            if len(n.assigned) == 0:
                controledges.append([n,nodes[-1]])
                continue
            for v in n.assigned:
                if len(users[v]) == 0:
                    controledges.append([n,nodes[-1]])
                    break
        
        
        self.nodes = nodes
        self.edges = edges
        self.controledges = controledges
    
    def __init__(self,block):
        
        self.nodes = []
        
        for i in block:
            self.nodes.append(i)
        self.recalculateEdges()
    
    def getCreatorNode(self,var):
        for e in self.edges:
            if e[2] == var:
                return e[0]
    
    def removeNodes(self,nodes):
        self.nodes = [x for x in self.nodes if x not in nodes]
    
    def addNodes(self,nodes):
        self.nodes = nodes + self.nodes
    
    def topological(self):
        
        alledges = self.edges + self.controledges
        s = []
        toprocess = [n for n in self.nodes]
        
        
        while len(toprocess):
            n = toprocess.pop()
            match = True
            for e in alledges:
                if n == e[1]: #node has dependencies
                    toprocess.insert(0,n)
                    match = False
                    break
            if match:
                s.append(n)
                alledges = [e for e in alledges if e[0] != n]
        return s
