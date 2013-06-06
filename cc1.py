import sys
import argparse

from c.frontend import CFrontend

from backend.x86 import x86
from backend.irbackend import irbackend

backends = {
    "x86" : x86.X86 ,
    "ir" : irbackend.IRBackend ,
}


argparser = argparse.ArgumentParser()

argparser.add_argument('source')

argparser.add_argument('--backend',default="x86")
argparser.add_argument('--frontend',default="C")
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

def main():
    
    
    if args.backend not in backends:
        print "invalid backend - %s"%args.backend
        sys.exit(1)
    
    backendClass = backends[args.backend]
    
    m = CFrontend.translateModule(args.source)
    
    machine = backendClass()
    if args.output == '-':
        ofile = sys.stdout
    else:
        ofile = open(args.output,'w')
    machine.translate(args,m,ofile)
    ofile.close()
    
    
if __name__ == '__main__':
    
    main()
