from pycparser import parse_file

import symtab
import typecheck
import irgen


class CFrontend(object):

    @staticmethod
    def translateModule(fname):
        print("parsing file")
        ast = parse_file(fname,use_cpp=False)
        ast.show()
        print("generating symtab:")
        stb = symtab.SymTab()
        stb.visit(ast)
        
        irg = irgen.IRGenerator(stb)
        irg.visit(ast)
        mod = irg.getModule()
        
        return mod

