import os
import subprocess
import tempfile

class GraphViz(object):

    def __init__(self):
        self.gvfd,self.gvfname = tempfile.mkstemp(suffix=".gv")
        fd,self.svgfname = tempfile.mkstemp(suffix=".svg")
        os.close(fd) # we dont need this fd  
    
    def __enter__(self):

        return self
    
    def write(self,s):
        os.write(self.gvfd,s)
    
    def finalize(self):
        subprocess.check_call(['dot','-Tsvg',self.gvfname,'-o',self.svgfname])
        
    def show(self):
        subprocess.check_call(['display',self.svgfname])
        
    def __exit__(self, type, value, traceback):
        os.close(self.gvfd)
        os.remove(self.gvfname)
        os.remove(self.svgfname)
