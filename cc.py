import sys
from c.frontend import CFrontend

from backend import standardmachine

from vis import irvis 



def main():
    m = CFrontend.translateModule(sys.argv[1])
    irvis.IR2Text(m)
    machine = standardmachine.StandardMachine()
    machine.translate(m,None)
    
if __name__ == '__main__':
    main()
