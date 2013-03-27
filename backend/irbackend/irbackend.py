
from backend.target import Target



class IRBackend(Target):
    
    def translateFunction(self,f,ofile):
        ofile.write(f.name)
        for block in f:
            ofile.write(block.name + ":\n")
            for instr in block:
                ofile.write("    %s\n"%str(instr))
