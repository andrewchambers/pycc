from backend import ir
from vis import dagvis

class InstructionMatch(object):
    
    def __init__(self,repl,count):
        self.repl = repl
        self.count = count
    
    def __len__(self):
        return self.count
        
    def replace(self):
        self.repl()


class InstructionSelector(object):
    
    def select(self,target,dag):
        
        instr = target.getInstructions()
        unmatchable = set()
        while True:
            print("topological sort")
            nodes = dag.ordered()
            matches = []
            n = nodes.pop()
            print("finding a matchable node")
            while n in unmatchable or n.instr.isMD():
                if not len(nodes):
                    print("cant match any more")
                    return
                n = nodes.pop()
            
            print("trying to match <<%s>>"%n)
            
            for i in instr:
                m = i.match(dag,n)
                if m != None:
                    matches.append(m)
            
            if len(matches) == 0:
                print("unmatchable")
                unmatchable.add(n)
                continue
                
            maxmatch = max(matches)
            print("found a match")
            maxmatch.replace()
            
    

