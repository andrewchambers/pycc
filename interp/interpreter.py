#Interpret the IR, used for testing
from backend import ir
import StringIO
import memory


class CallFrame(object):

    def __init__(self):
        self.registers = {}
        self.stackslots = {}
        self.paramslots = {}


class Interpreter(object):
    
    def __init__(self):
        self.mm = memory.MemoryManager()
        self.setStdOut(StringIO.StringIO())
        self.setStdErr(StringIO.StringIO())
        self.setStdIn(StringIO.StringIO())
        
    def setStdOut(self,f):
        self._stdout = f
    
    def setStdErr(self,f):
        self._stderr = f
    
    def setStdIn(self,f):
        self._stdin = f
    
    def loadModule(self,module,args):
        self.curFunction = None
        self.curBlock = None
        self.blockIdx = 0
        curFrame = CallFrame()
        self.callStack = [curFrame]
        self.curFunction = module.getFunction('main')
        self.curBlock = self.curFunction.entry
        
        
    def step(self):
        instr = self.curBlock[self.blockIdx]
        
        self.doInstruction()
    

