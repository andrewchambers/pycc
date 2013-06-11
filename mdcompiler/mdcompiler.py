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


def isValidType(tname):
    return tname in ['I32','I8','Pointer']

def isValidInstr(instr):
    return instr in ['Binop','Unop']

def isValidOperator(op):
    return op in ['"+"','"-"']


def parseInstr(tree):
    if tree[0] != 'instr':
        raise Exception("Expected an instr sexpression")
    print "class %s(machineinstruction.MI):"%tree[1]
    
    #print tree
    for field in tree[2:]:
        if field[0] == 'pattern':
            parsePattern(field)
        elif field[0] == 'extra':
            parseExtra(field)
        else:
            raise Exception("unexpected field %s in instr %s"%(field[0],tree[1]))

def parseExtra(extra):
    if type(extra[1]) != str:
        raise Exception("extra must be a string! got %s" % extra[1])
    sys.stdout.write(extra[1][1:-1])

def parsePattern(tree):
    #print "parsing pattern",tree
    if tree[0] != 'pattern':
        raise Exception("Expected a pattern sexpression, got %s" % tree[0])      
    
    print "    @classmethod"
    print "    def match(cls,dag,node):"
    print "        nodestack = [node]"
    print "        newins = []"
    print "        newouts = []"
    parseNodeMatch(0,tree[1])
    print "        newnode = SDNode()"
    print "        newinstr = cls()"
    print "        newinstr.read = newins"
    print "        newinstr.assigned = newouts"
    print "        newnode.instr = newinstr"
    print "        print newnode.outs"
    print "        node.ins[0].edge.head = newnode.outs[0]"
    print "        raise Exception('Unhandled match!')"

def parseNodeMatch(depth,node):
    #print "parsingMatchNode",node
    print "        if len(nodestack[-1].instr.assigned) != 1:"
    print "            return None"
    if not isValidType(node[0]):
        raise Exception("not a valid virtual reg type %s" % node[0]) 
    print "        if type(nodestack[-1].instr.assigned[0]) != ir.%s:"%node[0]
    print "            return None"
    if len(node) == 1:
        pass
    else:
        if not isValidInstr(node[1]):
            raise Exception("not a valid instr type %s" % node[1]) 
        print "        if type(nodestack[-1].instr) != ir.%s:"%node[1]
        print "            return None"
        #print depth
        if depth > 0:
            print "        if len(nodestack[-1].outs[0]) > 1:"
            print "            return None"
        offset = 0
        if node[1] in ['Binop','Unop']:
            offset += 1
            if not isValidOperator(node[2]):
                raise Exception("not a valid Operator type %s" % node[2]) 
            print "        if nodestack[-1].instr.op != %s:"%node[2]
            print "            return None"
            
        for idx,inp in enumerate(node[2+offset:]):
            print "        nodestack.append(nodestack[-1].ins[%s].edge.head.parent)" % idx
            parseNodeMatch(depth+1,inp)
    
    print "        nodestack.pop()"
    




if __name__ == '__main__':
    text = sys.stdin.read()
    text = removeComments(text)
    print "#Auto generated file! generated with %s" %(sys.argv[0])
    print "from backend import machineinstruction"
    print "from backend import  ir"
    print "from backend.selectiondag import *"
    print ""
    tree = parser.parse(text)
    for instr in tree:
       #print instr
        parseInstr(instr)
        print ""
    
    print "matchableInstructions = ["
    for instr in tree:
        print "    %s,"%instr[1]
    print ']'
        

