import gv



def showInterferenceGraph(ig):
    
    counter = 0
    nodenames = {}
    for v in ig.nodes:
        counter += 1
        nodenames[v] = "node%d" % counter
            
    with gv.GraphViz() as g:
        g.write("graph g {\n")
        for v in ig.nodes:
            g.write("%s [label=\"%s\"];\n"%(nodenames[v],str(v)))
        
        for v,other in ig.interference:
            g.write("%s -- %s;\n"%(nodenames[v],nodenames[other]))
        
        for v,other in ig.moveedges:
            g.write("%s -- %s [style=\"dotted\"];\n"%(nodenames[v],nodenames[other]))
        
        g.write("}\n")
        g.finalize()
        g.show()
