
from pyswip.prolog import Prolog


class liverange(object):
    
    def __init__(self):
        pass
    


class InterferenceGraph(object):
    
    def __init__(self,function):
        
        self.interference = {}
        
        for block in function():
    
