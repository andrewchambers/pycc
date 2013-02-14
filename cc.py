import sys
from c.frontend import CFrontend

from backend.x86 import x86



def main():
    m = CFrontend.translateModule(sys.argv[1])
    machine = x86.X86()
    machine.translate(m,None)
    
if __name__ == '__main__':
    main()
