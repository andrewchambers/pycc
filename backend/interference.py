
import itertools

class InterferenceGraph(object):
    
    def __init__(self,function):
        
        
        blocklist = [block for block in function]
        
        assigned = set()
        assignedblock = {}
        readinstrs = {}
        
        for b in blocklist:
            for i in b:
                for v in i.read:
                    if not v.isPhysical():
                        if v not in readinstrs:
                            readinstrs[v] = []
                        readinstrs[v].append(i)
                for v in i.assigned:
                    if not v.isPhysical():
                        assigned.add(v)
                        if v in assignedblock and assignedblock[v] != b:
                            raise Exception("Internal bug, non ssa code detected")
                        assignedblock[v] = b
        
        assigned = list(assigned)
        vartoindex = {}
        for k,v in enumerate(assigned):
            vartoindex[v] = k
        
        edges = [ (b,s) for b in blocklist for s in b[-1].getSuccessors() ]
        
        reachability = {}
        for b in blocklist:
            for b2 in blocklist:
                if b not in reachability:
                    reachability[b] = {}
                reachability[b][b2] = [False]*len(assigned)
        
        
        for start,end in edges:
            for index,v in enumerate(assigned):
                if assignedblock[v] == end:
                    reachability[start][end][index] = False
                else:
                    reachability[start][end][index] = True
        
        #this could be a matrix
        #Floyd-Warshall algorithm
        for k in blocklist:
            for i in blocklist:
                for j in blocklist:
                    for index in range(len(assigned)):
                        reachability[i][j][index] = reachability[i][j][index] or (reachability[i][k][index] and reachability[k][j][index])
        
        #print reachability
        
        instrtoblock = {}
        
        for b in blocklist:
            for i in b:
                instrtoblock[i] = b
        
        def instructionReachable(start,end,var):
            if start == end:
                return True
            b1 = instrtoblock[start]
            b2 = instrtoblock[end]
            if b1 == b2:
                reachedstart = False
                for instr in b1:
                    if var in instr.assigned: #can be a precomputer array
                        return False
                    if instr == end:    
                        if not reachedstart:
                            return False
                        else:
                            return True
                    if instr == start:
                        reachedstart = True
            else:
                return reachability[b1][b2][vartoindex[var]]
        
        liveness = {}
        
        for var in assigned:
            for b in blocklist:
                for i in b:
                    liveness[i] = set([])
                    for iread in readinstrs[v]:
                        if instructionReachable(i,iread,var):
                            liveness[i].add(var)
                            break
        for i in liveness:
            print i
            print "\t %s"%liveness[i]
        #self.liveness = liveness
                    
