import unittest

from backend import interference

from backend import function
from backend import basicblock


class TestInterferenceGraph(unittest.TestCase):
    
    def test_simple(self):
        #test (in at&t order) that recreates a failiure from ... 
        #0  mov $1, %v1
        #1  mov %v1, %v3
        #2  mov $2, %v2
        #3  add %v2,%v3
        #4  mov %v3, %v4
        #5  ret %v4
        
        func = function.Function("testfunc")
        block = basicblock.BasicBlock()
        
        class FakeV(object):
            pass
        
        class FakeI(object):
            def getSuccessors(self):
                return []
            
            def isMove(self):
                return self._isMove
        
        v1 = FakeV()
        v2 = FakeV()
        v3 = FakeV()
        v4 = FakeV()
        
        #block
        b = [ FakeI() for x in range(6) ]
        b[0].read = []
        b[0].assigned = [v1]
        
        b[1].read = [v1]
        b[1].assigned = [v3]
        
        b[2].read = []
        b[2].assigned = [v2]
        
        b[3].read = [v2,v3]
        b[3].assigned = [v3] 
        
        b[4].read = [v3]
        b[4].assigned = [v4] 
        
        b[5].read = [v4]
        b[5].assigned = []
        
        block.opcodes = b
        
        func.setEntryBlock(block)
        
        interference.InterferenceGraph(func)
        
        
        
