import target
import selectiondag

from vis import irvis
from vis import dagvis
from vis import interferencevis

from passes import jumpfix
from passes import blockmerge
from passes import unused
from passes import branchreplace

import instructionselector
import interference

class Register(object):
    def __init__(self,name,sizes):
        self.name = name
        self.sizes = sizes
    def __repr__(self):
        return self.name

class StandardMachine(target.Target):
    
    def translateFunction(self,f,ofile):
        
        irvis.showFunction(f)
        while False:
            #irvis.showFunction(f)
            if jumpfix.JumpFix().runOnFunction(f):
                continue
            if blockmerge.BlockMerge().runOnFunction(f):
                continue
            if unused.UnusedVars().runOnFunction(f):
                continue
            if branchreplace.BranchReplace().runOnFunction(f):
                continue
            
            break
            
        irvis.showFunction(f)
        
        
        for b in f:
            sd = selectiondag.SelectionDag(b)
            isel = instructionselector.InstructionSelector()
            dagvis.showSelDAG(sd)
            self.applyDagFixups(sd)
            dagvis.showSelDAG(sd)
            self.callingConventions(sd)
            dagvis.showSelDAG(sd)
            isel.select(self,sd)
            dagvis.showSelDAG(sd)
            newblockops = [node.instr for node in sd.topological()]
            b.opcodes = newblockops
        
        irvis.showFunction(f)
        ig = interference.InterferenceGraph(f)
        interferencevis.showInterferenceGraph(ig)
    
    def applyDagFixups(self,dag):
        pass
    
    def callingConventions(self,dag):
        pass
    
    def prologAndEpilog(self,dag):
        pass
    
    def getRegisters(self):
        return []
    
    def getInstructions(self):
        raise Exception("unimplemented")
