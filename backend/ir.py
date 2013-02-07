

class Variable(object):
    pass

class I32(Variable):
    pass

class Constant(object):
    pass

class ConstantI32(Constant):
    def __init__(self,v):
        self.value = int(v)


class Instruction(object):
    
    def __init__(self):
        pass

class Binop(Instruction):
    def __init__(self,op,res,l,r):
        pass

class Ret(Instruction):
    def __init__(self):
        pass

class LoadConstant(Instruction):
    def __init__(self,var,const):
        pass
