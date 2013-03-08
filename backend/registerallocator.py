import itertools



class RegisterAllocator(object):
    
    def __init__(self,tgt):
        self.target = tgt
    
    def allocate(self,f,ig):
        
        allocations = {}
        nodes = list(ig.nodes)
        degrees = {}
        
        usedRegisters = set()
        
        for b in f:
            for i in b:
                for v in itertools.chain(i.read,i.assigned):
                    if v.isPhysical():
                        usedRegisters.add(v)
        
        for v in nodes:
            degree = 0
            for edge in ig.interference:
                if v in edge:
                    degree += 1
            degrees[v] = degree
        
        nodes.sort(key=lambda n : degrees[n])
        
        for n in nodes:
            interferes = ig.getInterferes(n)
            interferes = set([allocations.get(x,x) for x in interferes ])
            possibleregs = self.target.getPossibleRegisters(n)
            possibleregs = filter(lambda x : x not in interferes ,possibleregs )
            
            if len(possibleregs):
                
                possibleAndUsed = list(filter(lambda x : x in usedRegisters, possibleregs))
                if len(possibleAndUsed):
                    chosenreg = possibleAndUsed.pop()
                else:
                    chosenreg = possibleregs.pop()
                
                usedRegisters.add(chosenreg)
                allocations[n] = chosenreg
                
                #XXX todo use move edges
                #regcounts = {}
                
                #for reg in possibleregs:
                #    regcounts[reg] = 0
                #    for mvedge in ig.moveedges:
                #        if n in mvedge and :
                #allocations[n] = max(possibleregs,key=lambda r : )
        
        
        for b in f:
            for i in b:
                for v in allocations:
                    i.swapVar(v,allocations[v])
        
        self.spill(f,ig)
    
    def spill(self,f,ig):
        
        for  b in f:
            idx = 0
            while idx != len(b):
                instr = b[idx]
                tospill = filter(lambda x : x.isPhysical() == False, itertools.chain(instr.read,instr.assigned))
                for spillvar in tospill:
                    possible = set(self.target.getPossibleRegisters(spillvar)) - set(instr.read)
                    reg = possible.pop()
                    instr.swapVar(spillvar,reg)
                    print "spilling %s - calc done in %s" %(spillvar,reg)
                    ss1 = None
                    ss2 = None
                    start,end = self.target.getSpillCode(reg,ss1,ss2)
                    b.opcodes = b.opcodes[:idx] + start + [instr] + end + b.opcodes[idx+1:]
                    idx = idx + len(start)
                idx += 1
                    
                    
                
