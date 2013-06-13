#Auto generated file! generated with ./mdcompiler/mdcompiler.py
from backend import machineinstruction
from backend import  ir
import backend.selectiondag as seldag

import x86

#['instr', 'X86Add', ['pattern', ['_', 'Binop', '"+"', ['_'], ['_']]], ['asmstr', '"add %{2},%{0}"']]
class X86Add(machineinstruction.MI):
    @classmethod
    def match(cls,dag,node):
        nodestack = [node]
        newchildren = []
        newins = []
        if len(nodestack[-1].instr.assigned) != 1:
            return False
        out = nodestack[-1].instr.assigned
        if type(nodestack[-1].instr) != ir.Binop:
            return False
        if nodestack[-1].instr.op != "+":
            return False
        #we can only match nodes with noutputs 1
        if nodestack[-1].children[0][0] != 0:
            return False
        nodestack.append(nodestack[-1].children[0][1])
        #matching terminal ['_']
        newchildren.append((0,nodestack[-1]))
        newins.append(nodestack[-1].instr.assigned[0])
        nodestack.pop()
        #we can only match nodes with noutputs 1
        if nodestack[-1].children[1][0] != 0:
            return False
        nodestack.append(nodestack[-1].children[1][1])
        #matching terminal ['_']
        newchildren.append((0,nodestack[-1]))
        newins.append(nodestack[-1].instr.assigned[0])
        nodestack.pop()
        node.instr = cls(node)
        node.instr.assigned = out
        node.children = newchildren
        node.instr.read = newins
        return True
    asmstr = "add %{2},%{0}"
    def __init__(self,node):
        machineinstruction.MI.__init__(self)
        pass

#['instr', 'X86Sub', ['pattern', ['_', 'Binop', '"-"', ['_'], ['_']]], ['asmstr', '"sub %{2},%{0}"']]
class X86Sub(machineinstruction.MI):
    @classmethod
    def match(cls,dag,node):
        nodestack = [node]
        newchildren = []
        newins = []
        if len(nodestack[-1].instr.assigned) != 1:
            return False
        out = nodestack[-1].instr.assigned
        if type(nodestack[-1].instr) != ir.Binop:
            return False
        if nodestack[-1].instr.op != "-":
            return False
        #we can only match nodes with noutputs 1
        if nodestack[-1].children[0][0] != 0:
            return False
        nodestack.append(nodestack[-1].children[0][1])
        #matching terminal ['_']
        newchildren.append((0,nodestack[-1]))
        newins.append(nodestack[-1].instr.assigned[0])
        nodestack.pop()
        #we can only match nodes with noutputs 1
        if nodestack[-1].children[1][0] != 0:
            return False
        nodestack.append(nodestack[-1].children[1][1])
        #matching terminal ['_']
        newchildren.append((0,nodestack[-1]))
        newins.append(nodestack[-1].instr.assigned[0])
        nodestack.pop()
        node.instr = cls(node)
        node.instr.assigned = out
        node.children = newchildren
        node.instr.read = newins
        return True
    asmstr = "sub %{2},%{0}"
    def __init__(self,node):
        machineinstruction.MI.__init__(self)
        pass

#['instr', 'X86SHLI32', ['pattern', ['I32', 'Binop', '"<<"', ['I32'], ['I32']]], ['asmstr', '"shl %cl,%{0}"']]
class X86SHLI32(machineinstruction.MI):
    @classmethod
    def match(cls,dag,node):
        nodestack = [node]
        newchildren = []
        newins = []
        if len(nodestack[-1].instr.assigned) != 1:
            return False
        out = nodestack[-1].instr.assigned
        if type(nodestack[-1].instr.assigned[0]) != ir.I32:
            return False
        if type(nodestack[-1].instr) != ir.Binop:
            return False
        if nodestack[-1].instr.op != "<<":
            return False
        #we can only match nodes with noutputs 1
        if nodestack[-1].children[0][0] != 0:
            return False
        nodestack.append(nodestack[-1].children[0][1])
        #matching terminal ['I32']
        if type(nodestack[-1].instr.assigned[0]) != ir.I32:
            return False
        newchildren.append((0,nodestack[-1]))
        newins.append(nodestack[-1].instr.assigned[0])
        nodestack.pop()
        #we can only match nodes with noutputs 1
        if nodestack[-1].children[1][0] != 0:
            return False
        nodestack.append(nodestack[-1].children[1][1])
        #matching terminal ['I32']
        if type(nodestack[-1].instr.assigned[0]) != ir.I32:
            return False
        newchildren.append((0,nodestack[-1]))
        newins.append(nodestack[-1].instr.assigned[0])
        nodestack.pop()
        node.instr = cls(node)
        node.instr.assigned = out
        node.children = newchildren
        node.instr.read = newins
        return True
    asmstr = "shl %cl,%{0}"
    def __init__(self,node):
        machineinstruction.MI.__init__(self)
        pass

#['instr', 'X86SHRI32', ['pattern', ['I32', 'Binop', '">>"', ['I32'], ['I32']]], ['asmstr', '"shr %cl,%{0}"']]
class X86SHRI32(machineinstruction.MI):
    @classmethod
    def match(cls,dag,node):
        nodestack = [node]
        newchildren = []
        newins = []
        if len(nodestack[-1].instr.assigned) != 1:
            return False
        out = nodestack[-1].instr.assigned
        if type(nodestack[-1].instr.assigned[0]) != ir.I32:
            return False
        if type(nodestack[-1].instr) != ir.Binop:
            return False
        if nodestack[-1].instr.op != ">>":
            return False
        #we can only match nodes with noutputs 1
        if nodestack[-1].children[0][0] != 0:
            return False
        nodestack.append(nodestack[-1].children[0][1])
        #matching terminal ['I32']
        if type(nodestack[-1].instr.assigned[0]) != ir.I32:
            return False
        newchildren.append((0,nodestack[-1]))
        newins.append(nodestack[-1].instr.assigned[0])
        nodestack.pop()
        #we can only match nodes with noutputs 1
        if nodestack[-1].children[1][0] != 0:
            return False
        nodestack.append(nodestack[-1].children[1][1])
        #matching terminal ['I32']
        if type(nodestack[-1].instr.assigned[0]) != ir.I32:
            return False
        newchildren.append((0,nodestack[-1]))
        newins.append(nodestack[-1].instr.assigned[0])
        nodestack.pop()
        node.instr = cls(node)
        node.instr.assigned = out
        node.children = newchildren
        node.instr.read = newins
        return True
    asmstr = "shr %cl,%{0}"
    def __init__(self,node):
        machineinstruction.MI.__init__(self)
        pass

#['instr', 'X86IMulI32', ['pattern', ['I32', 'Binop', '"*"', ['I32'], ['I32']]], ['asmstr', '"mul %{3}"']]
class X86IMulI32(machineinstruction.MI):
    @classmethod
    def match(cls,dag,node):
        nodestack = [node]
        newchildren = []
        newins = []
        if len(nodestack[-1].instr.assigned) != 1:
            return False
        out = nodestack[-1].instr.assigned
        if type(nodestack[-1].instr.assigned[0]) != ir.I32:
            return False
        if type(nodestack[-1].instr) != ir.Binop:
            return False
        if nodestack[-1].instr.op != "*":
            return False
        #we can only match nodes with noutputs 1
        if nodestack[-1].children[0][0] != 0:
            return False
        nodestack.append(nodestack[-1].children[0][1])
        #matching terminal ['I32']
        if type(nodestack[-1].instr.assigned[0]) != ir.I32:
            return False
        newchildren.append((0,nodestack[-1]))
        newins.append(nodestack[-1].instr.assigned[0])
        nodestack.pop()
        #we can only match nodes with noutputs 1
        if nodestack[-1].children[1][0] != 0:
            return False
        nodestack.append(nodestack[-1].children[1][1])
        #matching terminal ['I32']
        if type(nodestack[-1].instr.assigned[0]) != ir.I32:
            return False
        newchildren.append((0,nodestack[-1]))
        newins.append(nodestack[-1].instr.assigned[0])
        nodestack.pop()
        node.instr = cls(node)
        node.instr.assigned = out
        node.children = newchildren
        node.instr.read = newins
        return True
    asmstr = "mul %{3}"
    def __init__(self,node):
        machineinstruction.MI.__init__(self)
        pass

#['instr', 'X86IDivI32', ['pattern', ['I32', 'Binop', '"/"', ['I32'], ['I32']]], ['asmstr', '"cdq\\nidiv %{3}"'], ['extra', '"    \n    def getPreClobberedRegisters(self):\n        return [x86.getRegisterByName(\'edx\')]\n    "']]
class X86IDivI32(machineinstruction.MI):
    @classmethod
    def match(cls,dag,node):
        nodestack = [node]
        newchildren = []
        newins = []
        if len(nodestack[-1].instr.assigned) != 1:
            return False
        out = nodestack[-1].instr.assigned
        if type(nodestack[-1].instr.assigned[0]) != ir.I32:
            return False
        if type(nodestack[-1].instr) != ir.Binop:
            return False
        if nodestack[-1].instr.op != "/":
            return False
        #we can only match nodes with noutputs 1
        if nodestack[-1].children[0][0] != 0:
            return False
        nodestack.append(nodestack[-1].children[0][1])
        #matching terminal ['I32']
        if type(nodestack[-1].instr.assigned[0]) != ir.I32:
            return False
        newchildren.append((0,nodestack[-1]))
        newins.append(nodestack[-1].instr.assigned[0])
        nodestack.pop()
        #we can only match nodes with noutputs 1
        if nodestack[-1].children[1][0] != 0:
            return False
        nodestack.append(nodestack[-1].children[1][1])
        #matching terminal ['I32']
        if type(nodestack[-1].instr.assigned[0]) != ir.I32:
            return False
        newchildren.append((0,nodestack[-1]))
        newins.append(nodestack[-1].instr.assigned[0])
        nodestack.pop()
        node.instr = cls(node)
        node.instr.assigned = out
        node.children = newchildren
        node.instr.read = newins
        return True
    asmstr = "cdq\nidiv %{3}"
    
    def getPreClobberedRegisters(self):
        return [x86.getRegisterByName('edx')]
    
    def __init__(self,node):
        machineinstruction.MI.__init__(self)
        pass

#['instr', 'X86IModI32', ['pattern', ['I32', 'Binop', '"%"', ['I32'], ['I32']]], ['asmstr', '"cdq\\nidiv %{3}"'], ['extra', '"    \n    def getPreClobberedRegisters(self):\n        return [x86.getRegisterByName(\'edx\')]\n    "']]
class X86IModI32(machineinstruction.MI):
    @classmethod
    def match(cls,dag,node):
        nodestack = [node]
        newchildren = []
        newins = []
        if len(nodestack[-1].instr.assigned) != 1:
            return False
        out = nodestack[-1].instr.assigned
        if type(nodestack[-1].instr.assigned[0]) != ir.I32:
            return False
        if type(nodestack[-1].instr) != ir.Binop:
            return False
        if nodestack[-1].instr.op != "%":
            return False
        #we can only match nodes with noutputs 1
        if nodestack[-1].children[0][0] != 0:
            return False
        nodestack.append(nodestack[-1].children[0][1])
        #matching terminal ['I32']
        if type(nodestack[-1].instr.assigned[0]) != ir.I32:
            return False
        newchildren.append((0,nodestack[-1]))
        newins.append(nodestack[-1].instr.assigned[0])
        nodestack.pop()
        #we can only match nodes with noutputs 1
        if nodestack[-1].children[1][0] != 0:
            return False
        nodestack.append(nodestack[-1].children[1][1])
        #matching terminal ['I32']
        if type(nodestack[-1].instr.assigned[0]) != ir.I32:
            return False
        newchildren.append((0,nodestack[-1]))
        newins.append(nodestack[-1].instr.assigned[0])
        nodestack.pop()
        node.instr = cls(node)
        node.instr.assigned = out
        node.children = newchildren
        node.instr.read = newins
        return True
    asmstr = "cdq\nidiv %{3}"
    
    def getPreClobberedRegisters(self):
        return [x86.getRegisterByName('edx')]
    
    def __init__(self,node):
        machineinstruction.MI.__init__(self)
        pass

#['instr', 'X86NotI32', ['pattern', ['I32', 'Unop', '"!"', ['I32']]], ['asmstr', '"        \n        if self.read[0] == self.assigned[0]:\n            ret =  \'subl $1,%{0}\\nadcl %{0},%{0}\\nandl $1,%{0}\'\n            return ret.format(self.assigned[0])\n        else:\n            o = self.assigned[0]\n            ret = \'movl %{1},%{0}\\n\' + \\\n                  \'addl $-1,%{1}\\n\' + \\\n                  \'sbbl %{1},%{0}\\n\'\n            return ret.format(self.assigned[0],self.read[0])    \n    "']]
class X86NotI32(machineinstruction.MI):
    @classmethod
    def match(cls,dag,node):
        nodestack = [node]
        newchildren = []
        newins = []
        if len(nodestack[-1].instr.assigned) != 1:
            return False
        out = nodestack[-1].instr.assigned
        if type(nodestack[-1].instr.assigned[0]) != ir.I32:
            return False
        if type(nodestack[-1].instr) != ir.Unop:
            return False
        if nodestack[-1].instr.op != "!":
            return False
        #we can only match nodes with noutputs 1
        if nodestack[-1].children[0][0] != 0:
            return False
        nodestack.append(nodestack[-1].children[0][1])
        #matching terminal ['I32']
        if type(nodestack[-1].instr.assigned[0]) != ir.I32:
            return False
        newchildren.append((0,nodestack[-1]))
        newins.append(nodestack[-1].instr.assigned[0])
        nodestack.pop()
        node.instr = cls(node)
        node.instr.assigned = out
        node.children = newchildren
        node.instr.read = newins
        return True
    def asm(self):
        
        if self.read[0] == self.assigned[0]:
            ret =  'subl $1,%{0}\nadcl %{0},%{0}\nandl $1,%{0}'
            return ret.format(self.assigned[0])
        else:
            o = self.assigned[0]
            ret = 'movl %{1},%{0}\n' + \
                  'addl $-1,%{1}\n' + \
                  'sbbl %{1},%{0}\n'
            return ret.format(self.assigned[0],self.read[0])    
    
    def __init__(self,node):
        machineinstruction.MI.__init__(self)
        pass

#['instr', 'X86Mov', ['pattern', [['_'], 'Move', ['_']]], ['asmstr', '"mov %{1},%{0}"'], ['extra', '"    \n    def isMove(self):\n        return True\n    "']]
class X86Mov(machineinstruction.MI):
    @classmethod
    def match(cls,dag,node):
        nodestack = [node]
        newchildren = []
        newins = []
        if len(nodestack[-1].instr.assigned) != 1:
            return False
        out = nodestack[-1].instr.assigned
        if type(nodestack[-1].instr) != ir.Move:
            return False
        #we can only match nodes with noutputs 1
        if nodestack[-1].children[0][0] != 0:
            return False
        nodestack.append(nodestack[-1].children[0][1])
        #matching terminal ['_']
        newchildren.append((0,nodestack[-1]))
        newins.append(nodestack[-1].instr.assigned[0])
        nodestack.pop()
        node.instr = cls(node)
        node.instr.assigned = out
        node.children = newchildren
        node.instr.read = newins
        return True
    asmstr = "mov %{1},%{0}"
    
    def isMove(self):
        return True
    
    def __init__(self,node):
        machineinstruction.MI.__init__(self)
        pass

#['instr', 'X86NeI32', ['pattern', ['I32', 'Binop', '"!="', ['I32'], ['I32']]], ['asmstr', '"cmp %{2},%{1}\n        {instr.jmpinstr} {instr.branch}\n        xor %{0},%{0}\n        jmp {instr.exit}\n        {instr.branch}:\n        xor %{0},%{0}\n        inc %{0}\n        {instr.exit}:"'], ['extra', '"    jmpinstr = \'jne\'"'], ['constructor', '"        \n        self.branch = x86.newLocalLabel()\n        self.exit = x86.newLocalLabel()\n        "']]
class X86NeI32(machineinstruction.MI):
    @classmethod
    def match(cls,dag,node):
        nodestack = [node]
        newchildren = []
        newins = []
        if len(nodestack[-1].instr.assigned) != 1:
            return False
        out = nodestack[-1].instr.assigned
        if type(nodestack[-1].instr.assigned[0]) != ir.I32:
            return False
        if type(nodestack[-1].instr) != ir.Binop:
            return False
        if nodestack[-1].instr.op != "!=":
            return False
        #we can only match nodes with noutputs 1
        if nodestack[-1].children[0][0] != 0:
            return False
        nodestack.append(nodestack[-1].children[0][1])
        #matching terminal ['I32']
        if type(nodestack[-1].instr.assigned[0]) != ir.I32:
            return False
        newchildren.append((0,nodestack[-1]))
        newins.append(nodestack[-1].instr.assigned[0])
        nodestack.pop()
        #we can only match nodes with noutputs 1
        if nodestack[-1].children[1][0] != 0:
            return False
        nodestack.append(nodestack[-1].children[1][1])
        #matching terminal ['I32']
        if type(nodestack[-1].instr.assigned[0]) != ir.I32:
            return False
        newchildren.append((0,nodestack[-1]))
        newins.append(nodestack[-1].instr.assigned[0])
        nodestack.pop()
        node.instr = cls(node)
        node.instr.assigned = out
        node.children = newchildren
        node.instr.read = newins
        return True
    asmstr = "cmp %{2},%{1}\n        {instr.jmpinstr} {instr.branch}\n        xor %{0},%{0}\n        jmp {instr.exit}\n        {instr.branch}:\n        xor %{0},%{0}\n        inc %{0}\n        {instr.exit}:"
    jmpinstr = 'jne'
    def __init__(self,node):
        machineinstruction.MI.__init__(self)
        
        self.branch = x86.newLocalLabel()
        self.exit = x86.newLocalLabel()
        

#['instr', 'X86LtI32', ['pattern', ['I32', 'Binop', '"<"', ['I32'], ['I32']]], ['asmstr', '"cmp %{2},%{1}\n        {instr.jmpinstr} {instr.branch}\n        xor %{0},%{0}\n        jmp {instr.exit}\n        {instr.branch}:\n        xor %{0},%{0}\n        inc %{0}\n        {instr.exit}:"'], ['extra', '"    jmpinstr = \'jl\'"'], ['constructor', '"        \n        self.branch = x86.newLocalLabel()\n        self.exit = x86.newLocalLabel()\n        "']]
class X86LtI32(machineinstruction.MI):
    @classmethod
    def match(cls,dag,node):
        nodestack = [node]
        newchildren = []
        newins = []
        if len(nodestack[-1].instr.assigned) != 1:
            return False
        out = nodestack[-1].instr.assigned
        if type(nodestack[-1].instr.assigned[0]) != ir.I32:
            return False
        if type(nodestack[-1].instr) != ir.Binop:
            return False
        if nodestack[-1].instr.op != "<":
            return False
        #we can only match nodes with noutputs 1
        if nodestack[-1].children[0][0] != 0:
            return False
        nodestack.append(nodestack[-1].children[0][1])
        #matching terminal ['I32']
        if type(nodestack[-1].instr.assigned[0]) != ir.I32:
            return False
        newchildren.append((0,nodestack[-1]))
        newins.append(nodestack[-1].instr.assigned[0])
        nodestack.pop()
        #we can only match nodes with noutputs 1
        if nodestack[-1].children[1][0] != 0:
            return False
        nodestack.append(nodestack[-1].children[1][1])
        #matching terminal ['I32']
        if type(nodestack[-1].instr.assigned[0]) != ir.I32:
            return False
        newchildren.append((0,nodestack[-1]))
        newins.append(nodestack[-1].instr.assigned[0])
        nodestack.pop()
        node.instr = cls(node)
        node.instr.assigned = out
        node.children = newchildren
        node.instr.read = newins
        return True
    asmstr = "cmp %{2},%{1}\n        {instr.jmpinstr} {instr.branch}\n        xor %{0},%{0}\n        jmp {instr.exit}\n        {instr.branch}:\n        xor %{0},%{0}\n        inc %{0}\n        {instr.exit}:"
    jmpinstr = 'jl'
    def __init__(self,node):
        machineinstruction.MI.__init__(self)
        
        self.branch = x86.newLocalLabel()
        self.exit = x86.newLocalLabel()
        

#['instr', 'X86GtI32', ['pattern', ['I32', 'Binop', '">"', ['I32'], ['I32']]], ['asmstr', '"cmp %{2},%{1}\n        {instr.jmpinstr} {instr.branch}\n        xor %{0},%{0}\n        jmp {instr.exit}\n        {instr.branch}:\n        xor %{0},%{0}\n        inc %{0}\n        {instr.exit}:"'], ['extra', '"    jmpinstr = \'jg\'"'], ['constructor', '"        \n        self.branch = x86.newLocalLabel()\n        self.exit = x86.newLocalLabel()\n        "']]
class X86GtI32(machineinstruction.MI):
    @classmethod
    def match(cls,dag,node):
        nodestack = [node]
        newchildren = []
        newins = []
        if len(nodestack[-1].instr.assigned) != 1:
            return False
        out = nodestack[-1].instr.assigned
        if type(nodestack[-1].instr.assigned[0]) != ir.I32:
            return False
        if type(nodestack[-1].instr) != ir.Binop:
            return False
        if nodestack[-1].instr.op != ">":
            return False
        #we can only match nodes with noutputs 1
        if nodestack[-1].children[0][0] != 0:
            return False
        nodestack.append(nodestack[-1].children[0][1])
        #matching terminal ['I32']
        if type(nodestack[-1].instr.assigned[0]) != ir.I32:
            return False
        newchildren.append((0,nodestack[-1]))
        newins.append(nodestack[-1].instr.assigned[0])
        nodestack.pop()
        #we can only match nodes with noutputs 1
        if nodestack[-1].children[1][0] != 0:
            return False
        nodestack.append(nodestack[-1].children[1][1])
        #matching terminal ['I32']
        if type(nodestack[-1].instr.assigned[0]) != ir.I32:
            return False
        newchildren.append((0,nodestack[-1]))
        newins.append(nodestack[-1].instr.assigned[0])
        nodestack.pop()
        node.instr = cls(node)
        node.instr.assigned = out
        node.children = newchildren
        node.instr.read = newins
        return True
    asmstr = "cmp %{2},%{1}\n        {instr.jmpinstr} {instr.branch}\n        xor %{0},%{0}\n        jmp {instr.exit}\n        {instr.branch}:\n        xor %{0},%{0}\n        inc %{0}\n        {instr.exit}:"
    jmpinstr = 'jg'
    def __init__(self,node):
        machineinstruction.MI.__init__(self)
        
        self.branch = x86.newLocalLabel()
        self.exit = x86.newLocalLabel()
        

#['instr', 'X86EqI32', ['pattern', ['I32', 'Binop', '"=="', ['I32'], ['I32']]], ['asmstr', '"cmp %{2},%{1}\n        {instr.jmpinstr} {instr.branch}\n        xor %{0},%{0}\n        jmp {instr.exit}\n        {instr.branch}:\n        xor %{0},%{0}\n        inc %{0}\n        {instr.exit}:"'], ['extra', '"    jmpinstr = \'je\'"'], ['constructor', '"        \n        self.branch = x86.newLocalLabel()\n        self.exit = x86.newLocalLabel()\n        "']]
class X86EqI32(machineinstruction.MI):
    @classmethod
    def match(cls,dag,node):
        nodestack = [node]
        newchildren = []
        newins = []
        if len(nodestack[-1].instr.assigned) != 1:
            return False
        out = nodestack[-1].instr.assigned
        if type(nodestack[-1].instr.assigned[0]) != ir.I32:
            return False
        if type(nodestack[-1].instr) != ir.Binop:
            return False
        if nodestack[-1].instr.op != "==":
            return False
        #we can only match nodes with noutputs 1
        if nodestack[-1].children[0][0] != 0:
            return False
        nodestack.append(nodestack[-1].children[0][1])
        #matching terminal ['I32']
        if type(nodestack[-1].instr.assigned[0]) != ir.I32:
            return False
        newchildren.append((0,nodestack[-1]))
        newins.append(nodestack[-1].instr.assigned[0])
        nodestack.pop()
        #we can only match nodes with noutputs 1
        if nodestack[-1].children[1][0] != 0:
            return False
        nodestack.append(nodestack[-1].children[1][1])
        #matching terminal ['I32']
        if type(nodestack[-1].instr.assigned[0]) != ir.I32:
            return False
        newchildren.append((0,nodestack[-1]))
        newins.append(nodestack[-1].instr.assigned[0])
        nodestack.pop()
        node.instr = cls(node)
        node.instr.assigned = out
        node.children = newchildren
        node.instr.read = newins
        return True
    asmstr = "cmp %{2},%{1}\n        {instr.jmpinstr} {instr.branch}\n        xor %{0},%{0}\n        jmp {instr.exit}\n        {instr.branch}:\n        xor %{0},%{0}\n        inc %{0}\n        {instr.exit}:"
    jmpinstr = 'je'
    def __init__(self,node):
        machineinstruction.MI.__init__(self)
        
        self.branch = x86.newLocalLabel()
        self.exit = x86.newLocalLabel()
        

#['instr', 'X86LoadConstantI32', ['pattern', [['I32'], 'LoadConstant']], ['asmstr', '"mov ${instr.const},%{0}"'], ['constructor', '"        \n        self.const = node.instr.const    \n    "']]
class X86LoadConstantI32(machineinstruction.MI):
    @classmethod
    def match(cls,dag,node):
        nodestack = [node]
        newchildren = []
        newins = []
        if len(nodestack[-1].instr.assigned) != 1:
            return False
        out = nodestack[-1].instr.assigned
        if type(nodestack[-1].instr.assigned[0]) != ir.I32:
            return False
        if type(nodestack[-1].instr) != ir.LoadConstant:
            return False
        node.instr = cls(node)
        node.instr.assigned = out
        node.children = newchildren
        node.instr.read = newins
        return True
    asmstr = "mov ${instr.const},%{0}"
    def __init__(self,node):
        machineinstruction.MI.__init__(self)
        
        self.const = node.instr.const    
    

#['instr', 'X86LoadLocalAddr', ['pattern', [['Pointer'], 'LoadLocalAddr']], ['asmstr', '"    \n        r = self.assigned[0]\n        offset = self.sym.slot.offset\n        if offset == None:\n            offsetStr = \'XXX\'\n        else:\n            offsetStr = str( (offset) ) \n        return \'mov %%ebp, %%%s\\nsub $%s, %%%s\'%(r,offsetStr,r)\n    "'], ['constructor', '"        \n        self.sym = node.instr.sym    \n    "']]
class X86LoadLocalAddr(machineinstruction.MI):
    @classmethod
    def match(cls,dag,node):
        nodestack = [node]
        newchildren = []
        newins = []
        if len(nodestack[-1].instr.assigned) != 1:
            return False
        out = nodestack[-1].instr.assigned
        if type(nodestack[-1].instr.assigned[0]) != ir.Pointer:
            return False
        if type(nodestack[-1].instr) != ir.LoadLocalAddr:
            return False
        node.instr = cls(node)
        node.instr.assigned = out
        node.children = newchildren
        node.instr.read = newins
        return True
    def asm(self):
    
        r = self.assigned[0]
        offset = self.sym.slot.offset
        if offset == None:
            offsetStr = 'XXX'
        else:
            offsetStr = str( (offset) ) 
        return 'mov %%ebp, %%%s\nsub $%s, %%%s'%(r,offsetStr,r)
    
    def __init__(self,node):
        machineinstruction.MI.__init__(self)
        
        self.sym = node.instr.sym    
    

#['instr', 'X86LoadParamAddr', ['pattern', [['Pointer'], 'LoadParamAddr']], ['asmstr', '"    \n        r = self.assigned[0]\n        offset = self.sym.slot.offset\n        if offset == None:\n            offsetStr = \'XXX\'\n        else:\n            offsetStr = str( ( 8 + offset) ) \n        return \'mov %%ebp, %%%s\\nadd $%s, %%%s\'%(r,offsetStr,r)\n    "'], ['constructor', '"        \n        self.sym = node.instr.sym    \n    "']]
class X86LoadParamAddr(machineinstruction.MI):
    @classmethod
    def match(cls,dag,node):
        nodestack = [node]
        newchildren = []
        newins = []
        if len(nodestack[-1].instr.assigned) != 1:
            return False
        out = nodestack[-1].instr.assigned
        if type(nodestack[-1].instr.assigned[0]) != ir.Pointer:
            return False
        if type(nodestack[-1].instr) != ir.LoadParamAddr:
            return False
        node.instr = cls(node)
        node.instr.assigned = out
        node.children = newchildren
        node.instr.read = newins
        return True
    def asm(self):
    
        r = self.assigned[0]
        offset = self.sym.slot.offset
        if offset == None:
            offsetStr = 'XXX'
        else:
            offsetStr = str( ( 8 + offset) ) 
        return 'mov %%ebp, %%%s\nadd $%s, %%%s'%(r,offsetStr,r)
    
    def __init__(self,node):
        machineinstruction.MI.__init__(self)
        
        self.sym = node.instr.sym    
    

#['instr', 'X86LoadGlobalAddr', ['pattern', [['Pointer'], 'LoadGlobalAddr']], ['asmstr', '"leal {instr.sym.name}, %{0}"'], ['constructor', '"        \n        self.sym = node.instr.sym    \n    "']]
class X86LoadGlobalAddr(machineinstruction.MI):
    @classmethod
    def match(cls,dag,node):
        nodestack = [node]
        newchildren = []
        newins = []
        if len(nodestack[-1].instr.assigned) != 1:
            return False
        out = nodestack[-1].instr.assigned
        if type(nodestack[-1].instr.assigned[0]) != ir.Pointer:
            return False
        if type(nodestack[-1].instr) != ir.LoadGlobalAddr:
            return False
        node.instr = cls(node)
        node.instr.assigned = out
        node.children = newchildren
        node.instr.read = newins
        return True
    asmstr = "leal {instr.sym.name}, %{0}"
    def __init__(self,node):
        machineinstruction.MI.__init__(self)
        
        self.sym = node.instr.sym    
    

#['instr', 'X86StoreI32', ['pattern', [[], 'Store', ['Pointer'], ['I32']]], ['asmstr', '"movl %{1}, (%{0})"']]
class X86StoreI32(machineinstruction.MI):
    @classmethod
    def match(cls,dag,node):
        nodestack = [node]
        newchildren = []
        newins = []
        if len(nodestack[-1].instr.assigned) != 0:
            return False
        out = []
        if type(nodestack[-1].instr) != ir.Store:
            return False
        #we can only match nodes with noutputs 1
        if nodestack[-1].children[0][0] != 0:
            return False
        nodestack.append(nodestack[-1].children[0][1])
        #matching terminal ['Pointer']
        if type(nodestack[-1].instr.assigned[0]) != ir.Pointer:
            return False
        newchildren.append((0,nodestack[-1]))
        newins.append(nodestack[-1].instr.assigned[0])
        nodestack.pop()
        #we can only match nodes with noutputs 1
        if nodestack[-1].children[1][0] != 0:
            return False
        nodestack.append(nodestack[-1].children[1][1])
        #matching terminal ['I32']
        if type(nodestack[-1].instr.assigned[0]) != ir.I32:
            return False
        newchildren.append((0,nodestack[-1]))
        newins.append(nodestack[-1].instr.assigned[0])
        nodestack.pop()
        node.instr = cls(node)
        node.instr.assigned = out
        node.children = newchildren
        node.instr.read = newins
        return True
    asmstr = "movl %{1}, (%{0})"
    def __init__(self,node):
        machineinstruction.MI.__init__(self)
        pass

#['instr', 'X86StorePointer', ['pattern', [[], 'Store', ['Pointer'], ['Pointer']]], ['asmstr', '"movl %{1}, (%{0})"']]
class X86StorePointer(machineinstruction.MI):
    @classmethod
    def match(cls,dag,node):
        nodestack = [node]
        newchildren = []
        newins = []
        if len(nodestack[-1].instr.assigned) != 0:
            return False
        out = []
        if type(nodestack[-1].instr) != ir.Store:
            return False
        #we can only match nodes with noutputs 1
        if nodestack[-1].children[0][0] != 0:
            return False
        nodestack.append(nodestack[-1].children[0][1])
        #matching terminal ['Pointer']
        if type(nodestack[-1].instr.assigned[0]) != ir.Pointer:
            return False
        newchildren.append((0,nodestack[-1]))
        newins.append(nodestack[-1].instr.assigned[0])
        nodestack.pop()
        #we can only match nodes with noutputs 1
        if nodestack[-1].children[1][0] != 0:
            return False
        nodestack.append(nodestack[-1].children[1][1])
        #matching terminal ['Pointer']
        if type(nodestack[-1].instr.assigned[0]) != ir.Pointer:
            return False
        newchildren.append((0,nodestack[-1]))
        newins.append(nodestack[-1].instr.assigned[0])
        nodestack.pop()
        node.instr = cls(node)
        node.instr.assigned = out
        node.children = newchildren
        node.instr.read = newins
        return True
    asmstr = "movl %{1}, (%{0})"
    def __init__(self,node):
        machineinstruction.MI.__init__(self)
        pass

#['instr', 'X86DerefI32', ['pattern', [['I32'], 'Deref', ['Pointer']]], ['asmstr', '"mov (%{1}),%{0} "']]
class X86DerefI32(machineinstruction.MI):
    @classmethod
    def match(cls,dag,node):
        nodestack = [node]
        newchildren = []
        newins = []
        if len(nodestack[-1].instr.assigned) != 1:
            return False
        out = nodestack[-1].instr.assigned
        if type(nodestack[-1].instr.assigned[0]) != ir.I32:
            return False
        if type(nodestack[-1].instr) != ir.Deref:
            return False
        #we can only match nodes with noutputs 1
        if nodestack[-1].children[0][0] != 0:
            return False
        nodestack.append(nodestack[-1].children[0][1])
        #matching terminal ['Pointer']
        if type(nodestack[-1].instr.assigned[0]) != ir.Pointer:
            return False
        newchildren.append((0,nodestack[-1]))
        newins.append(nodestack[-1].instr.assigned[0])
        nodestack.pop()
        node.instr = cls(node)
        node.instr.assigned = out
        node.children = newchildren
        node.instr.read = newins
        return True
    asmstr = "mov (%{1}),%{0} "
    def __init__(self,node):
        machineinstruction.MI.__init__(self)
        pass

#['instr', 'X86DerefPointer', ['pattern', [['Pointer'], 'Deref', ['Pointer']]], ['asmstr', '"mov (%{1}),%{0} "']]
class X86DerefPointer(machineinstruction.MI):
    @classmethod
    def match(cls,dag,node):
        nodestack = [node]
        newchildren = []
        newins = []
        if len(nodestack[-1].instr.assigned) != 1:
            return False
        out = nodestack[-1].instr.assigned
        if type(nodestack[-1].instr.assigned[0]) != ir.Pointer:
            return False
        if type(nodestack[-1].instr) != ir.Deref:
            return False
        #we can only match nodes with noutputs 1
        if nodestack[-1].children[0][0] != 0:
            return False
        nodestack.append(nodestack[-1].children[0][1])
        #matching terminal ['Pointer']
        if type(nodestack[-1].instr.assigned[0]) != ir.Pointer:
            return False
        newchildren.append((0,nodestack[-1]))
        newins.append(nodestack[-1].instr.assigned[0])
        nodestack.pop()
        node.instr = cls(node)
        node.instr.assigned = out
        node.children = newchildren
        node.instr.read = newins
        return True
    asmstr = "mov (%{1}),%{0} "
    def __init__(self,node):
        machineinstruction.MI.__init__(self)
        pass

#['instr', 'X86Branch', ['pattern', [[], 'Branch', ['I32']]], ['asmstr', '"\n        if self.successors[0] != None and self.successors[1] == None:\n            return \'test %%%s,%%%s\\njnz .%s\'%(self.read[0],self.read[0],self.successors[0])\n        elif self.successors[0] == None and self.successors[1] != None:\n            return \'test %%%s,%%%s\\njz .%s\'%(self.read[0],self.read[0],self.successors[1])\n        else:\n            return \'test %%%s,%%%s\\njnz .%s\\njmp .%s\'%(self.read[0],self.read[0],self.successors[0],self.successors[1])\n        "'], ['constructor', '"        \n        self.successors = node.instr.successors\n        "']]
class X86Branch(machineinstruction.MI):
    @classmethod
    def match(cls,dag,node):
        nodestack = [node]
        newchildren = []
        newins = []
        if len(nodestack[-1].instr.assigned) != 0:
            return False
        out = []
        if type(nodestack[-1].instr) != ir.Branch:
            return False
        #we can only match nodes with noutputs 1
        if nodestack[-1].children[0][0] != 0:
            return False
        nodestack.append(nodestack[-1].children[0][1])
        #matching terminal ['I32']
        if type(nodestack[-1].instr.assigned[0]) != ir.I32:
            return False
        newchildren.append((0,nodestack[-1]))
        newins.append(nodestack[-1].instr.assigned[0])
        nodestack.pop()
        node.instr = cls(node)
        node.instr.assigned = out
        node.children = newchildren
        node.instr.read = newins
        return True
    def asm(self):

        if self.successors[0] != None and self.successors[1] == None:
            return 'test %%%s,%%%s\njnz .%s'%(self.read[0],self.read[0],self.successors[0])
        elif self.successors[0] == None and self.successors[1] != None:
            return 'test %%%s,%%%s\njz .%s'%(self.read[0],self.read[0],self.successors[1])
        else:
            return 'test %%%s,%%%s\njnz .%s\njmp .%s'%(self.read[0],self.read[0],self.successors[0],self.successors[1])
        
    def __init__(self,node):
        machineinstruction.MI.__init__(self)
        
        self.successors = node.instr.successors
        

#['instr', 'X86Jmp', ['pattern', [[], 'Jmp']], ['asmstr', '"        \n        if self.successors[0] == None:\n            return \'\'\n        else:\n            return \'jmp .%s\' % self.successors[0]\n     "'], ['constructor', '"        \n        self.successors = node.instr.successors\n        "']]
class X86Jmp(machineinstruction.MI):
    @classmethod
    def match(cls,dag,node):
        nodestack = [node]
        newchildren = []
        newins = []
        if len(nodestack[-1].instr.assigned) != 0:
            return False
        out = []
        if type(nodestack[-1].instr) != ir.Jmp:
            return False
        node.instr = cls(node)
        node.instr.assigned = out
        node.children = newchildren
        node.instr.read = newins
        return True
    def asm(self):
        
        if self.successors[0] == None:
            return ''
        else:
            return 'jmp .%s' % self.successors[0]
     
    def __init__(self,node):
        machineinstruction.MI.__init__(self)
        
        self.successors = node.instr.successors
        

matchableInstructions = [
    X86Add,
    X86Sub,
    X86SHLI32,
    X86SHRI32,
    X86IMulI32,
    X86IDivI32,
    X86IModI32,
    X86NotI32,
    X86Mov,
    X86NeI32,
    X86LtI32,
    X86GtI32,
    X86EqI32,
    X86LoadConstantI32,
    X86LoadLocalAddr,
    X86LoadParamAddr,
    X86LoadGlobalAddr,
    X86StoreI32,
    X86StorePointer,
    X86DerefI32,
    X86DerefPointer,
    X86Branch,
    X86Jmp,
]
