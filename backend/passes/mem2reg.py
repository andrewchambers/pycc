
import functionpass
from backend import ir
from backend import function


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
            #eliminate slots who have writes with differing types
            
            pointer = instr.read[0]
            slot = self.slotPointerMap.get(pointer,None)
            if slot: # we are still tracking this
                storeType = type(instr.read[1])
                
                if pointer not in self.slotUseTypes:
                    self.slotUseTypes[slot] = storeType
                
                if storeType != self.slotUseTypes[slot]:
                    self.eliminateSlot(slot)
        else:
            for v in instr.read:
                if self.isTrackingPointer(v):
                    self.eliminateSlot(self.slotPointerMap[v])
        
    def eliminateSlot(self,slot):
        for p in self.slotPointerMap[slot]:
            del self.slotPointerMap[p]
        del self.slotPointerMap[slot]
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
    
    def runOnFunction(self,f):
        
        
        #gather all aliasing slot pointers
        stracker = PromoteableSlotTracker()
        
        #XXX merge this code with the updateTrackerInfo code
        for block in f:
            for instr in block:
                if type(instr) == ir.LoadLocalAddr:
                    slot = instr.getSlot()
                    stracker.addSlotPointerPair(slot,instr.assigned[0])
        
        
        #update the tracker with all instructions so it can determine which are
        #slots are promoteable
        
        for block in f:
            for instr in block:
                stracker.updateTrackerInfo(instr)
                
        #map of slot -> virtual reg
        allocations = {}
        
        topromote = stracker.getPromoteableSlots()
        print topromote
        for slot,regclass in topromote:
            allocations[slot] = regclass()
        
        
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
        
        return True
