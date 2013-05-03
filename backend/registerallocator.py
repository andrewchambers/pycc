import itertools

import function
import interference
from vis import interferencevis


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
            
            print "XXX"
            print "spilling ",virt
            
            for b in f:
                idx = 0
                spilledReg = None
                hasBeenAssigned = False
                
                before = []
                after = []
                print "start of block",b
                #for instrx in b:
                #    print '\t',instrx
                while idx < len(b):
                    instr = b[idx]
                    print instr
                    
                    #print "\tProcessing",instr
                    
                    #spill a reg if we need to , try to keep using it until
                    #another opcode tries to use it, if this happens
                    #we have to restore it
                    
                    if spilledReg:
                        if spilledReg in instr.assigned or spilledReg in instr.read:
                            print("\t\trestoring spilled reg %s" % spilledReg)
                            
                            #XXX if hasBeenAssigned:
                            after.append(self.target.getSaveRegisterInstruction(spilledReg,varSlot))
                            #XXX if spilledReg in instr.read:
                            after.append(self.target.getLoadRegisterInstruction(spilledReg,backupSlot))
                            print "\t\t %s" % after
                            for spillinstr in after:
                                b.insert(idx,spillinstr)
                                idx += 1
                                after = []
                            spilledReg = None
                            hasBeenAssigned = False
                    
                    
                    if spilledReg == None:
                        if virt in instr.read or virt in instr.assigned:
                            #XXX these sets have non deterministic iterators
                            allocated = set(filter(lambda x : x.isPhysical(), instr.read + instr.assigned))
                            spilledReg = (set(self.target.getPossibleRegisters(virt)) - allocated).pop()
                            hasBeenAssigned = False
                            print("\tspilling reg %s" % spilledReg)

                        if virt in instr.read and virt in instr.assigned:
                            #print instr
                            before.append(self.target.getSaveRegisterInstruction(spilledReg,backupSlot))
                            before.append(self.target.getLoadRegisterInstruction(spilledReg,varSlot))
                        elif virt in instr.read:
                            #print instr
                            before.append(self.target.getSaveRegisterInstruction(spilledReg,backupSlot))
                            before.append(self.target.getLoadRegisterInstruction(spilledReg,varSlot))
                        elif virt in instr.assigned:
                            before.append(self.target.getSaveRegisterInstruction(spilledReg,backupSlot))
                        
                        for spillinstr in before:
                            b.insert(idx,spillinstr)
                            idx += 1
                            before = []
                    
                    if virt in instr.assigned:
                        hasBeenAssigned = True
                    
                    if spilledReg != None:
                        instr.swapVar(virt,spilledReg)
                    
                    idx += 1
                
                print("end of block")
                
                #end of block and we have a spilled reg, restore it.
                if spilledReg:
                    print("\t\trestoring spilled reg %s" % spilledReg)
                    
                    #abort now...
                    if hasBeenAssigned:
                        after.append(self.target.getSaveRegisterInstruction(spilledReg,varSlot))
                    after.append(self.target.getLoadRegisterInstruction(spilledReg,backupSlot))
                    print "\t\t %s" % after
                    for spillinstr in after:
                        b.insert(idx-1,spillinstr)
                        after = []
                
                for instrx in b:
                    print '\t',instrx
        
        
        

