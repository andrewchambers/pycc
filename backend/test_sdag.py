

import selectiondag
import basicblock
import ir
import vis.dagvis as dagvis



def test_selectiondag():
    
    bb = basicblock.BasicBlock()
    
    a = ir.I32()
    b = ir.I32()
    c = ir.I32()
    
    d = ir.I32()
    e = ir.I32()
    f = ir.I32()
    
    h = ir.I32()
    
    bb.append(ir.Binop('+',c,a,b))
    bb.append(ir.Binop('-',ir.I32(),a,b))
    bb.append(ir.Store(ir.Pointer(),a))
    subinstr = ir.Binop('+',d,e,f)
    bb.append(subinstr)
    headinstr = ir.Binop('+',h,c,d)
    bb.append(headinstr)
    bb.append(ir.Jmp(bb))
    
    sd = selectiondag.SelectionDag(bb,set([c]))
    
    sd.sanityCheck()
    
    #dagvis.showSelDAG(sd)
    
    assert(sd.root.instr == bb[-1])
    ordered = sd.ordered()
    
    assert(ordered[-1].instr == bb[-1])
    assert(len(ordered) == 15)
    
    
    
    
    
    
    
    
