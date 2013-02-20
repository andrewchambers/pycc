import ir
import weakref




class SDDataEdge(object):
    
    def __init__(self,head,tail):
        
        self._head = head
        self._tail = tail
        self.head.edge = self
        self.tail.addEdge(self)
        self.var = self.tail.var
    
    @property
    def head(self):
        return self._head

    @head.setter
    def head(self, head):
        self.head.var = None
        self._head = head
        self.head.var = self.var
    
    @property
    def tail(self):
        return self._tail

    @tail.setter
    def tail(self, tail):
        self.tail.removeEdge(self)
        self._tail = tail
        self.head._setVar(self.var)
    
    @property
    def var(self):
        return self.tail.var

    @var.setter
    def var(self, var):
        self.head._setVar(var)
        self.tail._setVar(var)
    
    def remove(self):
        self.head.edge = None
        self.tail.removeEdge(self)

class SDInPort(object):
    def __init__(self,parent,idx):
        self.parent = parent
        self.idx = idx
        self._edge = None
    
    def _setVar(self,var):
        self.parent.instr.read[self.idx] = var
    
    @property
    def edge(self):
        return self._edge

    @edge.setter
    def edge(self, edge):
        if edge != None:
            self._setVar(edge.var)
        else:
            self._setVar(None)
        self._edge = edge
    
    @property
    def var(self):
        return self.parent.instr.read[self.idx]

    @var.setter
    def var(self, var):
        #the edge does the real var change
        self.edge.var = var

class SDOutPort(object):
    def __init__(self,parent,idx):
        self.idx = idx
        self.parent = parent
        self._edges = set([])
    
    @property
    def var(self):
        return self.parent.instr.assigned[self.idx]

    def _setVar(self,var):
        self.parent.instr.assigned[self.idx] = var

    @var.setter
    def var(self, var):
        for e in self._edges:
            #the edge does the real var change
            e.var = var
    
    @property
    def edges(self):
        return self._edges

    @edges.setter
    def edges(self, edges):
        raise Exception("error, modify edges via addEdge or removeEdge")
    
    def addEdge(self,edge):
        self._edges.add(edge)
    
    def removeEdge(self,edge):
        self._edges.remove(edge)
    
class SDNode(object):
    
    def __init__(self):
        self.ins = []
        self.outs = []
        self.control = []
        self._instr = None
    
    @property
    def instr(self):
        return self._instr
        
    @instr.setter
    def instr(self, instr):
        
        self._instr = instr
        self.ins = []
        self.outs = []
        self.control = []
        for idx,v in enumerate(instr.assigned):
            self.outs.append(SDOutPort(self,idx))
            
        for idx,v in enumerate(instr.read):
            self.ins.append(SDInPort(self,idx))
        
    
    


class SelectionDag(object):
    
    #this relies on SSA form to create a DAG
    def __init__(self,block):
        
        users = {}
        assigners = {}
        self.nodes = []
        
        lastWrite = None
        
        for instr in block:
            node = SDNode()
            self.nodes.append(node)
            node.instr = instr
        
            for idx,v in enumerate(instr.assigned):
                if v not in assigners:
                    assigners[v] = []
                assigners[v].append([node,idx])
            
        
        for node in self.nodes:
            if node.instr.readsMem():
                if lastWrite != None:
                    node.control.append(lastWrite)
            if node.instr.writesMem():
                lastWrite = node
        
        for node in self.nodes:
            instr = node.instr
            for idx,v in enumerate(instr.read):
                ass = assigners[v]
                if len(ass) != 1:
                    raise Exception("block not in SSA")
                head = node.ins[idx]
                tail = ass[0][0].outs[ass[0][1]]
                SDDataEdge(head,tail)

        for n in self.nodes[:-1]:
            if len(n.outs) == 0:
                n.control.append(self.nodes[-1])
        
        #we dont need order anymore
        self.nodes = set(self.nodes)
    
    
    
    
    def topological(self):
        pass
        #s = []
        #toprocess = [n for n in self.nodes]
        #while len(toprocess):
        #    n = toprocess.pop()
        #    match = True
        #    for other in self.nodes:
        #        if other in s:
        #            continue
        #        if n in other.outs or n in other.control:
        #            match = False
        #            toprocess.insert(0,n)
        #            break
        #        
        #    if match:
        #        s.append(n)
        #return s

