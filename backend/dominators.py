

#XXX this can be optmised alot, we are currently using 
#pretty naive methods with no memoization

class DominatorInfo(object):
    
    def __init__(self,f):
        
        
        dominators = {}
        
        predecessors = {}
        
        for block in f:
            predecessors[block] = set()
        
        for block in f:
            for successor in block.getSuccessors():
                predecessors[successor].add(block)
        
        dominators[f.entry] = set([f.entry])
        
        allnodes = set(f)
        allnodeswithentry = allnodes.copy()
        allnodes.discard(f.entry)
        for node in allnodes:
            dominators[node] = allnodeswithentry
        
        dominators[f.entry] = set([f.entry])
        
        redo = True
        while redo:
            redo = False
            for node in allnodes:
                print "XXX",node
                preddominatorsets = map(lambda pred : dominators[pred],predecessors[node])
                print "intersection of",preddominatorsets
                newdomset = set.intersection(*preddominatorsets)
                newdomset.add(node)
                if newdomset != dominators[node]:
                    print "change!",newdomset
                    dominators[node] = newdomset
                    redo = True
            
        
        self.predecessors = predecessors
        self.dominators = dominators
        self.blocks = list(f)
        
    def getDominators(self,block):
        return self.dominators[block]
    
    #does b1 dominate b2?
    def dominates(self,b1,b2):
        return b1 in self.dominators[b2]
        
    def getImmediateDominator(self,block):
        dominators = self.getDominators(block)
        for dom in dominators:
            isIdom = True
            for other in dominators:
                if other == dom:
                    continue
                if self.dominates(dom,other) and other != block:
                    isIdom = False
                    break
            if isIdom and dom != block:
                return dom
        return None
    
    def getDominanceFrontier(self,block):
        return self.getDominanceFrontiers()[block]
    
    def getDominanceFrontiers(self):
        
        dfs = {}
        
        for block in self.blocks:
            dfs[block] = set()
        
        for block in self.blocks:
            preds = self.predecessors[block]
            if len(preds) >= 2:
                for p in preds:
                    runner = p
                    idom = self.getImmediateDominator(block)
                    while runner != idom:
                        dfs[runner].add(block)
                        runner = self.getImmediateDominator(runner)
        return dfs
        
    def getDominatorTree(self):
        
        ret = {}
        
        for block in self.blocks:
            idom = self.getImmediateDominator(block)
            if idom == None:
                ret['root'] = block
            else:
                if idom not in ret:
                    ret[idom] = set()
                ret[idom].add(block)
        return ret
    
