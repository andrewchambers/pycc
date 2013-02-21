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
        return "mov %s,%d"%(self.assigned[0],self.const.value)

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
        return "mov %s,%s"%(self.assigned[0],self.read[0])


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
        return "add %s,%s"%(self.assigned[0],self.read[1])

class X86LoadLocalAddr(machineinstruction.MI):
    
    
    @staticmethod
    def match(dag,node):
        
        if type(node.instr) != ir.LoadLocalAddr:
            return None
        
        
        def repl():
            lla = X86LoadLocalAddr()
            lla.assigned = node.instr.assigned
            node.instr = lla
        
        return InstructionMatch(repl,1)

    def asm(self):
        return "mov %s, ebp + XXX "%(self.assigned[0])

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


instructions = [
    X86AddI32,
#    MultI32,
    X86MovI32,
    X86LoadI32,
    X86LoadConstantI32,
    X86LoadLocalAddr,
    X86StoreI32,
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
    
    def getInstructions(self):
        return instructions
        
    def getRegisters(self):
        return registers
        
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
            dag.nodes.add(n)
    
    
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
            dag.nodes.add(n)

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
            dag.nodes.add(n)

    
    def callingConventions(self, dag):
        self.fixReturns(dag)
        self.fixCalls(dag)
