import itertools

import function


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
            else:
                print("failed to")
        
        for b in f:
            for i in b:
                for v in allocations:
                    i.swapVar(v,allocations[v])
        
        self.spill(f,ig)
    
    def spill(self,f,ig):
        
        tospillSet = set()
        varToSlotMapping = {}
        
        #collect all virtual registers that have not been allocated
        for b in f:
            for instr in b:
                tospill = filter(lambda x : x.isPhysical() == False, itertools.chain(instr.read,instr.assigned))
                map(lambda x : tospillSet.add(x),tospill)
        
        if len(tospillSet):
            print "XXXXXXXXXXXXXXXXXXXXXXXXXX"
            for v in tospillSet:
                #XXX get the correct size...
                varslot = f.createAndAddSpillSlot(4)
                backupslot = f.createAndAddSpillSlot(4)
                varToSlotMapping[v] = [varslot,backupslot]
            
            for b in f:
                idx = 0
                while idx < len(b):
                    instr = b[idx]
                    before = []
                    after = []
                    readVirts = filter(lambda x : x.isPhysical() == False, instr.read)
                    assignedVirts = filter(lambda x : x.isPhysical() == False, instr.assigned)
                    allocated = set(filter(lambda x : x.isPhysical(), instr.read))
                    
                    for virt in readVirts:
                        varSlot,backupSlot = varToSlotMapping[virt]
                        reg = (set(self.target.getPossibleRegisters(virt)) - allocated).pop()
                        print "spilling: %s to %s" % (virt,reg)
                        instr.swapVar(virt,reg)
                        before.append(self.target.getSaveRegisterInstruction(reg,backupSlot))
                        before.append(self.target.getLoadRegisterInstruction(reg,varSlot))
                        after.append(self.target.getLoadRegisterInstruction(reg,backupSlot))
                    
                    for virt in assignedVirts:
                        varSlot,backupSlot = varToSlotMapping[virt]
                        reg = (set(self.target.getPossibleRegisters(virt)) - allocated).pop()
                        instr.swapVar(virt,reg)
                        before.append(self.target.getSaveRegisterInstruction(reg,backupSlot))
                        after.append(self.target.getSaveRegisterInstruction(reg,varSlot))
                        after.append(self.target.getLoadRegisterInstruction(reg,backupSlot))
                    
                    for spillinstr in before:
                        b.insert(idx,spillinstr)
                        idx += 1
                    
                    for spillinstr in after:
                        b.insert(idx + 1,spillinstr)
                        idx += 1
                    
                    
                    idx += 1

        
        
        
        
        

