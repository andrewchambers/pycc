
import itertools

class InterferenceGraph(object):
    
    def __init__(self,function):
        
        
        blockstates = {}
        
        #init the gen-kill sets
        for block in function:
            gen = set()
            kill = set()
            for instr in block:
                for v in instr.read:
                    if v not in kill:
                        gen.add(v)
                for v in instr.assigned:
                    kill.add(v)
            blockstates[block] = [gen,kill,set(),set()]
        
        #init the sucessor table
        successors = {}
        for block in function:
            successors[block] = list(block.getReachableBlocks())
        
        changed = True
        while changed:
            changed = False
            for block in blockstates:
                newout = set()
                newin = set()
                blockstate = blockstates[block]
                if len(successors[block]) == 0:
                    newout = set()
                else:
                    for s in successors[block]:
                        newout = newout.union(blockstate[2])
                
                newin = blockstate[0].union(newout - blockstate[1])
                
                if blockstate[2] != newin or blockstate[3] != newout:
                    blockstate[2] = newin
                    blockstate[3] = newout
                    changed = True
                
        liveness = []
        
        for block in blockstates:
            
            live = blockstates[block][3]
            #work backwards from liveout
            for instr in reversed(block):
                
                liveness.append(live.copy())
                
                for v in instr.read:
                    live.add(v)
                
                for v in instr.assigned:
                    if v in live:
                        live.remove(v)
                
        self.nodes = function.variables
        #XXX rename to interference edges
        self.interference = []
        for varset in liveness:
            for edge in itertools.combinations(varset,2):
                edge = set(edge)
                if edge not in self.interference:
                    self.interference.append(edge)
        
        moveedges = []
        
        for b in function:
            for i in b:
                if i.isMove():
                    self.moveedges.append(set([i.assigned[0],i.read[0]]))
        
        self.moveedges = moveedges
    
    def getInterferes(self,n):
        ret = set()
        for edge in self.interference:
            if n in edge:
                new = edge.copy()
                new.remove(n)
                for other in new:
                    ret.add(other)
        return ret
                
                
