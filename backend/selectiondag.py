import ir

class SelectionDag(object):
    
    def __init__(self,block):
        
        creators = {}
        users = {}
        
        nodes = []
        edges = []
        controledges = []
        
        for i in block:
            nodes.append(i)
            for v in i.read:
                if not v in users:
                    users[v] = set()
                users[v].add(i)
        
        for i in block:
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
        
        for i in block:
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
