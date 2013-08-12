import pytest
from bits import *


def test_getSignedVal():
    
    assert getSignedVal(0,32) == 0
    assert getSignedVal(0xff,32) == 255
    assert getSignedVal(0xffff,32) == 65535
    assert getSignedVal(0xffffff,32) == 16777215
    assert getSignedVal(0xffffffff,32) == -1
    
    assert getSignedVal(0,16) == 0
    assert getSignedVal(0xff,16) == 255
    assert getSignedVal(0xffff,16) == -1
    
    assert getSignedVal(0,32) == 0
    assert getSignedVal(0xff,8) == -1
    
    assert getSignedVal(0xfe,8) == -2
    assert getSignedVal(0xfffe,16) == -2
    assert getSignedVal(0xfffffffe,32) == -2
    
    assert getSignedVal(0xffffffff,16) == -1
    assert getSignedVal(0xfff00001,8) == 1
    assert getSignedVal(0xfff000fe,8) == -2
    
    with pytest.raises(Exception):
        getSignedVal(-1,32)

def test_getUnsignedVal():
    
    assert getUnsignedVal(0,32) == 0
    assert getUnsignedVal(-1,8) == 0xff
    assert getUnsignedVal(-1,16) == 0xffff
    assert getUnsignedVal(-1,32) == 0xffffffff
    
    assert getUnsignedVal(0,16) == 0
    assert getUnsignedVal(0xff,16) == 255
    assert getUnsignedVal(0xffff,16) == 0xffff
    
    assert getUnsignedVal(0,32) == 0
    assert getUnsignedVal(0xff,8) == 0xff
    
    assert getUnsignedVal(0xfe,8) == 0xfe
    assert getUnsignedVal(0xfffe,16) == 0xfffe
    assert getUnsignedVal(0xfffffffe,32) == 0xfffffffe
    
    assert getUnsignedVal(0xffffffff,16) == 0xffff
    assert getUnsignedVal(0xfff00001,8) == 0x01
    assert getUnsignedVal(0xfff000fe,8) == 0xfe
    


def test_bytesToVal():
    
    assert bytesToVal([0,0,0,0],bits=32,signed=False,little=True) == 0
    assert bytesToVal([1,2,3,4],bits=32,signed=False,little=False) == 0x01020304
    assert bytesToVal([1,2,3,4],bits=32,signed=False,little=True) == 0x04030201 
    assert bytesToVal([0xff,0xff,0xff,0xff],bits=32,signed=True,little=True) == -1
    assert bytesToVal([0x7f,0xff,0xff,0xff],bits=32,signed=True,little=True) ==  getSignedVal(0xffffff7f,32)
    assert bytesToVal([0x7f,0xff,0xff,0xff],bits=32,signed=True,little=False) == getSignedVal(0x7fffffff,32)
    

def test_valToBytes():
    
    assert valToBytes(0,bits=32,signed=False,little=True) == [0,0,0,0]
    assert valToBytes(0x01020304,bits=32,signed=False,little=False) == [1,2,3,4]
    assert valToBytes(0x04030201,bits=32,signed=False,little=True) ==  [1,2,3,4]
    assert valToBytes(-1,bits=32,signed=True,little=True) == [0xff,0xff,0xff,0xff]
    assert valToBytes(getSignedVal(0xffffff7f,32),bits=32,signed=True,little=True) ==  [0x7f,0xff,0xff,0xff]
    assert valToBytes(getSignedVal(0x7fffffff,32),bits=32,signed=True,little=False) == [0x7f,0xff,0xff,0xff]
    assert valToBytes(-1,bits=32,signed=False) == [0xff,0xff,0xff,0xff]





