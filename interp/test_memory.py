import pytest
import memory


def test_read_write():
    mm = memory.MemoryManager()
    
    p = mm.malloc(8)
    assert len(p.memory) == 8
    p.write(0xffffffff)
    assert len(p.memory) == 8
    
    p2 = p + 4
    p2.write(0x11223344)
    assert len(p.memory) == 8
    
    p3 = p + 8
    assert len(p.memory) == 8
    assert p3.offset == 8
    with pytest.raises(memory.InvalidMemoryAccess):
        p3.read()
    
    assert p.read() == -1
    assert p.read(signed=False) == 0xffffffff
    assert p.read(little=False) == -1
    assert p2.read() == 0x11223344
    assert p2.read(little=False) == 0x44332211



def test_MemoryBlock():
    mem = memory.MemoryBlock(8)
    mem.write(0xffffffff,0)
    mem.write(0x11223344,4)
    
    assert mem.read(0) == -1
    assert mem.read(0,signed=False) == 0xffffffff
    assert mem.read(0,little=False) == -1
    assert mem.read(4) == 0x11223344
    assert mem.read(4,little=False) == 0x44332211
    
    with pytest.raises(memory.InvalidMemoryAccess):
        mem.read(32)
    
    with pytest.raises(memory.InvalidMemoryAccess):
        mem.read(7)
    
    with pytest.raises(memory.InvalidMemoryAccess):
        mem.read(6)
        
    with pytest.raises(memory.InvalidMemoryAccess):
        mem.read(5)
    
