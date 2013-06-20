from pycparser import c_ast
from backend import ir

#parse a typedef ast and return the appropriate types
def parseTypeDecl(typeTable,node):
    if type(node) == c_ast.Decl:
        return parseTypeDecl(typeTable,node.type)
    elif type(node) == c_ast.Struct:
        return _parseStruct(typeTable,node)
    elif type(node) == c_ast.TypeDecl:
        return _parseTypeDecl(typeTable,node)
    elif type(node) == c_ast.PtrDecl:
        return _parsePtrDecl(typeTable,node)
    elif type(node) == c_ast.ArrayDecl:
        return _parseArrayDecl(typeTable,node)
    elif type(node) == c_ast.FuncDecl:
        return _parseFuncDecl(typeTable,node)
    elif type(node) == c_ast.Typename:
        return parseTypeDecl(typeTable,node.type)
    elif type(node) == c_ast.EllipsisParam:
        return VarArgType()
    else:
        raise Exception("unknown type %s" % node)

def _parseFuncDecl(typeTable,node):
    retType = parseTypeDecl(typeTable,node.type)
    if node.args == None:
        args = []
    else:
        args = map( lambda arg : parseTypeDecl(typeTable,arg),
                    node.args.params)
        
        if len(args) == 1:
            if type(args[0]) == Void:
                args = []

        for arg in args:
            if type(arg) == Void:
                raise Exception("Void argument not allowed")

    return Function(retType,args)

def _parsePtrDecl(typeTable,node):
    return Pointer(parseTypeDecl(typeTable,node.type))
    
def _parseStruct(typeTable,node):
   if node.decls == None:
      return typeTable.lookupType(node.name,isStructType=True)

   t = Struct(node.name)
   for subdecl in node.decls:
       t.addMember(subdecl.name,parseTypeDecl(typeTable,subdecl))
   if node.name != None:
        typeTable.registerType(node.name,t)
   return t

def _parseTypeDecl(typeTable,node):
    sub = node.type
    if type(sub) == c_ast.IdentifierType:
        return _parseIdentifierType(typeTable,sub)
    else:
        return parseTypeDecl(typeTable,sub)

def _parseIdentifierType(typeTable,node):
    
    s = sorted(node.names)
    
    s = [v for v in s if v not in ['signed','unsigned','long','short']]
    
    if len(s) == 0:
        typename = 'int'
    else:
        assert(len(s) == 1)
        typename = s[0]
    
    if 'short' in node.names and 'long' in node.names:
        raise Exception("No valid type is both short and long.")
    
    if 'signed' in node.names and 'unsigned' in node.names:
        raise Exception("No valid type is both signed and unsigned.")
            
    if node.names.count('long') > 1:
        raise Exception("currently unimplemented long long")
    
    if 'unsigned' in node.names:
        signed = False
    else:
        signed = True
    
    if typename == 'int':
        if 'long' in node.names:
            return LongInt(signed=signed)
        elif 'short' in node.names:
            return ShortInt(signed=signed)
        else:
            return Int(signed=signed)
    elif typename == 'char':
        if 'long' in node.names or 'short' in node.names:
            raise Exception('cannot have a long or short char')
        return Char(signed=signed)
    else:
        ret = typeTable.lookupType(typename).clone()
        if isinstance(ret,IntType):
            ret.signed = signed
        return ret

def _parseArrayDecl(typeTable,node):
    dim = node.dim
    if type(dim)  == c_ast.Constant:
        dim = int(dim.value,10)
    else:
        raise Exception("XXX non constant array size not permitted")
    return Array(parseTypeDecl(typeTable,node.type),dim)



class Type(object):
    isStruct = False
    isInt = False

    def strictTypeMatch(self,t):
        if type(t) != type(self):
            return False
        return True

class VarArgType(Type):
    pass

class Function(object):
    def __init__(self,rettype,args):
        self.rettype = rettype
        self.args = args

    def clone(self):
        return Function(self.rettype.clone(),
                map(lambda x : x.clone(),self.args))
    
    def strictTypeMatch(self,t):
        if type(t) != Function:
            return False
        if not self.rettype.strictTypeMatch(t.rettype):
            return False
        
        if len(self.args) != len(t.args):
            return False
        
        for i in range(len(self.args)):
            if not self.args[i].strictTypeMatch(t.args[i]):
                return false
        return True

class Unqualified(Type):
    isStruct = True

    def __init__(self,name):
        self.name = name
    
    def createVirtualReg(self):
        return ir.Pointer()

    def clone(self):
        return Unqualified(self.name)
    
    def strictTypeMatch(self,t):
        if type(t) != Unqualified:
            return False

        if t.name != self.name:
            return False

        return True

class Void(Type):
    
    def clone(self):
        return Void()
    
    def createVirtualReg(self):
        return None

class Pointer(Type):
    
    def __init__(self,t):
        self.type = t
    
    def getSize(self):
        return 4
    
    def createVirtualReg(self):
        return ir.Pointer()
    
    def clone(self):
        return Pointer(self.type.clone())
    
    def strictTypeMatch(self,t):
        if type(t) != Pointer:
            return False

        return self.type.strictTypeMatch(t.type)

    
class Array(Type):
    
    def __init__(self,t,length):
        self.type = t
        self.length = length
    
    def getSize(self):
        return self.type.getSize() * self.length
        
    def clone(self):    
        return Array(self.type.clone(),self.length)
        
    def createVirtualReg(self):
        return ir.Pointer()

    def strictTypeMatch(self,t):
        if type(t) != Array:
            return False
        
        if not self.type.strictTypeMatch(t.type):
            return False
        
        return True

class IntType(Type):
    isInt = True
    def __init__(self,signed=True):
        self.signed = signed
    
    
    def strictTypeMatch(self,t):
        if type(t) != type(self):
            return False
        
        if self.signed != t.signed:
            return False
        
        return True

class Char(IntType):
    def getSize(self):
        return 1
        
    def createVirtualReg(self):
        return ir.I8()
    
    def clone(IntType):
        return Char()


class ShortInt(IntType):
    
    def getSize(self):
        return 2
        
    def createVirtualReg(self):
        return ir.I16()
    
    def clone(self):
        return ShortInt()

class Int(IntType):
    
    def getSize(self):
        return 4
        
    def createVirtualReg(self):
        return ir.I32()
    
    def clone(self):
        return Int()

class LongInt(IntType):
    
    def getSize(self):
        return 4
        
    def createVirtualReg(self):
        return ir.I32()
    
    def clone(self):
        return LongInt()


class Struct(Type):
    
    isStruct = True
    
    def __init__(self,name):
        self.name = name
        self.members = []
    
    def getSize(self):
        size = 0
        for name,t in self.members:
            size += t.getSize()
        return size
    
    def getMember(self,name):
        #XXX refactor
        return self.getMemberInfo(name)[0]
    
    def getMemberOffset(self,name):
        return self.getMemberInfo(name)[1]

    def getMemberInfo(self,name):
        #XXX deprecate...
        offset = 0
        
        for memberName,t in self.members:
            if memberName == name:
                return (t,offset)
            offset += t.getSize()
        
        return (None,None)
    
    def addMember(self,name,t):
        self.members.append([name,t])
        
    def clone(self):
        
        ret = Struct(self.name)
        for name,t in self.members:
            ret.addMember(name,t.clone())
        
        return ret
    
    def strictTypeMatch(self,t):
        if type(t) != Struct:
            return False

        if len(self.members) != len(t.members):
            return False

        for i in range(len(self.members)):
            if self.members[i][0] != t.members[i][0]:
                return False
            if not self.members[i][1].strictTypeMatch(t.members[i][1]):
                return False

        return True

class TypeTable(object):
    
    def __init__(self):
         
         self.types = {}
         self.structTypes = {}
         self.registerType('void',Void())
    
    def lookupType(self,name,isStructType=False):
        if isStructType:
            ret = self.structTypes.get(name,Unqualified(name)).clone()
        else:    
            ret = self.types[name].clone()
        return ret 
    
    def registerType(self,name,t,isTypedef=False):
        #print "registering type",name
        if name in self.types or name in self.structTypes:
            raise Exception("type %s already defined!" % name)
        
        if t.isStruct and isTypedef or not t.isStruct:
            self.types[name] = t
        else:
            #print "making struct type",name
            self.structTypes[name] = t
            
            
