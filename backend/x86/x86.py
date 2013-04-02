from backend import  ir

from backend import standardmachine
from backend import machineinstruction

from backend.instructionselector import *
from backend.selectiondag import *


class MultI32(machineinstruction.MI):
    
    @staticmethod
    def match(dag,node):
        
        if type(node.instr) != ir.Binop or node.instr.op != '*':
            return None
        
        if len(node.ins) != 2:
            return None
        
        if type(node.instr.read[0]) != ir.I32:
            return None
        
        if type(node.instr.read[1]) != ir.I32:
            return None
        
        if type(node.instr.assigned[0]) != ir.I32:
            return None
        
        def repl():
            m = MultI32()
            m.assigned = node.instr.assigned
            m.read = node.instr.read
            node.instr = m
        
        return InstructionMatch(repl,1)

    def asm(self):
        return "mul %s %s %s"%(self.assigned[0],self.read[0],self.read[1])

class X86LoadConstantI32(machineinstruction.MI):
    
    def __init__(self,const):
        machineinstruction.MI.__init__(self)
        self.const = const
    
    @staticmethod
    def match(dag,node):
        
        if type(node.instr) != ir.LoadConstant:
            return None
        
        if len(node.ins) != 0:
            return None
        
        if type(node.instr.assigned[0]) != ir.I32:
            return None
        
        def repl():
            ld = X86LoadConstantI32(node.instr.const)
            ld.assigned = node.instr.assigned
            ld.read = node.instr.read
            node.instr = ld
        
        return InstructionMatch(repl,1)

    def asm(self):
        return "mov %d,%%%s"%(self.const.value,self.assigned[0])

class X86MovI32(machineinstruction.MI):

    @staticmethod
    def match(dag,node):
        
        if type(node.instr) != ir.Move:
            return None
        
        if len(node.ins) != 1:
            return None
            
        if type(node.instr.read[0]) != ir.I32:
            return None
        
        if type(node.instr.assigned[0]) != ir.I32:
            return None
        
        
        def repl():
            mov = X86MovI32()
            mov.assigned = node.instr.assigned
            mov.read = node.instr.read
            node.instr = mov
        
        return InstructionMatch(repl,1)

    def asm(self):
        return "mov %%%s,%%%s"%(self.read[0],self.assigned[0])


class X86AddI32(machineinstruction.MI):
    
    
    @staticmethod
    def match(dag,node):
        
        
        if type(node.instr) != ir.Binop or node.instr.op != '+':
            return None
        
        if len(node.ins) != 2:
            return None
        
        if type(node.instr.assigned[0]) != ir.I32:
            return None
        
        if type(node.instr.read[0]) != ir.I32:
            return None
            
        if type(node.instr.read[1]) != ir.I32:
            return None
        
        if node.instr.assigned[0] != node.instr.read[0]:
            return None
        
        def repl():
            add = X86AddI32()
            add.assigned = node.instr.assigned
            add.read = node.instr.read
            node.instr = add
        
        return InstructionMatch(repl,1)

    def asm(self):
        return "add %%%s,%%%s"%(self.read[1],self.assigned[0])

class X86LoadLocalAddr(machineinstruction.MI):
    
    
    @staticmethod
    def match(dag,node):
        
        if type(node.instr) != ir.LoadLocalAddr:
            return None
        
        
        def repl():
            lla = X86LoadLocalAddr()
            lla.assigned = node.instr.assigned
            lla.sym = node.instr.sym
            node.instr = lla
            
        
        return InstructionMatch(repl,1)

    def asm(self):
        r = self.assigned[0]
        return "mov %s, ebp + %s "%(r,self.sym.slot.offset)

class X86LoadLocalI32(machineinstruction.MI):
    
    
    @staticmethod
    def match(dag,node):
        
        
        if type(node.instr) != ir.Deref:
            return None
        
        loadAddr = node.ins[0].edge.tail.parent
        
        
        if type(loadAddr.instr) != ir.LoadLocalAddr:
            return None
        
        
        def repl():
            
            newnode = SDNode()
            lla = X86LoadLocalI32()
            lla.assigned = node.instr.assigned
            lla.sym = loadAddr.instr.sym
            newnode.instr = lla
            
            oldedges = list(node.outs[0].edges)
            for edge in oldedges:
                edge.tail = newnode.outs[0]
            
            
            
        
        return InstructionMatch(repl,2)

    def asm(self):
        r = self.assigned[0]
        return "mov %s(%%ebp), %%%s "%(-1*self.sym.slot.offset,r)


class X86StoreLocalI32(machineinstruction.MI):
    
    
    @staticmethod
    def match(dag,node):
        
        if type(node.instr) != ir.Store:
            return None
        
        loadAddr = node.ins[0].edge.tail.parent
        
        
        if type(loadAddr.instr) != ir.LoadLocalAddr:
            return None
        
        oldsourceport = node.ins[1].edge.tail
        
        def repl():
            sla = X86StoreLocalI32()
            sla.read = [None]
            sla.sym = loadAddr.instr.sym
            node.ins[1].edge.remove()
            node.instr = sla
            SDDataEdge(node.ins[0],oldsourceport)
        return InstructionMatch(repl,2)

    def asm(self):
        r = self.read[0]
        return "mov %%%s, %s(%%ebp) "%(r,-1 * self.sym.slot.offset)


class X86LoadI32(machineinstruction.MI):
    
    @staticmethod
    def match(dag,node):
        
        if type(node.instr) != ir.Deref:
            return None
        
        if len(node.ins) != 1:
            return None
        
        if type(node.instr.assigned[0]) != ir.I32:
            return None
        
        def repl():
            ld = X86LoadI32()
            ld.read = node.instr.read
            ld.assigned = node.instr.assigned
            node.instr = ld
            
        return InstructionMatch(repl,1)

    def asm(self):
        return "mov %s, [%s]"%(self.assigned[0],self.read[0])

class X86StoreI32(machineinstruction.MI):
    
    @staticmethod
    def match(dag,node):
        
        if type(node.instr) != ir.Store:
            return None
        
        if len(node.ins) != 2:
            return None
        
        if type(node.instr.read[0]) != ir.I32:
            return None
        
        def repl():
            st = X86StoreI32()
            st.read = node.instr.read
            st.assigned = node.instr.assigned
            node.instr = st
            
        return InstructionMatch(repl,1)

    def asm(self):
        return "mov [%s], %s"%(self.read[0],self.read[1])

class X86PushI32(machineinstruction.MI):
    
    def asm(self):
        return "push %s"%(self.read[0])

class X86StackLoadI32(machineinstruction.MI):
    
    def asm(self):
        return "mov %s, [ebp + XXX]"%(self.assigned[0])


class X86StackSaveI32(machineinstruction.MI):
    
    def asm(self):
        return "mov [ebp + XXX], %s "%(self.read[0])
        
class X86Jmp(machineinstruction.MI):
    
    def asm(self):
        return "jmp %s"%(self.getSuccessors()[0].name)


class X86Branch(machineinstruction.MI):
    
    def asm(self):
        
        if self.successors[0] != None and self.successors[1] == None:
            return "test %s; jnz %s"%(self.read[0],self.successors[0])
        elif self.successors[0] == None and self.successors[1] != None:
            return "test %s; jz %s"%(self.read[0],successors[1])
        else:
            return "test %s; jnz %s; jmp %s"%(self.read[0],self.successors[0],successors[1])

class X86Nop(machineinstruction.MI):
    def asm(self):
        return "nop"

class X86Ret(machineinstruction.MI):
    def asm(self):
        return "ret"

class X86Enter(machineinstruction.MI):
    def __init__(self,stackSize):
        machineinstruction.MI.__init__(self)
        self.stackSize = stackSize
    def asm(self):
        return "pushl %%ebp; movl %%esp,%%ebp;  subl %s,%%esp;" % self.stackSize

class X86Leave(machineinstruction.MI):
    def __init__(self, stackSize):
        machineinstruction.MI.__init__(self)
        self.stackSize = stackSize
    def asm(self):
        return "movl %ebp, %esp;popl %ebp;"


instructions = [
    X86AddI32,
#    MultI32,
    X86MovI32,
    X86LoadI32,
    X86LoadConstantI32,
    X86LoadLocalI32,
    X86LoadLocalAddr,
    X86StoreLocalI32,
#    X86StoreI32,
#    X86PushI32,
]


registers = [
    standardmachine.Register('eax',[ir.I32]),
    standardmachine.Register('ebx',[ir.I32]),
    standardmachine.Register('ecx',[ir.I32]),
    standardmachine.Register('edx',[ir.I32]),
]

def getRegisterByName(n):
    for r in registers:
        if r.name == n:
            return r
    raise Exception("bad register %s"%n)

class X86(standardmachine.StandardMachine):
    
    
    def getEpilog(self,stackSize):
        return [X86Leave(stackSize)]
    
    def getProlog(self,stackSize):
        return [X86Enter(stackSize)]
    
    
    def getInstructions(self):
        return instructions
        
    def getRegisters(self):
        return registers
    
    def getSpillCode(self,reg,ss1,ss2):
        
        start = [X86StackSaveI32(),X86StackLoadI32()]
        end = [X86StackSaveI32(),X86StackLoadI32()]
        
        start[0].read = [reg]
        start[1].assigned = [reg]
        end[0].read = [reg]
        end[1].assigned = [reg]
        
        return start,end
    
    def applyDagFixups(self,dag):
        
        print("x86 fixups")
        newnodes = []
        for n in dag.nodes:
            if type(n.instr) == ir.Binop and n.instr.op == '+':
                print("fixing up binop in DAG")
                #add a,b,c
                # -------
                #copy a,b
                #add a,a,c
                copy = SDNode()
                copy.instr = ir.Move(None,None)
                
                a = n.outs[0].var
                b = n.ins[0].var
                
                oldedge = n.ins[0].edge
                port = oldedge.tail
                oldedge.remove()
                e1 = SDDataEdge(n.ins[0],copy.outs[0])
                e2 = SDDataEdge(copy.ins[0],port)
                e1.var = a
                e2.var = b
                
                newnodes.append(copy)
                    
        for n in newnodes:
            dag.nodes.append(n)
    
    
    def fixReturns(self,dag):
        
        newnodes = []
        for n in dag.nodes:
            if type(n.instr) == ir.Ret:
                ret = n
                eax = getRegisterByName('eax')
                oldvar = ret.ins[0].var
                oldtail = ret.ins[0].edge.tail
                ret.ins[0].edge.remove()
                
                copy = SDNode()
                instr = X86MovI32()
                instr.read = [oldvar]
                instr.assigned = [eax]
                copy.instr = instr
                
                e1 = SDDataEdge(copy.ins[0],oldtail)
                e2 = SDDataEdge(ret.ins[0],copy.outs[0])
                
                e1.var = oldvar
                e2.var = eax
                
                newnodes.append(copy)
        
        for n in newnodes:
            dag.nodes.append(n)

    def fixCalls(self,dag):
        
        newnodes = []
        for n in dag.nodes:
            if type(n.instr) == ir.Call:
                call = n
                eax = getRegisterByName('eax')
                
                prevPush = None
                for inport in call.ins:
                    outport = inport.edge.tail
                    node = SDNode()
                    newnodes.append(node)
                    p = X86PushI32()
                    v = inport.var
                    inport.edge.remove()
                    p.read = [None]
                    node.instr = p
                    e = SDDataEdge(node.ins[0],outport)
                    e.var = v
                    node.control.append(call)
                    if prevPush != None:
                        prevPush.control.append(node)
                    prevPush = node
                
                if len(call.outs) :
                    deps = [ x for x in call.outs[0].edges ]
                    heads = [ x.head for x in call.outs[0].edges ]
                    oldvars = [ h.var for h in heads]
                    for e in deps:
                        e.remove()
                    copy = SDNode()
                    instr = X86MovI32()
                    instr.read = [None]
                    instr.assigned = [None]
                    copy.instr = instr
                    e1 = SDDataEdge(copy.ins[0],call.outs[0])
                    e1.var = eax
                    for k,h in enumerate(heads):
                        e2 = SDDataEdge(h,copy.outs[0])
                        e2.var = oldvars[k]
                    newnodes.append(copy)
        
        for n in newnodes:
            dag.nodes.append(n)
    
    
    def callingConventions(self, dag):
        self.fixReturns(dag)
        self.fixCalls(dag)
    
    
    def terminatorSelection(self,instr):
        
        if type(instr) == ir.Jmp:
            
            next = instr.getSuccessors()[0]
            if next == None:
                return X86Nop()
            newJump = X86Jmp()
            newJump.setSuccessors(instr.getSuccessors())
            return newJump
            
            
        elif type(instr) == ir.Branch:
            
            trueBlock,falseBlock = instr.getSuccessors()
            if trueBlock == None and falseBlock == None:
                return X86Nop()
            
            newBranch = X86Branch()
            newBranch.setSuccessors(instr.getSuccessors())
            newBranch.read = instr.read
            return newBranch
        
        elif type(instr) == ir.Ret:
            return X86Ret()
        else:
            raise Exception("unreachable branch selection - %s" % instr)
            
            
            
            
            


