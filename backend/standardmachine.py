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
import registerallocator

class Register(object):
    def __init__(self,name,sizes):
        self.name = name
        self.sizes = sizes
    def __repr__(self):
        return self.name
    
    def isPhysical(self):
        return True

class StandardMachine(target.Target):
    
    def translateFunction(self,f,ofile):
        
        if self.args.show_all or self.args.show_preopt_function:
            irvis.showFunction(f)
        
        opt = self.args.iropt
        while opt:
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
        
        if self.args.show_all or self.args.show_postopt_function:
            irvis.showFunction(f)

        
        for b in f:
            sd = selectiondag.SelectionDag(b)
            isel = instructionselector.InstructionSelector()
            if self.args.show_all or self.args.show_selection_dag:
                dagvis.showSelDAG(sd)
            self.applyDagFixups(sd)
            self.callingConventions(sd)
            isel.select(self,sd)
            if self.args.show_all or self.args.show_md_selection_dag:
                dagvis.showSelDAG(sd)
            newblockops = [node.instr for node in sd.topological()]
            b.opcodes = newblockops
        
        ig = interference.InterferenceGraph(f)
        interferencevis.showInterferenceGraph(ig)
        
        ra = registerallocator.RegisterAllocator()
        ra.allocate(f,ig)
        
        
        if self.args.show_all or self.args.show_md_function:
            irvis.showFunction(f)
        
    
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
