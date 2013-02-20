import target
import selectiondag

from vis import irvis
from vis import dagvis
from passes import jumpfix
from passes import blockmerge
from passes import unused
from passes import branchreplace

from backend import instructionselector

class Register(object):
    def __init__(self,name,sizes):
        self.name = name
        self.sizes = sizes
    def __repr__(name):
        return self.name

class StandardMachine(target.Target):
    
    def translateFunction(self,f,ofile):
        
        irvis.showFunction(f)
        while True:
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
            #isel.select(self,sd)
            #dagvis.showSelDAG(sd)
            #self.callingConventions(sd)
            #dagvis.showSelDAG(sd)
    
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
