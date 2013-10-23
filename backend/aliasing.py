from backend import ir


class AliasAnalysis(object):
    
    def __init__(self,function):
        
        stackSlotAliases = {}
        
        for block in function:
            for instr in block:
                if type(instr) == ir.LoadLocalAddress:
                    if instr.sym.slot not in stackSlotAliases
                        stackSlotAliases[instr.sym.slot] = set()
                    
                    stackSlotAliases[instr.sym.slot].add(instr.assigned[0])
        
        self.definateAliases = list(stackSlotAliases.values())
    
    #XXX memoize this
    def definatelyAlias(self,a,b):
        for aliasSet in self.definateAliases:
            if a in aliasSet and b in aliasSet:
                return True
        return False
        
    def possiblyAlias(self,a,b):
        #XXX safe assumption
        return True
        

