import target
import dag

import vis
import vis.dagvis

class StandardMachine(target.Target):
    
    def translate(self,module,ofile):
        
        for f in module:
            self.translateFunction(f,ofile)
    
    def translateFunction(self,f,ofile):
        
        for b in f:
            insDag = dag.DAG(b)
            vis.dagvis.DAG2Text(insDag)