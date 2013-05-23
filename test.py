import argparse
import tempfile
import subprocess
import os
import os.path
import shelve
import multiprocessing
import multiprocessing.pool
import time

parser = argparse.ArgumentParser(
            description='Run individual tests, or whole test set for the compiler')

parser.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="store_true")

parser.add_argument('path',nargs='?',default='./tests/',
                   help='a test file or path to build and run, default: "./tests/"')



#The configuration defines how to build
#and run a file filling out a test result object

class TestConfiguration(object):
    
    def __enter__(self):
        
        self.asmfile = newTempFile('.s')
        self.executeable = newTempFile()
        
        return self
        
    def __exit__(self, type, value, traceback):
        
        if os.path.isfile(self.asmfile):
            os.unlink(self.asmfile)
        
        if os.path.isfile(self.executeable):
            os.unlink(self.executeable)
    
    def buildCFile(self,cfile):
        args = self.compileCommand.format(cfile,self.asmfile).split(' ')
        subprocess.check_output(['timeout','2s'] + args,stderr=subprocess.STDOUT)
    
    def assemble(self):
        args = self.assembleCommand.format(self.asmfile,self.executeable).split(' ')
        subprocess.check_output(['timeout','2s'] + args,stderr=subprocess.STDOUT)
    
    #run a test returning a tuple of 
    #stdout,retcode 
    def runTest(self):
        retcode = 0
        try:
            output = subprocess.check_output(['timeout','2s',self.executeable],stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            output = e.output
            retcode = e.returncode
        
        return retcode,output

class GCCX86(TestConfiguration):
    configurationName = "gcc configuration"
    compileCommand = "gcc -std=c99 {0} -S -o {1}"
    assembleCommand = "gcc {0} -o {1}"

class CCX86(TestConfiguration):
    configurationName = "cc noopt configuration"
    compileCommand = "python ./cc.py {0} --output={1}"
    assembleCommand = "gcc {0} -o {1}"

class CCOPTX86(TestConfiguration):
    configurationName = "cc with opt configuration"
    compileCommand = "python ./cc.py --iropt {0} --output={1}"
    assembleCommand = "gcc {0} -o {1}"

#File system manipulation:

def newTempFile(suffix=''):
    t = tempfile.NamedTemporaryFile(delete=False,suffix=suffix)
    ret = t.name
    t.close()
    return ret


def enumerateTests(path):
    
    if os.path.isfile(path) and path.endswith('.c'):
        yield path
    elif os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            dirs.sort()
            files.sort()
            for fname in files:
                newfile = os.path.join(root,fname)
                if newfile.endswith('.c'):
                    yield newfile


def buildResult(testconfig,testpath):
    
    with testconfig() as tc:
        
        compiles = False
        assembles = False
        retcode = None
        output = None
        
        try:
            tc.buildCFile(testpath)
            compiles = True
            tc.assemble()
            assembles = True
            retcode,output = tc.runTest()
        except subprocess.CalledProcessError as e:
            pass
            
    result = { 'compiles' : compiles,
               'assembles' : assembles,
               'retcode' : retcode,
               'output' : output, 
             }
    return result




def main():
    args = parser.parse_args()
    path = args.path
    pool = multiprocessing.pool.ThreadPool(multiprocessing.cpu_count() + 2)
    passed = 0
    failed = 0
    v = args.verbose
    
    
    def mapFunc(test):
        
        ideal = buildResult(GCCX86,test)
        passed = True
        
        for testconfig in [CCX86,CCOPTX86]:
            
            testResult = buildResult(testconfig,test)
            
            if testResult != ideal:
                print "\033[91mFAIL\033[0m: %s (%s)" % (test,testconfig.configurationName)
                passed = False
        
        if v:
            print "\033[92mPASS\033[0m: %s" % test
        
        return passed
    
    print("Tests starting...")
    
    tests = enumerateTests(path)
    starttime = time.time()
    passfail = pool.map(mapFunc,tests)
    duration = time.time() - starttime
    
    print "----------------------------------"
    print "\033[95mSummary\033[0m: "
    print "----------------------------------"
    print "ran %d tests in %d mins %d seconds" % (len(passfail),duration/60,duration%60)
    print "PASSED: %d" % sum(passfail)
    print "FAILED: %d" % (len(passfail) - sum(passfail))

if __name__ == '__main__':
    main()
