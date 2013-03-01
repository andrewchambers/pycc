import sys
import argparse

from c.frontend import CFrontend

from backend.x86 import x86

argparser = argparse.ArgumentParser()

argparser.add_argument('source')
argparser.add_argument('--iropt', action='store_true')
argparser.add_argument('--show-preopt-function', action='store_true')
argparser.add_argument('--show-postopt-function', action='store_true')
argparser.add_argument('--show-selection-dag', action='store_true')
argparser.add_argument('--show-md-selection-dag', action='store_true')
argparser.add_argument('--show-md-function', action='store_true')
argparser.add_argument('--show-all', action='store_true')

args = argparser.parse_args()

def main():
    m = CFrontend.translateModule(args.source)
    machine = x86.X86()
    machine.translate(args,m,None)
    
if __name__ == '__main__':
    
    main()
