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
                
                elif type(instr) == ir.Branch:
                    if instr.read[0] in constants:
                        if constants[instr.read[0]].value == 0:
                            b[idx] = ir.Jmp(instr.successors[1])
                        else:
                            b[idx] = ir.Jmp(instr.successors[0])
                elif type(instr) == ir.Binop:
                    if instr.read[0] in constants and instr.read[1] in constants:
                        if type(instr.read[0]) == ir.I32 and type(instr.read[1]) == ir.I32:
                            
                            x = constants[instr.read[0]].value
                            y = constants[instr.read[1]].value
                            
                            if instr.op == '*':
                                val = x * y
                            elif instr.op == '/':
                                val = x / y
                            elif instr.op == '%':
                                val = x % y
                            elif instr.op == '+':
                                val = x + y
                            elif instr.op == '-':
                                val = x - y
                            elif instr.op == '!=':
                                if x != y:
                                    val = 1
                                else:
                                    val = 0
                            elif instr.op == '==':
                                if x == y:
                                    val = 1
                                else:
                                    val = 0
                            else:
                               print("constant fold unsupported %s " % instr.op )
                               idx += 1
                               continue
                            val = ir.ConstantI32(val)
                            b.insert(idx,ir.LoadConstant(instr.assigned[0],val))
                            changed = True
                            del b[idx + 1]
                idx += 1
        return changed
