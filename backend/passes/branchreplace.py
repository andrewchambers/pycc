import functionpass
from backend import ir


#this pass removes branches who have the same outcome for both cases

class BranchReplace(functionpass.FunctionPass):
    
    def runOnFunction(self,f):
        modified = False
        for b in f:
            if type(b[-1]) == ir.Branch:
                s = b[-1].getSuccessors()
                if s[0] is s[1]:
                    b[-1] = ir.Jmp(s[0])
                    modified = True
        return modified
