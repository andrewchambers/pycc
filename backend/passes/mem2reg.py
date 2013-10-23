
import functionpass
from backend import ir
from backend import function
from backend import dominators

from vis import irvis

#This pass aims to be similar to the mem2reg pass in llvm. promoting 
#registers from stack slots into registers

class PromoteableSlotTracker(object):
    
    def __init__(self):
        #dict of StackSlot -> Set (Pointer)
        #and Pointer -> StackSkot
        self.slotPointerMap = {}
        #dict of stackslot -> type
        #used to find out if the loaded type changed ever
        self.slotUseTypes = {}
    
    def updateTrackerInfo(self,instr):
        
        if type(instr) == ir.Deref:
            
            #eliminate slots who have reads with differing types
            
            pointer = instr.read[0]
            slot = self.slotPointerMap.get(pointer,None)
            if slot: # we are still tracking this
                loadType = type(instr.assigned[0])
                
                if pointer not in self.slotUseTypes:
                    self.slotUseTypes[slot] = loadType
                
                if loadType != self.slotUseTypes[slot]:
                    self.eliminateSlot(slot)
                
            
        elif type(instr) == ir.Store:
            #print "XXXXXXXXXXXXX",instr
            #eliminate slots who have writes with differing types
            
            pointer = instr.read[0]
            slot = self.slotPointerMap.get(pointer,None)
            if slot: # we are still tracking this
                storeType = type(instr.read[1])
                
                if pointer not in self.slotUseTypes:
                    self.slotUseTypes[slot] = storeType
                
                if storeType != self.slotUseTypes[slot]:
                    self.eliminateSlot(slot)
            
            #store can use the pointer as an argument too
            #which prevents us from promoting to a register...
            v = instr.read[1]
            if self.isTrackingPointer(v):
                self.eliminateSlot(self.slotPointerMap[v])
            
        else:
            for v in instr.read:
                if self.isTrackingPointer(v):
                    self.eliminateSlot(self.slotPointerMap[v])
        
    def eliminateSlot(self,slot):
        for p in self.slotPointerMap[slot]:
            del self.slotPointerMap[p]
        del self.slotPointerMap[slot]
        if slot in self.slotUseTypes:
            del self.slotUseTypes[slot]
    
    def isTrackingPointer(self,p):
        return p in self.slotPointerMap
    
    def addSlotPointerPair(self,slot,pointer):
        if slot not in self.slotPointerMap:
            self.slotPointerMap[slot] = set()
        self.slotPointerMap[slot].add(pointer)
        self.slotPointerMap[pointer] = slot
    
    def getPromoteableSlots(self):
        slots = filter(lambda x : type(x) == function.StackSlot,self.slotPointerMap.keys())
        return list(map(lambda x : [x,self.slotUseTypes[x]],slots))
    
    def getPromoteableSlotFromPointer(self,pointer):
        return self.slotPointerMap.get(pointer,None)
    
    
class Mem2Reg(functionpass.FunctionPass):
    
    def ssaify(self,dominatorinfo,f,v):
        
        everInWorklist = set()
        worklist = set()
        hasphi = set()
        addedPhis = set()
        
        for block in f:
            for instr in block:
                if v in instr.assigned:
                    worklist.add(block)
                    everInWorklist.add(block)
        
        while len(worklist):
            n = worklist.pop()
            for dfNode in dominatorinfo.getDominanceFrontier(n):
                if dfNode not in hasphi:
                    hasphi.add(dfNode)
                    newPhi = ir.Phi(v,[])
                    addedPhis.add(newPhi)
                    dfNode.insert(0,newPhi)
                    if dfNode not in everInWorklist:
                        worklist.add(dfNode)
                        everInWorklist.add(dfNode)
        domtree = dominatorinfo.getDominatorTree()
        self.rename(domtree,v,domtree['root'],v,addedPhis)
    
    def rename(self,dominatortree,v,block,newv,addedPhis):
        
        for instr in block:
            if type(instr) != ir.Phi:
                instr.swapRead(v,newv)
            if v in instr.assigned:
                newv = type(v)()
                instr.swapAssigned(v,newv)
        
        for successor in block.getSuccessors():
            for instr in successor:
                if type(instr) == ir.Phi:
                    if instr in addedPhis:
                        instr.read.append(newv)
                        instr.blocks.append(block)
        if block in dominatortree:
            for next in dominatortree[block]:
                self.rename(dominatortree,v,next,newv,addedPhis)
    
    def runOnFunction(self,f):
        
        
        #gather all aliasing slot pointers
        stracker = PromoteableSlotTracker()
        
        #XXX merge this code with the updateTrackerInfo code
        for block in f:
            for instr in block:
                if type(instr) == ir.LoadLocalAddr:
                    slot = instr.getStackSlots()[0]
                    stracker.addSlotPointerPair(slot,instr.assigned[0])
        
        
        #update the tracker with all instructions so it can determine which are
        #slots are promoteable
        
        for block in f:
            for instr in block:
                stracker.updateTrackerInfo(instr)
                
        #map of slot -> virtual reg
        allocations = {}
        
        topromote = stracker.getPromoteableSlots()
        
        #for slot in topromote:
        #    print slot
        
        #print topromote
        for slot,regclass in topromote:
            allocations[slot] = regclass()
        
        #convert loads and stores to copys
        for block in f:
            for idx,instr in enumerate(block):
                if type(instr) == ir.Deref:
                    promoteableSlot = stracker.getPromoteableSlotFromPointer(instr.read[0])
                    if promoteableSlot:
                        block[idx] = ir.Move(instr.assigned[0],allocations[promoteableSlot])
                elif type(instr) == ir.Store:
                    promoteableSlot = stracker.getPromoteableSlotFromPointer(instr.read[0])
                    if promoteableSlot:
                        block[idx] = ir.Move(allocations[promoteableSlot],instr.read[1])
        
        #Now that we have moved out of SSA, we must move back into SSA
        
        
        
        di = dominators.DominatorInfo(f)
        
        for v in allocations.values():
            #print v
            self.ssaify(di,f,v)
            #irvis.showFunction(f)
        #print di.dominators
        #print di.getDominatorTree()
        #print di.getDominanceFrontiers()
        
        
        return True
