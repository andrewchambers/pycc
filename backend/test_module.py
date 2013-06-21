import module



def test_datafunction():
    
    m = module.Module()
    
    barlabel = m.addReadWriteData('bar')
    zerorw = m.addReadWriteData('\x00\x00\x00')
    zdlabel = m.addZeroInitData(64)
    foo1label = m.addReadOnlyData('foo')
    foo2label = m.addReadOnlyData('foo')
    
    assert(len(m.rwdata) == 2)
    assert(m.rwdata[0] == [[barlabel],'bar'])
    assert(m.rwdata[1] == [[zerorw],'\x00\x00\x00'])
    
    assert(len(m.rodata) == 2)
    assert(m.rodata[0] == [[foo1label],'foo'])
    assert(m.rodata[1] == [[foo2label],'foo'])
    assert(len(m.rwzdata) == 1)
    assert(m.rwzdata[0] == [[zdlabel],64])
    m.packData()
    
    assert(len(m.rwdata) == 1)
    assert(m.rwdata[0] == [[barlabel],'bar'])
    
    assert(len(m.rodata) == 1)
    assert(m.rodata[0] == [[foo1label,foo2label],'foo'])
    
    assert(len(m.rwzdata) == 2)
    assert(m.rwzdata[0] == [[zdlabel],64])
    assert(m.rwzdata[1] == [[zerorw],3])
