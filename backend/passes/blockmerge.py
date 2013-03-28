import functionpass
from backend import ir


#this fuses blocks that dont need to be seperate

class BlockMerge(functionpass.FunctionPass):
    
    def runOnFunction(self,f):
            modified = False
            incoming = {}
            for b in f:
                for s in b[-1].getSuccessors():
                    if s not in incoming:
                        incoming[s] = []
                    incoming[s].append(b)
            
            for b in incoming:
                if len(incoming[b]) == 1:
                    pred = incoming[b][0]
                    if type(pred[-1]) == ir.Jmp:
                        pred.opcodes = pred.opcodes[:-1] + b.opcodes
                        modified = True
            return modified
