from backend import ir
from vis import dagvis


class InstructionSelector(object):
    
    def select(self,target,dag):
        
        instr = target.getMatchableInstructions()
        unmatchable = set()
        while True:
            nodes = dag.ordered()
            n = nodes.pop()
            #print("finding a matchable node")
            while n in unmatchable or n.instr.isMD():
                if not len(nodes):
                    #print("cant match any more")
                    return
                n = nodes.pop()
            
            #print("trying to match <<%s>>"%n.instr)
            matched = False
            for i in instr:
                #print("matching against %s"%i)
                if i.match(n):
                    inst = i(n)
                    i.replace(n,inst)
                    #print("match succeeeded")
                    matched = True
                    break
            if not matched:
                #print "match failed!"
                unmatchable.add(n)
        
        dag.sanityCheck()
            
            
    

