
import itertools


class LivenessAnalysis(object):
    
    def __init__(self,function):
        
        live = {}
        curlive = set()
        
        for block in reversed(list(function)):
            for ins in reversed(list(block)):
                
                live[ins] = [v for v in curlive]
                
                for v in ins.read:
                    curlive.add(v)

                for v in ins.assigned:
                    curlive.remove(v)
        
        
        self.livevars = live
