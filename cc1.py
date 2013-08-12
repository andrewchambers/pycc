import sys
import argparse

from c.frontend import CFrontend
from backend.x86 import x86
from interp.interpreter import Interpreter

backends = {
    "x86" : x86.X86 ,
}

argparser = argparse.ArgumentParser()
argparser.add_argument('source')
argparser.add_argument('--backend',default="x86")
argparser.add_argument('--frontend',default="C")
argparser.add_argument('--dump-ir', default=None)
argparser.add_argument('--output',default="-")
argparser.add_argument('--iropt', action='store_true')
argparser.add_argument('--show-preopt-function', action='store_true')
argparser.add_argument('--show-postopt-function', action='store_true')
argparser.add_argument('--show-selection-dag', action='store_true')
argparser.add_argument('--show-md-selection-dag', action='store_true')
argparser.add_argument('--show-md-function-preallocation', action='store_true')
argparser.add_argument('--show-md-function', action='store_true')
argparser.add_argument('--show-interference', action='store_true')
argparser.add_argument('--show-all', action='store_true')
args = argparser.parse_args()


def interpret(module):
    i = Interpreter()
    i.loadProcess(module,'main',[])
    while True:
        if i.step() == False:
            sys.exit(i.getExitCode())



def main():
    
    if args.backend not in backends:
        print "invalid backend - %s"%args.backend
        sys.exit(1)
    
    backendClass = backends[args.backend]
    
    m = CFrontend.translateModule(args.source)
    
    if args.dump_ir:
        import pickle
        f = open(args.dump_ir,'w')
        pickle.dump(m,f)
        return
    
    machine = backendClass()
    if args.output == '-':
        ofile = sys.stdout
    else:
        ofile = open(args.output,'w')
    machine.translate(args,m,ofile)
    if args.output != '-':
        ofile.close()
    
    
if __name__ == '__main__':
    main()
    

