from pycparser import parse_file

import symtab
import typecheck
import irgen



class CFrontend(object):

    @staticmethod
    def translateModule(fname):
        ast = parse_file(fname,use_cpp=False)
        stb = symtab.SymTabGenerator()
        stb.visit(ast)
        
        irg = irgen.IRGenerator()
        irg.visit(ast)
        mod = irg.getModule()
        
        return mod
