
import os
import os.path
import sys
import tempfile
import shutil
import subprocess
import argparse

"""
This is the main driver for the compiler.

It invokes the preprocessor, the assembler, and linker. Will be
compatible enough with gcc enough so that is can be used in configure scripts
etc.
"""

argparser = argparse.ArgumentParser()

argparser.add_argument('input',help='source files')
argparser.add_argument('-O','--Optimization',default=0,type=int,help='Optimization level')
argparser.add_argument('-o','--output',default=None,help='output file')
argparser.add_argument('-S',action='store_true',help='assemble only, no link')
argparser.add_argument('-v','--verbose',action='store_true',help='verbose')

args = None


def getCompilerBasePath():
    return os.path.dirname(os.path.abspath(__file__))

def vprint(s):
    if args.verbose:
        print s


def preprocessSource(infname,outfname):
    subprocess.check_call( [
                            sys.executable,
                            getCompilerBasePath()+'/cpp.py',
                            '-I'+getCompilerBasePath() + '/include/',
                            infname,
                            '-o',outfname,
                            ])
def compileSource(infname,outfname):
    
    cmd = [
            sys.executable,
            getCompilerBasePath()+'/cc1.py',
            infname,
            '--output',outfname,
            ]
    if args.Optimization > 0:
        cmd += ['--iropt']
    
    subprocess.check_call(cmd)

def assembleSourceFile(infname,outfname):
    cmd = [
            'gcc', '-c',
            infname,
            '-o',outfname,
            ]
    subprocess.check_call(cmd)

def linkExecuteable(objectfile,outfname):
    cmd = [
        'gcc',
        objectfile,
        '-o',outfname,
        ]
    subprocess.check_call(cmd)




def main():
    global args
    args = argparser.parse_args()
    
    d = tempfile.mkdtemp()
    vprint("created temp dir %s" % d)
    fname = args.input
    base = os.path.basename(fname)[:-2]
    preprocessed = d+('/%s.preprocessed.c'%base)
    assembly = d+('/%s.s'%base)
    objectfile = d+('/%s.o'%base)
    ofile = args.output
    
    try:
        vprint("preprocessing source...")
        preprocessSource(fname,preprocessed)
        vprint("compiling file preprocessed source...")
        compileSource(preprocessed,assembly)
        vprint("assembling...")
        assembleSourceFile(assembly,objectfile)
        if args.S:
            if ofile == None:
                ofile = base + '.s'
            shutil.copy(assembly,ofile)
            vprint("Done!")
        else:
            vprint("linking...")
            if ofile == None:
                ofile = './a.out'
            linkExecuteable(objectfile,ofile)
            vprint("removing temp dir %s..." % d)
            shutil.rmtree(d)
            vprint("Done!")
    except subprocess.CalledProcessError:
        vprint("removing temp dir %s..." % d)
        shutil.rmtree(d)
        sys.stderr.write("ERROR terminating...\n")
        sys.exit(1)
        
        
    
    
    
    
    

if __name__ == '__main__':
    main()
