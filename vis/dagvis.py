import gv



def showSelDAG(dg):
        with gv.GraphViz() as g:
            #generate a name for each node
            #so that dot can handle them
            nodenames = {}
            counter = 0
            for node in dg.nodes:
                counter += 1
                nodenames[node] = "node%d"%counter 
                
            g.write("digraph g {\n")
            for node in dg.nodes:
                span = max(len(node.read),1)
                g.write("%s [shape=none, margin 0,label=<\n" % nodenames[node] )
                g.write("<TABLE>\n")
                g.write("<TR>")
                if len(node.assigned):
                    for v in node.assigned:
                        g.write("<TD COLSPAN=\"%d\">%s</TD>"%(span,v))
                else:
                    g.write("<TD COLSPAN=\"%d\">X</TD>\n"%span)
                g.write("</TR>\n")
                g.write("<TR><TD COLSPAN=\"%d\">%s</TD></TR>\n"%(span,node.getDagDisplayText()))
                g.write("<TR>")
                if len(node.read):
                    for v in node.read:
                        g.write("<TD>%s</TD>"%v)
                else:
                    g.write("<TD>X</TD>")
                g.write("</TR>\n")
                
                g.write("</TABLE\n>")
                g.write(">];\n")
            for e in dg.edges:
                g.write("%s -> %s;\n"%(nodenames[e[0]],nodenames[e[1]]))
            for e in dg.controledges:
                g.write("%s -> %s [style=dotted];\n"%(nodenames[e[0]],nodenames[e[1]]))
            g.write("}")
            g.finalize()
            g.show()
