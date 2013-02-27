import gv



def showInterferenceGraph(ig):
    
    counter = 0
    nodenames = {}
    for v in ig.interference:
        counter += 1
        nodenames[v] = "node%d" % counter
    
    pairs = []
    for v in ig.interference:
        for other in ig.interference[v]:
            pair = set([v,other])
            if pair not in pairs:
                pairs.append(pair)
            
    with gv.GraphViz() as g:
        g.write("graph g {\n")
        for v in ig.interference:
            g.write("%s [label=\"%s\"];\n"%(nodenames[v],str(v)))
        for v,other in pairs:
            g.write("%s -- %s;\n"%(nodenames[v],nodenames[other]))
        g.write("}\n")
        g.finalize()
        g.show()
