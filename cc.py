import sys
from c.frontend import CFrontend

from backend import standardmachine



def main():
    m = CFrontend.translateModule(sys.argv[1])
    machine = standardmachine.StandardMachine()
    machine.translate(m,None)
    
if __name__ == '__main__':
    main()
