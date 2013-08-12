import sys
import interp.interpreter as interpreter


def main():
    import pickle
    m = pickle.load(open(sys.argv[1]))
    interpreterInst = interpreter.Interpreter()
    interpreterInst.setStdOut(sys.stdout)
    interpreterInst.loadModule(m,[])
    
    while True:
        interpreterInst.step()

if __name__ == '__main__':
    main()
