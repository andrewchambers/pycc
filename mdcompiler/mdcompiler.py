import sys
import ply.yacc as yacc
import ply.lex as lex

# List of token names.   This is always required
tokens = (
   'WORD'  ,
   'LPAREN',
   'RPAREN',
   'STRING',
)

t_WORD = r'[a-zA-Z_][_a-zA-Z0-9]*'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_STRING  = r'"[^"]*"'


def removeComments(s):
    ret = ''
    
    normal = 0
    comment = 1
    string = 2
    escape = 3
    
    state = normal
    for c in s:
        if state == normal:
            if c == ';':
                state = comment
            elif c  == '"':
                state = string
        elif state == comment:
            if c == '\n':
                state = normal
        elif state == string:
            if c == '"':
                state = normal
            elif c == '\\':
                state = escape
        elif state == escape:
            state = string
        else:
            raise Exception('bad state')
        
        if state != comment:
            ret += c
    return ret




# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t'

def p_file(p):
    """file : sexpr file
    |   
    """
    if len(p) == 1:
        p[0] = []
    else:
        p[0] = [p[1]] + p[2]
    
def p_sexpr(p):
    """sexpr : LPAREN members RPAREN
        | LPAREN RPAREN
    """
    if len(p) == 3:
        p[0] = []
    else:
        p[0] = p[2]   

def p_members(p):
    """members : members member
        | member
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_member(p):
    """
    member : sexpr
        | WORD
        | STRING
    """
    p[0] = p[1]


# Error handling rule
def t_error(t):
    print "Illegal character '%s'" % t.value[0]
    t.lexer.skip(1)


# Error rule for syntax errors
def p_error(p):
    raise Exception("Syntax error in input! %s" % p)

# Build the parser
# Build the lexer
lexer = lex.lex()
parser = yacc.yacc()


#Support functions

def isAsmStr(s):
    if s.startswith("#asm"):
        return True
    if "return" in s:
        return False
    return True


def isValidType(tname):
    return tname in ['I32','I8','Pointer', '_']

_validinstructions = [
        'Binop',
        'Unop',
        'Move',
        'LoadConstant',
        'LoadGlobalAddr',
        'LoadLocalAddr',
        'LoadParamAddr',
        'Store',
        'Deref',
        'Branch',
        'Jmp',
]

def isValidInstr(instr):
    return instr in _validinstructions 

def isValidOperator(op):
    op = op[1:-1]
    return op in ['+','-','!=','==','<','>','<=','>=','*','/','%','!','>>','<<']

#end support functions

def parseInstr(tree):
    if tree[0] != 'instr':
        raise Exception("Expected an instr sexpression")
    print "class %s(machineinstruction.MI):"%tree[1]
    hasConstructor = False
    #print tree
    for field in tree[2:]:
        if field[0] == 'pattern':
            parsePattern(field)
        elif field[0] == 'extra':
            parseExtra(field)
        elif field[0] == 'asmstr':
            parseAsmStr(field)
        elif field[0] == 'constructor':
            if hasConstructor:
                raise Exception('more than one constructor in %s' % tree[1])
            hasConstructor = True
            doConstructor(field[1][1:-1])
        else:
            raise Exception("unexpected field %s in instr %s"%(field[0],tree[1]))
    
    if hasConstructor == False:
        doConstructor('        pass')

def doConstructor(consbody):
    print "    def __init__(self,node):"
    print "        machineinstruction.MI.__init__(self)"
    sys.stdout.write(consbody + '\n')


def parseAsmStr(asmstr):
    if type(asmstr[1]) != str:
        raise Exception("asmstr must be a string! got %s" % extra[1])
    if  isAsmStr(asmstr[1]):
        print "    asmstr = %s" %asmstr[1].replace('\n','\\n')
    else:
        doAsmFunction(asmstr[-1][1:-1])


def doAsmFunction(s):
    print "    def asm(self):"
    print s


def parseExtra(extra):
    if type(extra[1]) != str:
        raise Exception("extra must be a string! got %s" % extra[1])
    sys.stdout.write(extra[1][1:-1])
    print ("")

def parsePattern(tree):
    #print "parsing pattern",tree
    if tree[0] != 'pattern':
        raise Exception("Expected a pattern sexpression, got %s" % tree[0])      
    
    print "    @classmethod"
    print "    def match(cls,dag,node):"
    print "        nodestack = [node]"
    print "        newchildren = []"
    print "        newcontroldeps = set()"
    print "        newins = []"
    parseHeadNodeMatch(True,tree[1])
    print "        node.instr = cls(node)"
    print "        node.instr.assigned = out"
    print "        node.children = newchildren"
    print "        node.control = list(newcontroldeps)"
    print "        node.instr.read = newins"
    print "        return True"

def parseHeadNodeMatch(isTopLevel,node):

    sys.stderr.write(str(node) + '\n')
    
    if type(node[0]) == str:
        rettype = node[0]
        nreturns = 1
    else:
        if len(node[0]) == 0:
            rettype = None
            nreturns = 0
        else:
            nreturns = 1
            rettype = node[0][0]
    
    print "        if len(nodestack[-1].instr.assigned) != %s:" % nreturns
    print "            return False"
    
    print "        newcontroldeps.update(nodestack[-1].control)"
    
    if isTopLevel == False:
        print "        #we cant match instructions whose intermediate is needed elsewhere"
        print "        if len(nodestack[-1].parents) > 1:"
        print "            return False"
        
    if isTopLevel:
        if nreturns == 0:
            print "        out = []"
        else:
            print "        out = nodestack[-1].instr.assigned"
    #sanity check... 
    if isTopLevel == False:
        print "        if len(nodestack[-1].parents) == 0:"
        print "            return False"  
    
    if rettype != None:
        if not isValidType(rettype):
            raise Exception("bad type %s" % rettype)
            
        if rettype != '_':
            print "        if type(nodestack[-1].instr.assigned[0]) != ir.%s:"%rettype
            print "            return False"
    
    if not isValidInstr(node[1]):
        raise Exception("not a valid instr type %s" % node[1])
    print "        if type(nodestack[-1].instr) != ir.%s:"%node[1]
    print "            return False"
    
    offset = 0
    if node[1] in ['Binop','Unop']:
        offset += 1
        if not isValidOperator(node[2]):
            raise Exception("not a valid Operator type %s" % node[2]) 
        print "        if nodestack[-1].instr.op != %s:"%node[2]
        print "            return False"
    
    if len(node[2 + offset:]):
        
    
    
        for idx,subnode in enumerate(node[2 + offset:]):
            print "        #we can only match nodes with noutputs 1"
            print "        if nodestack[-1].children[%s][0] != 0:" % idx
            print "            return False"
            print "        nodestack.append(nodestack[-1].children[%s][1])" % idx
            if len(subnode) == 1:
                parseTerminalNodeMatch(subnode)
            else:
                parseHeadNodeMatch(False,subnode)
            print "        nodestack.pop()"


def parseTerminalNodeMatch(node):
    print "        #matching terminal %s" % node
    if not isValidType(node[0]):
        raise Exception("bad type %s" % node[0])
    
    if node[0] != '_':
        print "        if type(nodestack[-1].instr.assigned[0]) != ir.%s:"% node[0]
        print "            return False"
    print "        newchildren.append((0,nodestack[-1]))"
    print "        newins.append(nodestack[-1].instr.assigned[0])"

    
    




if __name__ == '__main__':
    text = sys.stdin.read()
    text = removeComments(text)
    print "#Auto generated file! generated with %s" %(sys.argv[0])
    print "from backend import machineinstruction"
    print "from backend import  ir"
    print "import backend.selectiondag as seldag"
    print ""
    tree = parser.parse(text)
    matchableInstructions = []
    for item in tree:
        if item[0] == 'instr':
            sys.stdout.write('#')
            print item
            matchableInstructions.append(item[1])
            parseInstr(item)
            print ""
        elif item[0] == 'code':
            print item[1][1:-1]
            print ''
        else:
            raise Exception("unknown top level instruction %s" % item[0])
    
    print "matchableInstructions = ["
    for instr in matchableInstructions:
        print "    %s,"%instr
    print ']'
        

