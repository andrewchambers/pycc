



class InterferenceGraph(object):
    
    def __init__(self,la):
        
        interference = {}
        
        for instr in la.livevars:
            for live in la.livevars[instr]:
                for other in la.livevars[instr]:
                    if live not in interference:
                        interference[live] = set()
                    if live != other:
                        interference[live].add(other)
        
