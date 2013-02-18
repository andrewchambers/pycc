from backend import ir
from vis import dagvis

class InstructionMatch(object):
    
    def __init__(self,new,remove,count):
        self.remove = remove
        self.new = new
        self.count = count
    
    def __len__(self):
        return self.count


class InstructionSelector(object):
    
    def select(self,target,dag):
        
        instr = target.getInstructions()
        unmatchable = set()
        while True:
            print("topological sort")
            dagvis.showSelDAG(dag)
            nodes = dag.topological()
            matches = []
            
            n = nodes.pop()
            print("finding a matchable node")
            while n in unmatchable or n.isMD():
                if not len(nodes):
                    return
                n = nodes.pop()
            
            print("trying to match <<%s>>"%n)
            
            for i in instr:
                m = i.match(n)
                if m != None:
                    matches.append(m)
            
            if len(matches) == 0:
                print("unmatchable")
                unmatchable.add(n)
                continue
                
            maxmatch = max(matches)
            print("found a match")
            dag.removeNodes(maxmatch.remove)
            dag.addNodes(maxmatch.new)
            dag.recalculateEdges()
            
    













