#Interpret the IR, used for testing
from backend import ir
import StringIO


class Memory(object):
    
    def __init__(self):
        self.pages = {}
    
    def readUInt32(self,addr):
        pass
        
    #allocate heap memory
    def malloc(self):
        pass
    
    #allocate memory on the stack
    def alloca(self):
        pass

class CallFrame(object):

    def __init__(self):
        self.registers = {}
        self.stackslots = {}
        self.paramslots = {}

class Interpreter(object):
    
    def __init__(self):
        self.setStdOut(StringIO.StringIO())
        self.setStdErr(StringIO.StringIO())
        self.setStdIn(StringIO.StringIO())
        
    def setStdOut(self,f):
        self._stdout = f
    
    def setStdErr(self,f):
        self._stderr = f
    
    def setStdIn(self,f):
        self._stdin = f
    
    def loadProcess(module,entrypoint,args):
        self.curFunction = None
        self.curBlock = None
        self.blockIdx = 0
        self.callStack = []    
        
    def step(self):
        pass
    

