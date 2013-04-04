import itertools



class RegisterAllocator(object):
    
    def __init__(self,tgt):
        self.target = tgt
    
    def allocate(self,f,ig):
        
        allocations = {}
        nodes = list(ig.nodes)
        degrees = {}
        
        
        for v in nodes:
            degree = 0
            for edge in ig.interference:
                if v in edge:
                    degree += 1
            degrees[v] = degree
        
        nodes.sort(key=lambda n : degrees[n])
        
        for n in nodes:
            if n.isPhysical():
                continue
            interferes = ig.getInterferes(n)
            interferes = set([allocations.get(x,x) for x in interferes ])
            possibleregs = self.target.getPossibleRegisters(n)
            possibleregs = filter(lambda x : x not in interferes ,possibleregs )
            
            if len(possibleregs):
                
                movecount = -1
                chosenreg = None
                
                for reg in possibleregs:
                    print("testing reg %s for position %s"%(reg,n))
                    newmovecount = 0
                    for mvedge in ig.moveedges:
                        if n in mvedge:
                            for v in mvedge:
                                if v != n:
                                    if v.isPhysical() and v == reg:
                                        newmovecount += 1
                                    elif allocations.get(v,None) == reg:
                                        newmovecount += 1
                                    break
                            
                    
                    if newmovecount > movecount:
                        print("reg %s is better than %s" % (reg,chosenreg))
                        movecount = newmovecount
                        chosenreg = reg
                
                allocations[n] = chosenreg
        
        
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
                    
                    
                
