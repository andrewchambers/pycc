import gv



def showInterferenceGraph(ig):
    
    with gv.GraphViz() as g:
        g.write("digraph g {\n")
        g.write("}\n")
