import functionpass
from backend import ir


#this pass removes all unconditional jumps that are inbetween other jumps
# e.g.   block1 -> uncond1 -> uncond2 -> block2  can become block1-> block2
#

class JumpFix(functionpass.FunctionPass):
    
    def runOnFunction(self,f):
        modified = False
        swapped = True
        while swapped:
            swapped = False
            for b in f:
                for s in b[-1].getSuccessors():
                    if s is b:
                        continue
                    if len(s) == 1:
                        if type(s[0]) == ir.Jmp:
                            jmptarget =  s[0].getSuccessors()[0]
                            if s == jmptarget:
                                continue
                            b[-1].swapSuccessor(s,jmptarget)
                            swapped = True
                            modified = True
        return modified
