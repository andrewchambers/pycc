



class InterferenceGraph(object):
    
    def __init__(self,function):
        
        
        
        
        blocklist = [block for block in function]
        
        edges = [ (b,s) for b in blocklist for s in b[-1].getSuccessors() ]
        
        reachability = {}
        for b in blocklist:
            for b2 in blocklist:
                if b not in reachability:
                    reachability[b] = {}
                reachability[b][b2] = False
        
        
        for start,end in edges:
            reachability[start][end] = True
            
        print reachability
        #this could be a matrix
        #Floyd-Warshall algorithm
        for k in blocklist:
            for i in blocklist:
                for j in blocklist:
                    reachability[i][j] = reachability[i][j] or (reachability[i][k] and reachability[k][j])
        
        print reachability
        
