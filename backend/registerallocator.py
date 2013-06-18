import itertools

import function
import interference
from vis import interferencevis
from vis import irvis

#Refactor, make smaller
class RegisterAllocator(object):
    
    def __init__(self,tgt):
        self.target = tgt
    

    
    def allocate(self,f):
        
        while True:
            ig = self.build(f)
            if self.coalesce(f,ig):
                continue
            
            #interferencevis.showInterferenceGraph(ig)
            
            var = self.color(f,ig)
            if var != None:
                print("REGISTER ALLOCATOR:  spilling ",var)
                self.spill(f,var)
                continue
            
            break
        
    
    def build(self,f):
        return interference.InterferenceGraph(f)
    
    def coalesce(self,f,ig):
        for b in f:
            for instr in b:
                if instr.isMove():
                    r1,r2 = instr.read[0],instr.assigned[0]
                    if r1.isPhysical() == False:
                        if r1 != r2:
                            if r2 not in ig.getInterferes(r1):
                                print 'REGISTER ALLOCATOR: coalacing',r1,r2
                                self.replace(f,r1,r2)
                                return True
        return False
        
    def color(self,f,ig):
        
        stack = []
        coloring = {}
        tocolor = filter(lambda x : not x.isPhysical(), f.variables)
        tocolor = sorted(tocolor,key= lambda x : -len(ig.getInterferes(x)))
        removed = set()
        #XXX
        for v in tocolor:
            print "REGISTER ALLOCATOR: ",v
            interference = ig.getInterferes(v)
            interference = [x for x in interference if x.isPhysical()] + [coloring[x] for x in interference if x in coloring]
            interference = set(interference)
            possibleRegs = self.target.getPossibleRegisters(v)
            possibleRegs = set(possibleRegs) - interference
            overlappingRegSets = map(lambda x : self.target.getInterferenceSet(x),interference)
            overlappingRegs = set()
            for rs in overlappingRegSets:
                overlappingRegs.update(rs)
            
            possibleRegs = set(possibleRegs) - overlappingRegs
            
            print "REGISTER ALLOCATOR: Interference -> ",interference
            print "REGISTER ALLOCATOR: overlapping regs ", overlappingRegs
            print "REGISTER ALLOCATOR: possible regs ",possibleRegs
            print "REGISTER LLOCATOR: interferes ", ig.getInterferes(v)
            
            if len(possibleRegs) == 0:
                return tocolor[0]
            coloring[v] = sorted(possibleRegs,key = lambda x : x.name)[0]
            print "chose",coloring[v]
        
        print coloring
        self.applyColoring(f,coloring)
        return None
    
    def verifyColoring(self,f,coloring):
        ig = self.build(f)
        for v in f.variables:
            if v.isPhysical() == False:
                assert(v in coloring)
            
        for v in f.variables:
            if v.isPhysical() == False:
                for other in ig.getInterferes(v):
                    if other.isPhysical():
                        otherphys = other
                    else:
                        otherphys = coloring[other]
                    assert(coloring[v] != otherphys)
                    print v,coloring[v]
                    print otherphys,self.target.getInterferenceSet(coloring[v])
                    assert(otherphys not in self.target.getInterferenceSet(coloring[v]))
    
    def applyColoring(self,f,coloring):
        self.verifyColoring(f,coloring)
        for b in f:
            for instr in b:
                for k in coloring:
                    instr.swapVar(k,coloring[k])
    
    #replace r1 with r2 in func f
    def replace(self,f,r1,r2):                
        for b in f:
            for instr in b:
                instr.swapVar(r1,r2)
        
    def spill(self,f,virt):
        #irvis.showFunction(f)
        #XXX get the correct size...
        varSlot = f.createAndAddSpillSlot(4)

        
        for b in f:
            idx = 0
            while idx < len(b):
                instr = b[idx]
                before = []
                after = []
                #print virt.__class__
                if virt in instr.read and virt in instr.assigned:
                    replacement = virt.__class__()
                    before.append(self.target.getLoadRegisterInstruction(replacement,varSlot))
                    after.append(self.target.getSaveRegisterInstruction(replacement,varSlot))
                    instr.swapVar(virt,replacement)
                elif virt in instr.read:
                    #print instr
                    replacement = virt.__class__()
                    before.append(self.target.getLoadRegisterInstruction(replacement,varSlot))
                    instr.swapVar(virt,replacement)
                elif virt in instr.assigned:
                    replacement = virt.__class__()
                    after.append(self.target.getSaveRegisterInstruction(replacement,varSlot))
                    instr.swapVar(virt,replacement)
                
                for spillinstr in before:
                    b.insert(idx,spillinstr)
                    idx += 1
                
                for spillinstr in after:
                    b.insert(idx + 1,spillinstr)
                    idx += 1
                
                
                idx += 1

        #irvis.showFunction(f)
        
        
        
        

