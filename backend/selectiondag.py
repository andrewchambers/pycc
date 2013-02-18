import ir


class SDNode(object):
    
    def __init__(self,instr):
        self.instr = instr
        self.ins = []
        self.outs = []
        self.control = []


class SelectionDag(object):
    
    def __init__(self,block):
        
        nodes = []
        
        for i in block:
            nodes.append(SDNode(i))
        
        creator = {}
        users = {}
        
        for n in nodes:
            instr = n.instr
            for v in instr.assigned:
                creator[v] = n
            
            for v in instr.read:
                if v not in users:
                    users[v] = []
                users[v].append(n)
        
        for n in nodes:
            for v in n.instr.assigned:
                n.outs = users[v]
                for node in users[v]:
                    node.ins.append(n)
        
        lastWrite = None
        
        for n in nodes:
            if n.instr.writesMem():
                lastWrite = n
            if n.instr.readsMem():
                if lastWrite != None:
                    lastWrite.control.append(n)
        
        for n in nodes[:-1]:
            if len(n.outs) == 0 and len(n.control) == 0:
                n.control.append(nodes[-1])
        
        self.nodes = nodes
    
    def topological(self):
        s = []
        toprocess = [n for n in self.nodes]
        while len(toprocess):
            n = toprocess.pop()
            match = True
            for other in self.nodes:
                if other in s:
                    continue
                if n in other.outs or n in other.control:
                    match = False
                    toprocess.insert(0,n)
                    break
                
            if match:
                s.append(n)
        return s

