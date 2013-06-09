import argparse
import os

"""
This is the main driver for the compiler.

It invokes the preprocessor, the assembler, and linker. Will be
compatible enough with gcc enough so that is can be used in configure scripts
etc.
"""

argparser = argparse.ArgumentParser()

argparser.add_argument('input',nargs='+',help='source files')
argparser.add_argument('-O','--Optimization',type=int,help='Optimization level')
argparser.add_argument('-o','--output',help='output file')
argparser.add_argument('-S',action='store_true',help='assemble only, no link')

args = None

def preprocessSource(infname,outfname):
    pass

def compileSource(infname,outfname):
    pass

def assembleSourceFile(infname,outfname)
    pass

def linkExecuteable(objectfiles,outfname):
    pass

def removeFiles(fnamelist):
    for fname in fnamelist:
        os.unlink(fname)




def main():
    global args
    args = argparser.parse_args()


if __name__ == '__main__':
    main()
