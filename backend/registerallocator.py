



class RegisterAllocator(object):
    
    def allocate(self,f,ig):
        pass
        
    
    def spill(self,reg,f,ig):
        
        interferes = ig.getInterference(reg)
        
        
        for b in f:
            for i in b:
                if reg in i.read or reg in i.assigned:
                    useableRegisters = interferes - set(i.read) - set(i.assigned)
                    while True:
                        possible = useableRegisters.pop()
                        if possible.canContain(reg):
                            
                            for index,
                            
                            break
