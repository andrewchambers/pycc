
from pycparser import c_parser,c_ast 
import StringIO
import types

def astFromString(s):
    parser = c_parser.CParser()
    return parser.parse(s)


t1 = """
struct Foo {
    int x;
    int y;
};

struct Foo2 {
    int moo;
} bar;

struct {
    int x;
} barbar;

int x;
int * y;

struct Foo x;

struct {
    int x;
} * x;

struct Foobar {
    int x;
} * x;

int x[10];


struct unqualified * x;

struct unqualified {
    int x;
};


int (*foo)(int,int);

int foo(){

};

"""


def test_typeParsing():
    typeTable = types.TypeTable()
    ast = astFromString(t1)
    #ast.show()
    parsed = types.parseTypeDecl(typeTable,ast.ext[0])
    
    for t in [parsed,typeTable.lookupType('Foo',isStructType=True)]:
        assert(type(t) == types.Struct)
        assert(t.name == 'Foo')
        assert(type(t.getMember('x')) == types.Int)
        assert(type(t.getMember('y')) == types.Int)
        assert(t.getMemberOffset('x') == 0)

    parsed = types.parseTypeDecl(typeTable,ast.ext[1])

    for t in [parsed,typeTable.lookupType('Foo2',isStructType=True)]:
        assert(type(t) == types.Struct)
        assert(t.name == 'Foo2')
        assert(type(t.getMember('moo')) == types.Int)
        assert(t.getMemberOffset('moo') == 0)

    t = types.parseTypeDecl(typeTable,ast.ext[2])

    assert(type(t) == types.Struct)
    assert(t.name == None)
    assert(type(t.getMember('x')) == types.Int)
    assert(t.getMemberOffset('x') == 0)

    parsed = types.parseTypeDecl(typeTable,ast.ext[3])
    assert(type(parsed) == types.Int)
            
    #pointer to int
    parsed = types.parseTypeDecl(typeTable,ast.ext[4])
    assert(type(parsed) == types.Pointer)
    assert(type(parsed.type) == types.Int)
    
    
    parsed = types.parseTypeDecl(typeTable,ast.ext[5])
    for t in [parsed,typeTable.lookupType('Foo',isStructType=True)]:
        assert(type(t) == types.Struct)
        assert(t.name == 'Foo')
        assert(type(t.getMember('x')) == types.Int)
        assert(type(t.getMember('y')) == types.Int)
        assert(t.getMemberOffset('x') == 0)

    parsed = types.parseTypeDecl(typeTable,ast.ext[6])
    assert(type(parsed) == types.Pointer)
    assert(type(parsed.type) == types.Struct)
    assert(parsed.type.name == None)
    
    parsed = types.parseTypeDecl(typeTable,ast.ext[7])
    assert(type(parsed) == types.Pointer)
    assert(type(parsed.type) == types.Struct)
    assert(parsed.type.name == "Foobar")
    assert(typeTable.lookupType('Foobar',isStructType=True) != None)
    
    parsed = types.parseTypeDecl(typeTable,ast.ext[8])
    assert(type(parsed) == types.Array)
    assert(type(parsed.type) == types.Int)
    assert(parsed.length == 10)
    
    parsed = types.parseTypeDecl(typeTable,ast.ext[9])
    assert(type(parsed) == types.Pointer )
    
    parsed = types.parseTypeDecl(typeTable,ast.ext[10])
    assert(type(parsed) == types.Struct)  
    assert(parsed.name == "unqualified")
    
    parsed = types.parseTypeDecl(typeTable,ast.ext[11])
    assert(type(parsed) == types.Pointer)
    assert(type(parsed.type) == types.Function)
    assert(type(parsed.type.rettype) == types.Int)
    assert(type(parsed.type.args[0]) == types.Int)
    assert(len(parsed.type.args) == 2)


t2 = """

char * foo;
char * bar;

void (*foo) ();
void (*foo)(void);

struct Foo {
    int x;
    int y;
};

struct Foo bar;

"""

def test_typeMatching1():
    typeTable = types.TypeTable()
    ast = astFromString(t2)
 
    for i in range(3):
        a,b = i*2,i*2+1
        #print a,b
        typea = types.parseTypeDecl(typeTable,ast.ext[a])
        typeb = types.parseTypeDecl(typeTable,ast.ext[b])
        assert(typea.strictTypeMatch(typeb))

t3 = """

char * foo;
int * bar;

void (*foo) (int);
void (*foo)(void);

struct Foo {
    int x;
    int y;
};

struct Bar bar;

"""

def test_typeMatching2():
    typeTable = types.TypeTable()
    ast = astFromString(t3)
 
    for i in range(3):
        a,b = i*2,i*2+1
        #print a,b
        typea = types.parseTypeDecl(typeTable,ast.ext[a])
        typeb = types.parseTypeDecl(typeTable,ast.ext[b])
        assert(typea.strictTypeMatch(typeb) == False)



t4 = """
    char x;
    unsigned char x;
    int short x;
    short int x;
    unsigned short int x;
    short x;
    unsigned short x;
    unsigned x;
    int x;
    unsigned int x;
    long int x;
    unsigned long int x;
    long x;
    unsigned long x;
    long unsigned x;
"""

t4solutions = [
    types.Char(signed=True),
    types.Char(signed=False),
    types.ShortInt(signed=True),
    types.ShortInt(signed=True),
    types.ShortInt(signed=False),
    types.ShortInt(signed=True),
    types.ShortInt(signed=False),
    types.Int(signed=False),
    types.Int(signed=True),
    types.Int(signed=False),
    types.LongInt(signed=True),
    types.LongInt(signed=False),
    types.LongInt(signed=True),
    types.LongInt(signed=False),
    types.LongInt(signed=False),
]

def test_IntTypeParsing():
    
    typeTable = types.TypeTable()
    ast = astFromString(t4)
    assert(len(t4solutions) == len(ast.ext))
    for i,ideal in enumerate(t4solutions):

        parsed = types.parseTypeDecl(typeTable,ast.ext[i])
        print i
        print ideal
        print parsed
        matches = ideal.strictTypeMatch(parsed)
        assert(matches == True)

