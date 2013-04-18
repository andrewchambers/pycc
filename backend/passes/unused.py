import functionpass
from backend import ir


#remove vars that arent used

class UnusedVars(functionpass.FunctionPass):
    
    def runOnFunction(self,f):
            modified = False
            deleted = True
            while deleted:
                deleted = False
                read = set()
                assigned = set()
                
                for b in f:
                    for i in b:
                        for v in i.read:
                            read.add(v)
                        for v in i.assigned:
                            assigned.add(v)
                
                unused = set([x for x in assigned if x not in read])
                

                for b in f:
                    k = 0
                    while k < len(b):
                        i = b[k]
                        ass = set(i.assigned)
                        if len(ass) and ass.issubset(unused):
                            del b[k]
                            modified = True
                            deleted = True
                        k += 1
            return modified
