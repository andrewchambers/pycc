
def getSignedVal(val,bits):
    assert val >= 0
    if val & (1 << (bits-1)):
        return -((~val + 1) & (2**bits - 1))
    else:
        return val & (2**bits - 1)

def getUnsignedVal(val,bits):
    return val & (2**bits - 1)


def bytesToVal(bytes,bits=32,little=True,signed=True):
    
    ret = 0
    
    assert bits in {8,16,32,64}
    assert len(bytes) == bits/8
    
    if little:
        biter = iter(bytes)
    else:
        biter = iter(reversed(bytes))
    
    for byteNum,b in enumerate(biter):
        assert 0 <= b < 256
        ret += b << (byteNum * 8)
    
    if signed:
       ret = getSignedVal(ret,bits)
    
    return ret

def valToBytes(val,bits=32,little=True,signed=True):
    
    assert bits in {8,16,32,64}
    
    nbytes = bits/8
    
    if signed:
        val = getUnsignedVal(val,bits)
    
    
    ret = [0 for i in range(nbytes)]
    
    for i in range(nbytes):
        if little:
            ret[i] = val & 0xff
        else:
            ret[nbytes - i - 1] = val & 0xff
        val >>= 8
    return ret
