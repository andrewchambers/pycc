import itertools

import function
import interference
from vis import interferencevis

#Refactor, make smaller
class RegisterAllocator(object):
    
    def __init__(self,tgt):
        self.target = tgt
    
    def allocate(self,f):
        
        spilled = True
        while spilled:
            spilled = False
            ig = interference.InterferenceGraph(f)
            #interferencevis.showInterferenceGraph(ig)
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
                withRegOverlapInterferes = set()
                for reg in interferes:
                    withRegOverlapInterferes.add(reg)
                    if reg.isPhysical():
                        withRegOverlapInterferes.update(self.target.getInterferenceSet(reg))
                print interferes
                print  withRegOverlapInterferes
                interferes = withRegOverlapInterferes
                possibleregs = self.target.getPossibleRegisters(n)
                possibleregs = filter(lambda x : x not in interferes ,possibleregs )

                if len(possibleregs):
                    possibleregs.sort(key=lambda x : x.name)
                    #print possibleregs
                    allocations[n] = possibleregs.pop()
                else:
                    #print '-----------------'
                    #print allocations
                    #print '-----------------'
                    for b in f:
                        for i in b:
                            for v in allocations:
                                i.swapVar(v,allocations[v])
                    print("failed to allocate a register for %s" % n)
                    self.spill(f,n)
                    spilled = True
                    break
        #print '-----------------'
        #print allocations
        #print '-----------------'
        
        for b in f:
            for i in b:
                for v in allocations:
                    i.swapVar(v,allocations[v])
        
    
    def spill(self,f,virt):

            #XXX get the correct size...
            varSlot = f.createAndAddSpillSlot(4)
            backupSlot = f.createAndAddSpillSlot(4)

            
            for b in f:
                idx = 0
                while idx < len(b):
                    instr = b[idx]
                    before = []
                    after = []
                    
                    allocated = set(filter(lambda x : x.isPhysical(), instr.read + instr.assigned))
                    #XXX these sets have non deterministic iterators
                    
                    
                    if virt in instr.read and virt in instr.assigned:
                        #print instr
                        reg = (set(self.target.getPossibleRegisters(virt)) - allocated).pop()
                        instr.swapVar(virt,reg)
                        before.append(self.target.getSaveRegisterInstruction(reg,backupSlot))
                        before.append(self.target.getLoadRegisterInstruction(reg,varSlot))
                        after.append(self.target.getSaveRegisterInstruction(reg,varSlot))
                        after.append(self.target.getLoadRegisterInstruction(reg,backupSlot))
                    elif virt in instr.read:
                        #print instr
                        reg = (set(self.target.getPossibleRegisters(virt)) - allocated).pop()
                        instr.swapVar(virt,reg)
                        before.append(self.target.getSaveRegisterInstruction(reg,backupSlot))
                        before.append(self.target.getLoadRegisterInstruction(reg,varSlot))
                        after.append(self.target.getLoadRegisterInstruction(reg,backupSlot))
                        allocated.add(reg)
                    elif virt in instr.assigned:
                        #print instr
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

        
        
        
        
        

