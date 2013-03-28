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
                #print(unused)
                
                for b in f:
                    for k,i in enumerate(b.opcodes):
                        ass = set(i.assigned)
                        if len(ass) and ass.issubset(unused):
                            del b.opcodes[k]
                            modified = True
                            deleted = True
            return modified
