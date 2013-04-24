from backend import aliasing

class definateAliasMerge(FunctionPass):
    
    def runOnFunction(self,f):
        
        for block in function:
            initialAddresses = {}
            replacements = []
            
            idx = 0
            while idx < len(block):
                
                instr = block[idx]
                
                if type(instr) == ir.LoadLocalAddress:
                    if instr.sym.slot not in initialAddresses:
                        initialAddresses[instr.sym.slot] = instr.assigned[0]
                    else:
                        replacements.append((initialAddresses[instr.sym.slot],instr.assigned[0]))
                        del block[idx]
                        idx -= 1
                
                for old,new in replacements:
                    instr.swapVar(old,new)
                
                idx += 1
