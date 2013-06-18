from backend import machineinstruction
from backend.patterns import *

import x86

class X86MovI32(machineinstruction.MI):
    pattern = Set(I32,Move(I32))
    asmstr = "mov %{1},%{0}"


class X86MovI8(machineinstruction.MI):
    pattern = Set(I8,Move(I8))
    asmstr = "mov %{1},%{0}"

class X86AndI32(machineinstruction.MI):
    pattern = Set(I32,Binop('&',I32,I32))
    asmstr = "and %{2},%{0}"

class X86AndI8(machineinstruction.MI):
    pattern = Set(I8,Binop('&',I8,I8))
    asmstr = "and %{2},%{0}"


class X86Ptr(machineinstruction.MI):
    pattern = Set(Pointer,Move(Pointer))
    asmstr = "mov %{1},%{0}"
    
class X86AddI32(machineinstruction.MI):
    pattern = Set(I32,Binop('+',I32,I32))
    asmstr = "add %{2},%{0}"

class X86AddI8(machineinstruction.MI):
    pattern = Set(I8,Binop('+',I8,I8))
    asmstr = "add %{2},%{0}"

class X86AddPointer(machineinstruction.MI):
    pattern = Set(Pointer,Binop('+',Pointer,I32))
    asmstr = "add %{2},%{0}"

class X86SubI32(machineinstruction.MI):
    pattern = Set(I32,Binop('-',I32,I32))
    asmstr = "sub %{2},%{0}"

class X86SubI8(machineinstruction.MI):
    pattern = Set(I8,Binop('-',I8,I8))
    asmstr = "sub %{2},%{0}"

class X86IMulI32(machineinstruction.MI):
    pattern = Set(I32,Binop('*',I32,I32))
    asmstr = "mul %{3}"

class X86IDivI32(machineinstruction.MI):
    pattern = Set(I32,Binop('/',I32,I32))
    asmstr = "cdq\nidiv %{3}"
    
    #XXX should be refactored. getDisallowedRegisters?
    # this fixes the problem of registers that shouldnt have inputs put into
    def getPreClobberedRegisters(self):
        return [x86.getRegisterByName('edx')]

class X86IModI32(machineinstruction.MI):
    pattern = Set(I32,Binop('%',I32,I32))
    asmstr = "cdq\nidiv %{3}"
    
    def getPreClobberedRegisters(self):
        return [x86.getRegisterByName('edx')]

class X86SHLI32(machineinstruction.MI):
    pattern = Set(I32,Binop('<<',I32,I32))
    asmstr = "shl %cl,%{0}"
    
class X86SHRI32(machineinstruction.MI):
    pattern = Set(I32,Binop('>>',I32,I32))
    asmstr = "shr %cl,%{0}"

class X86SHRI8(machineinstruction.MI):
    pattern = Set(I8,Binop('>>',I8,I8))
    asmstr = "shr %cl,%{0}"

class X86SHLI8(machineinstruction.MI):
    pattern = Set(I8,Binop('<<',I8,I8))
    asmstr = "shl %cl,%{0}"

class X86LoadGlobalAddr(machineinstruction.MI):
    pattern = Set(Pointer,LoadGlobalAddr())
    asmstr = "leal {instr.sym.name}, %{0}"
    
    def __init__(self,node):
        machineinstruction.MI.__init__(self)
        self.sym = node.instr.sym   

class X86LoadLocalAddr(machineinstruction.MI):
    pattern = Set(Pointer,LoadLocalAddr())
    def __init__(self,node):
        machineinstruction.MI.__init__(self)
        self.sym = node.instr.sym
    def asm(self):
        r = self.assigned[0]
        offset = self.sym.slot.offset
        if offset == None:
            offsetStr = 'XXX'
        else:
            offsetStr = str( (offset) ) 
        return 'mov %%ebp, %%%s\nsub $%s, %%%s'%(r,offsetStr,r)      
    
    def getStackSlots(self):
        return [self.sym.slot]

class X86LoadParamAddr(machineinstruction.MI):
    pattern = Set(Pointer,LoadParamAddr())
    def __init__(self,node):
        machineinstruction.MI.__init__(self)
        self.sym = node.instr.sym
    def asm(self):
        r = self.assigned[0]
        offset = self.sym.slot.offset
        if offset == None:
            offsetStr = 'XXX'
        else:
            offsetStr = str( ( 8 + offset) ) 
        return 'mov %%ebp, %%%s\nadd $%s, %%%s'%(r,offsetStr,r)

class X86StoreI32(machineinstruction.MI):
    pattern = Store(Pointer,I32)
    asmstr = "mov %{1},(%{0})"

class X86StoreI8(machineinstruction.MI):
    pattern = Store(Pointer,I8)
    asmstr = "mov %{1},(%{0})"
    
 
class X86StorePointer(machineinstruction.MI):
    pattern = Store(Pointer,Pointer)
    asmstr = "mov %{1},(%{0})"

class X86DerefI32(machineinstruction.MI):
    pattern = Set(I32,Deref(Pointer))
    asmstr = "mov (%{1}),%{0}"

class X86DerefI8(machineinstruction.MI):
    pattern = Set(I8,Deref(Pointer))
    asmstr = "mov (%{1}),%{0}"   

class X86DerefPointer(machineinstruction.MI):
    pattern = Set(Pointer,Deref(Pointer))
    asmstr = "mov (%{1}),%{0}"

class X86LoadConstantI32(machineinstruction.MI):
    pattern = Set(I32,LoadConstant())
    asmstr = "mov ${instr.const},%{0}"
    def __init__(self,node):
        machineinstruction.MI.__init__(self)
        self.const = node.instr.const.value

class X86LoadConstantI8(machineinstruction.MI):
    pattern = Set(I8,LoadConstant())
    asmstr = "mov ${instr.const},%{0}"
    def __init__(self,node):
        machineinstruction.MI.__init__(self)
        self.const = node.instr.const.value

class X86BrI32(machineinstruction.MI):
    pattern = Branch(I32)
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

class X86BrI8(machineinstruction.MI):
    pattern = Branch(I8)
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



class X86Jmp(machineinstruction.MI):
    pattern = Jmp()
    def asm(self):
        if self.successors[0] == None:
            return '#jmp fallthrough'
        else:
            return 'jmp .%s'%(self.successors[0])

    
    def __init__(self,node):  
        machineinstruction.MI.__init__(self)
        self.successors = node.instr.successors

class X86Cmp(machineinstruction.MI):
    asmstr =""" 
    cmp %{2},%{1}
    {instr.jmpinstr} {instr.branch}
    xor %{0},%{0}
    jmp {instr.exit}
    {instr.branch}:
    xor %{0},%{0}
    inc %{0}
    {instr.exit}:
    """
    
    def __repr__(self):
        return str(type(self))
    
    def __init__(self,node):
        machineinstruction.MI.__init__(self)
        self.branch = x86.newLocalLabel()
        self.exit = x86.newLocalLabel()


class X86NeI32(X86Cmp):
    pattern = Set(I32,Binop("!=",I32,I32))
    jmpinstr = 'jne'

class X86EqI32(X86Cmp):
    pattern = Set(I32,Binop("==",I32,I32))
    jmpinstr = 'je'

class X86EqI8(X86Cmp):
    pattern = Set(I8,Binop("==",I8,I8))
    jmpinstr = 'je'
  
  
class X86JgI32(X86Cmp):
    pattern = Set(I32,Binop(">",I32,I32))
    jmpinstr = 'jg'  

class X86JlI32(X86Cmp):
    pattern = Set(I32,Binop("<",I32,I32))
    jmpinstr = 'jl'  

class X86SxI8toI32(machineinstruction.MI):
    pattern = Set(I32,Unop("sx",I8))
    asmstr = "movsx %{1},%{0}"

class X86ZxI8toI32(machineinstruction.MI):
    pattern = Set(I32,Unop("zx",I8))
    asmstr = "movzx %{1},%{0}"

class X86TrI32toI8(machineinstruction.MI):
    pattern = Set(I8,Unop("tr",I32))
    asmstr = "mov %{1},%{0}"
    def asm(self):
        if self.read[0].isPhysical():
            #hack, convert eax etc, to low byte
            r = self.read[0].name[1] + 'l'
        else:
            r = str(self.read[0])
        return "mov %{1},%{0}".format(self.assigned[0],r)



matchableInstructions = []

for cls in globals().values():
    try:
        if issubclass(cls,machineinstruction.MI) and hasattr(cls,'pattern'):
            matchableInstructions.append(cls)
    except TypeError:
        pass

print matchableInstructions

