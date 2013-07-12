import types
import valtracker
from backend import ir

def removeLValness(bb,val):
    if val.lval:
        if val.type.isStruct:
            raise Exception("connect get the value of a struct")
        preg = val.reg
        val = val.deref()
        bb.append(ir.Deref(val.reg,preg))
    return val


def promoteToInt(bb,val):
    
    val = removeLValness(bb,val)
    
    t = val.type
    
    if not t.isInt:
        raise Exception("XXX trying to promote %s to int" % t)
    
    if type(t) in [types.Char,types.ShortInt]:
        newt = types.Int(signed=True)
        newreg = newt.createVirtualReg()
        if t.signed:
            op = ir.Unop('sx',newreg,val.reg)
        else:
            op = ir.Unop('zx',newreg,val.reg)
        bb.append(op)
        return valtracker.ValTracker(False,newt,newreg)
        
    elif type(t) == types.Int:
        return val
    else:
        raise Exception("unimplemented case not handled!")


_ranks = {
    types.Char : 0,
    types.ShortInt : 1,
    types.Int : 2,
    types.LongInt : 3,
}

def getRank(t):
    return _ranks[type(t)]

def arithConversion(bb,lv,rv):
    
    lv,rv = removeLValness(bb,lv),removeLValness(bb,rv)
    lv,rv = promoteToInt(bb,lv),promoteToInt(bb,rv)
    
    assert(lv.lval == False)
    assert(rv.lval == False)
    assert(lv.type.isInt)
    assert(rv.type.isInt)
    
    if lv.type.strictTypeMatch(rv.type):
        return lv,rv
    
    r1,r2 = getRank(lv.type),getRank(rv.type)
    
    #they are the same size, just differ in signedness
    #swap this flag and carry on
    if r1 == r2:
        if lv.type.signed == True:
            assert(rv.type.signed == False)
            lv.type.signed = False
            return lv,rv
        else:
            assert(lv.type.signed == False)
            rv.type.signed = False
            return lv,rv
    
    
    #XXX can refactor out code duplication
    if lv.type.signed and rv.type.signed:
        if r1 > r2:
            oldreg = rv.reg
            rv = lv.clone()
            bb.append(ir.Unop('sx',rv.reg,oldreg))
            return lv,rv
        else:
            assert(r1 != r2)
            oldreg = lv.reg
            lv = rv.clone()
            bb.append(ir.Unop('sx',lv.reg,oldreg))
            return lv,rv
    
    if r1 > r2:
        if rv.type.signed:
            ext = 'sz'
        else:
            ext = 'zx'
        oldreg = rv.reg
        rv = lv.clone()
        bb.append(ir.Unop(ext,rv.reg,oldreg))
        rv.type.signed = False
        return lv,rv
    else:
        assert(r1 != r2)
        if lv.type.signed:
            ext = 'sz'
        else:
            ext = 'zx'
        oldreg = lv.reg
        lv = rv.clone()
        bb.append(ir.Unop(ext,lv.reg,oldreg))
        lv.type.signed = False
        return lv,rv        

    raise Exception("unhandled case! unreachable") 


def genCast(bb,v,t):
    
    #print("casting %s %s to %s %s"%(v.type,v.type.signed,t,t.signed))
    
    v = removeLValness(bb,v)
    
    if t.strictTypeMatch(v.type):
        return v
    
    newv = valtracker.ValTracker(False,t.clone(),None)
    newv.createVirtualReg()
    if type(v.type) in [types.Struct]:
        raise Exception("XXX cannot coerce structs and arrays atm")
    
    if type(t) == types.Pointer and type(v.type) == types.Pointer:
        newv.type = t.clone()
        newv.reg = v.reg
    elif type(t) == types.Char and type(v.type) == types.Int:
        bb.append(ir.Unop('tr',newv.reg,v.reg))
    elif type(t) == types.Int and type(v.type) == types.Char:
        if v.type.signed:
            bb.append(ir.Unop('sx',newv.reg,v.reg))
        else:
            bb.append(ir.Unop('zx',newv.reg,v.reg))
    elif type(t) == type(v.type) and t.isInt and v.type.isInt:
        assert(t.signed != v.type.signed)
        newv.reg = v.reg
    else:
        raise Exception("XXX unhandle coersion case %s %s"%(v.type,t))
    
    if hasattr(t,'signed'):
        newv.type.signed = t.signed
    #print("done casting %s %s to %s %s"%(newv.type,newv.type.signed,t,t.signed))
    assert(newv.type.strictTypeMatch(t))
    return newv


# Returns a valtracker object with the result
def genBinop(bb,op,lv,rv):
    
    if type(lv.type) == types.Pointer or type(rv.type) == types.Pointer:
        raise Exception("pointer binop not handled yet")
    
    if lv.type.isInt and rv.type.isInt:
        lv = promoteToInt(bb,lv)
        rv = promoteToInt(bb,rv)
        #neither is lval after its been promoted
        lv,rv = arithConversion(bb,lv,rv)
        ret = lv.clone()
        if op in ['+','-','*','/','%','!=','==','<','>','>>','<<']:
            bb.append(ir.Binop(op,ret.reg,lv.reg,rv.reg))
        else:
            raise Exception('unhandled binop %s' % op)
        return ret
    else:
        raise Exception("XXX unhandled case %s %s %s" % (lv.type,op,rv.type))
    
