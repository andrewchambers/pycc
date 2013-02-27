
from pyswip.prolog import Prolog



class InterferenceGraph(object):
    
    def __init__(self,function):
        
        interference = {}
        
        prologmap = {}
        varmap = {}
        added = set()
        
        bcount = 0
        icount = 0
        vcount = 0
        
        prolog = Prolog()
        
        for block in function:
            if block not in added:
                prologmap["b%d"%bcount] = block
                varmap[block] = "b%d"%bcount
                added.add(block)
                bcount += 1
            
            for instr in block:
                if instr not in added:
                    prologmap["i%d"%icount] = instr
                    varmap[instr] = "i%d"%icount
                    added.add(instr)
                    icount += 1
                
                for v in instr.read:
                    interference[v] = set([])
                    if v not in added:
                        prologmap["v%d"%vcount] = v
                        varmap[v] = "v%d"%vcount
                        added.add(v)
                        vcount += 1
                    
                for v in instr.assigned:
                    interference[v] = set([])
                    if v not in added:
                        prologmap["v%d"%vcount] = v
                        varmap[v] = "v%d"%vcount
                        added.add(v)
                        vcount += 1
        
        for block in function:
            prevInstr = None
            for instr in block:
                for r in instr.read:
                    print("reads(%s,%s)"%(varmap[instr],varmap[r]))
                    prolog.assertz("reads(%s,%s)"%(varmap[instr],varmap[r]))
                for a in instr.assigned:
                    print("writes(%s,%s)"%(varmap[instr],varmap[a]))
                    prolog.assertz("writes(%s,%s)"%(varmap[instr],varmap[a]))
                prolog.assertz("blockcontains(%s,%s)"%(varmap[block],varmap[instr]))
                if prevInstr != None:
                    print("nextinstr(%s,%s)"%(varmap[prevInstr],varmap[instr]))
                    prolog.assertz("nextinstr(%s,%s)"%(varmap[prevInstr],varmap[instr]))
                for successor in instr.getSuccessors():
                    print("nextinstr(%s,%s)"%(varmap[instr],varmap[successor[0]]))
                    prolog.assertz("nextinstr(%s,%s)"%(varmap[instr],varmap[successor[0]]))
                prevInstr = instr
        
        prolog.consult("interference.pl")
        
        for ans in prolog.query("interferes(X,Y)"):
            interference[prologmap[ans["X"]]].add(prologmap[ans["Y"]])
        
        self.interference = interference
