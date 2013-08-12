from bits import *

class InvalidMemoryAccess(RuntimeError):
    pass

class MemoryBlock():
    
    def __init__(self,size,name='ANON BLOCK'):
        self._bytearray = bytearray(size)
        self.isFree = False
        self.name = name
        
    def free(self,offset):
        self.isFree = True
    
    def __len__(self):
        return len(self._bytearray)
    
    def read(self,offset,bits=32,little=True,signed=True):
        
        if self.isFree:
            raise InvalidMemoryAccess("Attempting to read "
                                        "from a freed memory region (%s)"
                                            %self.name)
        
        endbound = offset + bits/8
        if offset < 0 or len(self._bytearray) < endbound:
            raise InvalidMemoryAccess("reading past end of buffer (%s). Offset: %s" 
                                        % (self.name,offset))
        
        bytes = self._bytearray[offset:endbound]

        
        return bytesToVal(bytes,bits=bits,little=little,signed=signed)
    
    def write(self,val,offset,bits=32,little=True,signed=True):
        
        if self.isFree:
            raise InvalidMemoryAccess("Attempting to write "
                                        "to a freed memory region (%s)" 
                                            % self.name)
        
        bytes = valToBytes(val,bits=bits,signed=signed,little=little)
        
        endbound = offset + bits/8
        if offset < 0 or len(self._bytearray) < endbound:
            raise InvalidMemoryAccess("writing past end of buffer (%s). Offset: %s" 
                                        % (self.name,offset))
        
        self._bytearray[offset:offset+bits/8] = bytes

        
class Pointer(object):
    
    def __init__(self,memory,offset=0):
        #offset within byte array
        self.offset = offset
        #byte array of memory pointed to
        self.memory = memory
    
    def addOffset(self,offset):
        newoffset = self.offset+offset
        return Pointer(memory=self.memory,offset=newoffset)
    
    def __add__(self,other):
        assert(type(other) == int)
        return self.addOffset(other)
    
    def ptrDiff(self,other):
        
        if other.memory != self.memory:
            raise Exception("Pointer diff between non related pointers!")
        
        return Pointer(memory=self.memory, offset=self.offset - other.offset)
    
    def __sub__(self,other):
        assert(type(other) == Pointer)
        return self.ptrDiff(other)
    
    def read(self,bits=32,little=True,signed=True):
        return self.memory.read(self.offset,bits=bits,little=little,signed=signed)
        
    def write(self,val,bits=32,little=True,signed=True):
        self.memory.write(val,self.offset,bits=bits,little=little,signed=signed)
    
class MemoryManager(object):
    
    def __init__(self):
        self.labelCounter = 0
    
    def newPointerLabel(self):
        self.labelCounter += 1
        return 'Memory Block %s' % self.labelCounter
        
    #allocate heap memory
    def malloc(self,size,name=None):
        if not name :
            name = self.newPointerLabel()
        name = 'Heap ' + name
        
        p = Pointer(MemoryBlock(size,name))
        return p
    
    #allocate memory on the stack
    def alloca(self,size,name=None):
        if not name :
            name = self.newPointerLabel()
        name = 'Stack ' + name
        
        p = Pointer(MemoryBlock(size,name))
        return p
    
    
    

