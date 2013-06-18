
from patterns import *


import basicblock
import ir
import selectiondag


v = {
     'a' : ir.I32(),
     'b' : ir.I32(),
     'c' : ir.I32(),
     'd' : ir.I32(),
     'e' : ir.I32(),
     'f' : ir.I32(),
     'p1' : ir.Pointer(),
     'p2' : ir.Pointer(),
}

b = basicblock.BasicBlock()

b.opcodes = [
    ir.Binop('+',v['c'],v['a'],v['b']),
    ir.Binop('-',v['d'],v['c'],v['b']),
    ir.Store(v['p1'],v['a']),
]


def test_patterns():
    sd = selectiondag.SelectionDag(b,[v['c']])
    pat = Set(I32,Binop('+',I32,I32))
    pat2 = Store(Pointer,I32)
    
    patternmap = {
        b[0] : pat,
        b[2] : pat2,
    }
    
    for instr in patternmap:    
        p = patternmap[instr]
        for n in sd.nodes:
            if n.instr == instr:
                assert(p.match(n) == True)
            else:
                assert(p.match(n) == False)
