import target
from vis import irvis
from passes import jumpfix
from passes import blockmerge
from passes import unused
from passes import branchreplace

class StandardMachine(target.Target):
    def translateFunction(self,f,ofile):
        
        #irvis.showFunction(f)
        while True:
            irvis.showFunction(f)
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

