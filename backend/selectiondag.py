import ir
import itertools

class Identity(ir.Instruction):
    def __init__(self,v):
        ir.Instruction.__init__(self)
        self.assigned = [v]

class LiveOut(ir.Instruction):
    pass

class Node(object):

    def __init__(self,instr):
        self.children = []
        self.control = []
        self.parents = []
        self.instr = instr
    
    def sanityCheck(self):
        #we have no more child inputs than what we read
        assert(len(self.children) == len(self.instr.read))
        
        for inidx,childpair in enumerate(self.children):
            outidx,child = childpair
            #assert consistency in child outputs and our inputs
            assert(child.instr.assigned[outidx] == self.instr.read[inidx])
            
        for parent in self.parents:
            assert(self in map(lambda x : x[1],parent.children))
    

class SelectionDag(object):
    
    #this relies on SSA form to create a DAG
    def __init__(self,block,liveout):
        
        var2node = {}
        
        nodes = []
        
        lastmemaccess = None
        
        for instr in block:
            node = Node(instr)
            
            if node.instr.writesMem() or node.instr.readsMem():
                if lastmemaccess != None:
                    node.control.append(lastmemaccess)
                lastmemaccess = node

            nodes.append(node)
            for v in instr.read:
                if v not in var2node:
                    identnode = Node(Identity(v))
                    nodes.insert(0,identnode)
                    node.children.append((0,identnode))
                else:
                    node.children.append(var2node[v])
            #print instr
            #print instr.assigned
            for idx,v in enumerate(instr.assigned):
                if v in var2node.keys():
                    raise Exception("block not in SSA")
                var2node[v] = (idx,node)
        #assume any unread vars are liveout
        unread = []
        for v in var2node:
            read = False
            for instr in block:
                if v in instr.read:
                    read = True
                    break 
            if read == False:
                unread.append(v)
        liveout.update(unread)
        
        if len(liveout):
            node = Node(LiveOut())
            for v in liveout:
                node.instr.read.append(v)
                node.children.append(var2node[v])
            nodes.insert(-1,node)
        
            if nodes[-2] not in nodes[-1].control:
                nodes[-1].control.append(nodes[-2])
        
        for n in nodes[:-1]:
            if type(n.instr) == ir.Store:
                nodes[-1].control.append(n)
        
        self.root = nodes[-1]
        
        self._setParents()
        
    
    #set all the parents
    def _setParents(self):
        nodes = self.nodes
        
        for n in nodes:
            n.parents = []
        
        for n in nodes:
            for inidx,childpair in enumerate(n.children):
                outidx,child = childpair
                child.parents.append(n)
        
    
    @property
    def nodes(self):
        return self.ordered()
    
    def ordered(self):
        ret = []
        self._ordered(set(),ret,self.root)
        return ret
        
    def _ordered(self,visited,ret,node):
        
        if node in visited:
            return
        visited.add(node)

        for child in node.control:
            self._ordered(visited,ret,child)
        
        for idx,child in node.children:
            self._ordered(visited,ret,child)
        
        ret.append(node)
        
    
    def sanityCheck(self):
        nodes = self.ordered()
        for n in nodes:
            n.sanityCheck()
            
    
    
    
        
