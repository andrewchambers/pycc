
import valtracker
import types
from backend import basicblock
from backend import ir
import operatorgen


def test_removeLValness1():
    t1 = types.Int(signed=True)
    v = valtracker.ValTracker(True,t1,None)
    v.createVirtualReg()
    bb = basicblock.BasicBlock()
    newv = operatorgen.removeLValness(bb,v)
    
    assert(newv != v)
    assert(type(bb[0]) == ir.Deref)
    assert(bb[0].read[0] == v.reg)
    assert(bb[0].assigned[0] == newv.reg)
    assert(len(bb) == 1)
    assert(newv.lval == False)
    assert(type(newv.type) == types.Int)
    assert(newv.type.signed == True)

def test_removeLValness2():
    t1 = types.Int(signed=True)
    v = valtracker.ValTracker(False,t1,None)
    v.createVirtualReg()
    bb = basicblock.BasicBlock()
    newv = operatorgen.removeLValness(bb,v)
    assert(newv == v)
    assert(len(bb) == 0)




def test_promotetoint1():
    t = types.Int(signed=True)
    v = valtracker.ValTracker(False,t,None)
    v.createVirtualReg()
    bb = basicblock.BasicBlock()
    newv = operatorgen.promoteToInt(bb,v)
    
    assert(newv == v)
    assert(len(bb) == 0)
    
    t = types.Int(signed=False)
    v = valtracker.ValTracker(False,t,None)
    v.createVirtualReg()
    bb = basicblock.BasicBlock()
    newv = operatorgen.promoteToInt(bb,v)
    
    assert(newv == v)
    assert(len(bb) == 0)
    
    t = types.Int(signed=False)
    v = valtracker.ValTracker(True,t,None)
    v.createVirtualReg()
    bb = basicblock.BasicBlock()
    newv = operatorgen.promoteToInt(bb,v)
    
    assert(type(bb[0]) == ir.Deref)
    assert(len(bb) == 1)
    
    
    t = types.Char(signed=False)
    v = valtracker.ValTracker(False,t,None)
    v.createVirtualReg()
    assert(type(v.reg) == ir.I8)
    bb = basicblock.BasicBlock()
    newv = operatorgen.promoteToInt(bb,v)
    
    assert(len(bb) == 1)
    assert(newv.type.signed == True)
    assert(type(newv.type) == types.Int)
    assert(type(bb[0]) == ir.Unop)
    assert(bb[0].read[0] == v.reg)
    assert(bb[0].assigned[0] == newv.reg)
    assert(bb[0].op == 'zx')
    assert(len(bb) == 1)

    t = types.Char(signed=True)
    v = valtracker.ValTracker(False,t,None)
    v.createVirtualReg()
    assert(type(v.reg) == ir.I8)
    bb = basicblock.BasicBlock()
    newv = operatorgen.promoteToInt(bb,v)
    
    assert(len(bb) == 1)
    assert(newv.type.signed == True)
    assert(type(newv.type) == types.Int)
    assert(type(bb[0]) == ir.Unop)
    assert(bb[0].read[0] == v.reg)
    assert(bb[0].assigned[0] == newv.reg)
    assert(bb[0].op == 'sx')
    assert(len(bb) == 1)

    t = types.ShortInt(signed=False)
    v = valtracker.ValTracker(False,t,None)
    v.createVirtualReg()
    assert(type(v.reg) == ir.I16)
    bb = basicblock.BasicBlock()
    newv = operatorgen.promoteToInt(bb,v)
    
    assert(len(bb) == 1)
    assert(newv.type.signed == True)
    assert(type(newv.type) == types.Int)
    assert(type(bb[0]) == ir.Unop)
    assert(bb[0].read[0] == v.reg)
    assert(bb[0].assigned[0] == newv.reg)
    assert(bb[0].op == 'zx')
    assert(len(bb) == 1)

    t = types.ShortInt(signed=True)
    v = valtracker.ValTracker(False,t,None)
    v.createVirtualReg()
    assert(type(v.reg) == ir.I16)
    bb = basicblock.BasicBlock()
    newv = operatorgen.promoteToInt(bb,v)
    
    assert(len(bb) == 1)
    assert(newv.type.signed == True)
    assert(type(newv.type) == types.Int)
    assert(type(bb[0]) == ir.Unop)
    assert(bb[0].read[0] == v.reg)
    assert(bb[0].assigned[0] == newv.reg)
    assert(bb[0].op == 'sx')
    assert(len(bb) == 1)




def test_arithconversion():
    t1,t2 = types.Int(signed=True),types.Int(signed=True)
    v1,v2 = valtracker.ValTracker(False,t1,None),valtracker.ValTracker(False,t2,None)
    v1.createVirtualReg()
    v2.createVirtualReg()
    bb = basicblock.BasicBlock()
    
    _v1,_v2 = operatorgen.arithConversion(bb,v1,v2)
    
    assert(len(bb) == 0)
    assert(_v1.type.strictTypeMatch(t1))
    assert(_v2.type.strictTypeMatch(t2))
    assert(_v2.type.strictTypeMatch(_v1.type))
    assert(type(_v2.type) == types.Int)
    assert(_v1.type.signed)
    assert(_v2.type.signed)

    t1,t2 = types.Int(signed=False),types.Char(signed=True)
    v1,v2 = valtracker.ValTracker(False,t1,None),valtracker.ValTracker(False,t2,None)
    v1.createVirtualReg()
    v2.createVirtualReg()
    bb = basicblock.BasicBlock()
    
    print v2.type,v1.type
    print v2.type.signed,v1.type.signed
    
    _v1,_v2 = operatorgen.arithConversion(bb,v1,v2)
    
    assert(len(bb) == 1)
    print _v2.type,_v1.type
    print _v2.type.signed,_v1.type.signed
    assert(_v2.type.strictTypeMatch(_v1.type))
    assert(type(_v2.type) == types.Int)
    assert(_v1.type.signed == False)
    assert(_v2.type.signed == False)
    
    
    t1,t2 = types.Char(signed=True),types.Int(signed=False)
    v1,v2 = valtracker.ValTracker(False,t1,None),valtracker.ValTracker(False,t2,None)
    v1.createVirtualReg()
    v2.createVirtualReg()
    bb = basicblock.BasicBlock()
    
    _v1,_v2 = operatorgen.arithConversion(bb,v1,v2)
    
    assert(len(bb) == 1)
    assert(_v2.type.strictTypeMatch(_v1.type))
    assert(type(_v1.type) == types.Int)
    assert(_v1.type.signed == False)
    assert(_v2.type.signed == False)

    t1,t2 = types.Char(signed=False),types.Char(signed=False)
    v1,v2 = valtracker.ValTracker(False,t1,None),valtracker.ValTracker(False,t2,None)
    v1.createVirtualReg()
    v2.createVirtualReg()
    bb = basicblock.BasicBlock()
    
    _v1,_v2 = operatorgen.arithConversion(bb,v1,v2)
    
    assert(len(bb) == 2)
    assert(_v2.type.strictTypeMatch(_v1.type))
    assert(type(_v2.type) == types.Int)
    assert(_v1.type.signed == True)
    assert(_v2.type.signed == True)
    
    


