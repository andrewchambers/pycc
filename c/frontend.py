from pycparser import parse_file

import symtab
import irgen


class CFrontend(object):

    @staticmethod
    def translateModule(fname):
        print("parsing file")
        ast = parse_file(fname,use_cpp=True)
        ast.show()
        print("generating IR")
        irg = irgen.IRGenerator()
        irg.visit(ast)
        mod = irg.getModule()
        return mod

