import functionpass
from backend import ir


#remove vars that arent used

class ConstantFold(functionpass.FunctionPass):
    
    def runOnFunction(self,f):
        changed = False
        for b in f:
            constants = {}
            idx = 0
            while idx < len(b):
                instr = b[idx]
                if type(instr) == ir.LoadConstant:
                    constants[instr.assigned[0]] = instr.const
                elif type(instr) == ir.Binop:
                    if instr.read[0] in constants and instr.read[1] in constants:
                        if type(instr.read[0]) == ir.I32 and type(instr.read[1]) == ir.I32:
                            
                            if instr.op == '*':
                                val = constants[instr.read[0]] * constants[instr.read[1]]
                            elif instr.op == '/':
                                val = constants[instr.read[0]] / constants[instr.read[1]]
                            elif instr.op == '%':
                                val = constants[instr.read[0]] % constants[instr.read[1]]
                            elif instr.op == '+':
                                val =  constants[instr.read[0]] + constants[instr.read[1]]
                            elif instr.op == '-':
                                val =  constants[instr.read[0]] - constants[instr.read[1]]
                            else:
                                raise Exception("constant fold unsupported %s " % instr.op )
                            
                            b.insert(idx,ir.LoadConstant(instr.assigned[0],val))
                            changed = True
                            del b[idx + 1]
                idx += 1
        return changed
