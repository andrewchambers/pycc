import functionpass
from backend import ir



class CopyPropagation(functionpass.FunctionPass):
    
    def runOnFunction(self,f):
        changed = False
        chain = {}
        
        #build a chain of equivalent vars
        
        for block in f:
            idx = 0
            while idx < len(block):
                instr = block[idx]
                if type(instr) in [ir.Move,ir.Phi]:
                    if len(instr.read) == 1:
                        chain[instr.assigned[0]] = instr.read[0]
                        del block[idx]
                        changed = True
                        continue
                idx += 1
        
        if not changed:
            return False
        
        chainChanged = True
        while chainChanged:
            chainChanged = False
            for k in chain.keys():
                if chain[k] in chain.keys():
                    chain[k] = chain[chain[k]]
                    chainChanged = True
        
        for block in f:
            for instr in block:
                for k in chain:
                    instr.swapVar(k,chain[k])
                
        return True
