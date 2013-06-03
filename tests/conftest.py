# content of conftest.py

import pytest

import os
import os.path
import subprocess
import tempfile


def newTempFile(suffix=''):
    t = tempfile.NamedTemporaryFile(delete=False,suffix=suffix)
    ret = t.name
    t.close()
    return ret


#The configuration defines how to build
#and run a file filling out a test result object

class TestConfiguration(object):
    
    def __init__(self,path):
        self.path = path
    
    def prepare(self):
        self.asmfile = newTempFile('.s')
        self.executeable = newTempFile()
        
    def cleanup(self):
        
        if os.path.isfile(self.asmfile):
            os.unlink(self.asmfile)
        
        if os.path.isfile(self.executeable):
            os.unlink(self.executeable)
    
    def buildCFile(self):
        args = self.compileCommand.format(self.path,self.asmfile).split(' ')
        subprocess.check_output(['timeout','2s'] + args,stderr=subprocess.STDOUT)
    
    def assemble(self):
        args = self.assembleCommand.format(self.asmfile,self.executeable).split(' ')
        subprocess.check_output(['timeout','2s'] + args,stderr=subprocess.STDOUT)
    
    #run a test returning a tuple of 
    #stdout,retcode 
    def runTest(self):
        retcode = 0
        try:
            output = subprocess.check_output(['timeout','2s',self.executeable],
                                                        stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            output = e.output
            retcode = e.returncode
        return retcode,output

    def getTestResults(self):    
        self.prepare()
        compiles = False
        assembles = False
        retcode = None
        output = None
        
        try:
            self.buildCFile()
            compiles = True
            self.assemble()
            assembles = True
            retcode,output = self.runTest()
        except subprocess.CalledProcessError as e:
            pass
        
        self.cleanup()
            
        result = { 'compiles' : compiles,
                   'assembles' : assembles,
                   'retcode' : retcode,
                   'output' : output, 
                 }
        return result


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


def pytest_addoption(parser):
    parser.addoption("--skipctests", action="store_true",
        help="Do not run the c tests")


def pytest_collect_file(parent, path):
    if path.ext == ".c":
        return CFile(path, parent)


class CFile(pytest.File):
    def collect(self):
        testpath = str(self.fspath)
        ideal = GCCX86(testpath)
        for testConf in [CCX86,CCOPTX86]:
            yield CTestItem(testpath, self,ideal,testConf(testpath))

class CTestItem(pytest.Item):
    
    def __init__(self,name,parent,idealConf,testConf):
        pytest.Item.__init__(self,name,parent)
        self.testConf = testConf
        self.idealConf = idealConf
    
    def runtest(self):
        
        if self.config.getoption("--skipctests"):
            pytest.skip("skipping full compile tests")
            return
        
        result = self.testConf.getTestResults()
        idealResult = self.idealConf.getTestResults()
        
        testfields = [
            'compiles',
            'assembles',
            'retcode',
            'output',
        ]
        
        for field in testfields:
            if result[field] != idealResult[field]:
                raise CTestException(field,idealResult,result)

    def repr_failure(self, excinfo):
        """ called when self.runtest() raises an exception. """
        if isinstance(excinfo.value, CTestException):
            e = excinfo.value
            return "\n".join([
                "CTest failed",
                "  '%s' is different" % e.field,
                "  ideal: %s" % e.ideal,
                "  actual: %s" % e.actual,
            ])
        else:
            e = excinfo.value
            return "\n".join([
                "CTest failed - uncaught exception",
                "%s" % type(excinfo.value),
                "%s" % str(excinfo.value)
            ])

    def reportinfo(self):
        return self.fspath, 0, "%s testfile: %s" % (self.testConf.configurationName,
                                                        self.name)

class CTestException(Exception):
    """ custom exception for error reporting. """
    def __init__(self,failedField,idealResult,actualResult):
        Exception.__init__(self)
        self.field = failedField
        self.ideal = idealResult
        self.actual = actualResult
        
