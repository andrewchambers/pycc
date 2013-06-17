from backend import machineinstruction
from backend.patterns import *

import x86

class X86Add(machineinstruction.MI):
    pattern = Set(I32,Binop('+',I32,I32))
    asmstr = "add %{1},%{0}"

matchableInstructions = [
    X86Add,
]
