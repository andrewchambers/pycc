import unittest

from backend import interference

from backend import function
from backend import basicblock
from backend import ir

from vis import interferencevis

class TestInterferenceGraph(unittest.TestCase):
    
    def test_noreadassign(self):
        func = function.Function("testfunc")
        block = basicblock.BasicBlock()
        v1 = ir.I32()
        v2 = ir.I32()
        v3 = ir.I32()
        
        block.append()
    
    def test_simple(self):
        
        #test (in at&t order) that recreates a failiure from ... 
        #0  mov $1, %v1 - live(v1)
        #1  mov %v1, %v3 - live(v1,v3)
        #2  mov $2, %v2 - live(v2,v3)
        #3  add %v2,%v3 - live(v2,v3)
        #4  mov %v3, %v4 - live(v3,v4)
        #5  ret %v4 - live(v4)
        
        
        
        func = function.Function("testfunc")
        block = basicblock.BasicBlock()
        
        v1 = ir.I32()
        v2 = ir.I32()
        v3 = ir.I32()
        v4 = ir.I32()
        
        #block
        block.append(ir.LoadConstant(v1,ir.ConstantI32(2)))
        block.append(ir.Move(v1,v3))
        block.append(ir.LoadConstant(v2,ir.ConstantI32(2)))
        block.append(ir.Binop('+',v3,v3,v2))
        block.append(ir.Move(v4,v3))
        block.append(ir.Ret(v4))
        
        func.setEntryBlock(block)
        
        ig = interference.InterferenceGraph(func)
        
        #interferencevis.showInterferenceGraph(ig)
        
        
        #self.assertTrue(set([v3,v2]) in ig.interference)
        #self.assertTrue(set([v3,v2]) in ig.interference)
