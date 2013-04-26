import functionpass
from backend import ir


#this fuses blocks that dont need to be seperate

class BlockMerge(functionpass.FunctionPass):
    
    def runOnFunction(self,f):
            modified = False
            incoming = {}
            for b in f:
                for s in b.getSuccessors():
                    if s not in incoming:
                        incoming[s] = []
                    incoming[s].append(b)
            
            #dict to update phi nodes
            mappings = {}
            
            for b in incoming:
                if len(incoming[b]) == 1:
                    pred = incoming[b][0]
                    if type(pred[-1]) == ir.Jmp:
                        #combine the two...
                        #combine the opcodes
                        pred.opcodes = pred.opcodes[:-1] + b.opcodes
                        mappings[b] = pred
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
                #update all phi instructions
                for b in f:
                    for instr in b:
                        if type(instr) == ir.Phi:
                            for idx,phiblock in enumerate(instr.blocks):
                                if phiblock in mappings:
                                    instr.blocks[idx] = mappings[phiblock]
            
            return modified
