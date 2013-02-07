import sys
from c.frontend import CFrontend




def main():
    m = CFrontend.translateModule(sys.argv[1])
    print(m)

if __name__ == '__main__':
    main()
