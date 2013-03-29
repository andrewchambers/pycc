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

import ir

class Register(object):
    def __init__(self,name,sizes):
        self.name = name
        self.sizes = set(sizes)
    
    def canContain(self,t):
        if type(t) == type(self):
            return True
        
        if t in self.sizes:
            return True
        
        return False
    
    def __repr__(self):
        return self.name
    
    def isPhysical(self):
        return True

class StandardMachine(target.Target):
    
    
    def translateFunction(self,f,ofile):
        
        if self.args.show_all or self.args.show_preopt_function:
            irvis.showFunction(f)

        if self.args.iropt:
            self.doIROpt(f)
        
        if self.args.show_all or self.args.show_postopt_function:
            irvis.showFunction(f)
        
        self.doInstructionSelection(f)
        
        ig = interference.InterferenceGraph(f)
        if self.args.show_all or self.args.show_interference:
            interferencevis.showInterferenceGraph(ig)
        
        ra = registerallocator.RegisterAllocator(self)
        ra.allocate(f,ig)
        
        f.resolveStack()
        
        if self.args.show_all or self.args.show_md_function:
            irvis.showFunction(f)
        
        
        self.prologAndEpilog(f)
        
        #linearize the function
        
        linear = list(f)
        
        #swap remove branch targets that will fall through
        for idx,b in enumerate(linear):
            terminator = b[-1]
            successors = terminator.getSuccessors()
            for target in successors:
                nextIdx = idx + 1
                if nextIdx >= len(linear):
                    continue
                if target == linear[nextIdx]:
                    terminator.swapSuccessor(target,None)
            
            linear[idx][-1] = self.terminatorSelection(terminator)
        
        ofile.write(".globl %s\n" % f.name)
        ofile.write("_%s:\n" % f.name)
        
        for block in linear:
            ofile.write("." + block.name + ':\n')
            for instr in block:
                ofile.write("\t" + instr.asm() + '\n')
            
        
        
    def doIROpt(self,func):
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
    
    def doInstructionSelection(self,func):
        for b in func:
            sd = selectiondag.SelectionDag(b)
            isel = instructionselector.InstructionSelector()
            if self.args.show_all or self.args.show_selection_dag:
                dagvis.showSelDAG(sd)
            self.applyDagFixups(sd)
            self.callingConventions(sd)
            isel.select(self,sd)
            if self.args.show_all or self.args.show_md_selection_dag:
                dagvis.showSelDAG(sd)
            newblockops = [node.instr for node in sd.ordered()]
            b.opcodes = newblockops
    
    def branchSelection(self,instr):
        raise Exception("unimlpemented")
    
    def outputModule(self,m,ofile):
        for f in m:
            self.outputFunction(f,ofile)
    
    def applyDagFixups(self,dag):
        pass
    
    def callingConventions(self,dag):
        pass
    
    def prologAndEpilog(self,func):
        
        stackSize = func.stackSize
        entry = func.entry
        
        prolog = self.getProlog(stackSize)
        
        insertCounter = 0
        for instr in prolog:
            entry.insert(0 + insertCounter,instr)
            insertCounter += 1
        
        for b in func:
            if type(b[-1]) == ir.Ret:
                epilog = self.getEpilog(stackSize)
                for instr in epilog:
                    b.insert(-1,instr)
        
    def getEpilog(self,stackSize):
        raise Exception("unimplemented")
    
    def getProlog(self,stackSize):
        raise Exception("unimplemented")
    
    
    def getRegisters(self):
        return []
    
    def getInstructions(self):
        raise Exception("unimplemented")
    
    def getPossibleRegisters(self,v):
        t = type(v)
        return filter(lambda x : x.canContain(t),self.getRegisters())
    
