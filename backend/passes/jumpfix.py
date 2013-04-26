import functionpass
from backend import ir


#this pass removes all unconditional jumps that are inbetween other jumps
# e.g.   block1 -> uncond1 -> uncond2 -> block2  can become block1-> block2
#

class JumpFix(functionpass.FunctionPass):
    
    def runOnFunction(self,f):
        
        mappings = {}
        modified = False
        swapped = True
        while swapped:
            swapped = False
            for b in f:
                for s in b.getSuccessors():
                    if s is b:
                        continue
                    if len(s) == 1:
                        if type(s[0]) == ir.Jmp:
                            jmptarget =  s[0].getSuccessors()[0]
                            if s == jmptarget:
                                continue
                            b[-1].swapSuccessor(s,jmptarget)
                            mappings[s] = b
                            swapped = True
                            modified = True
        
        if modified:
            mappingsChanged = True
            #if there was a chain of remappings then do resolve it
            while mappingsChanged:
                mappingsChanged = False
                for k in mappings.keys():
                    if mappings[k] in mappings.keys():
                        mappings[k] = mappings[mappings[k]]
                        mappingsChanged = True
            #print
            #print mappings
            #update all phi instructions
            for b in f:
                for instr in b:
                    if type(instr) == ir.Phi:
                        for idx,phiblock in enumerate(instr.blocks):
                            if phiblock in mappings:
                                print instr.blocks[idx],mappings[phiblock]
                                instr.blocks[idx] = mappings[phiblock]
        
        return modified
