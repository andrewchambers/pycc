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
                span = max(len(node.instr.read),1)
                g.write("%s [shape=none, margin 0,label=<\n" % nodenames[node] )
                g.write("<TABLE>\n")
                g.write("<TR>")
                if len(node.instr.assigned):
                    for v in node.instr.assigned:
                        g.write("<TD COLSPAN=\"%d\">%s</TD>"%(span,v))
                else:
                    g.write("<TD COLSPAN=\"%d\">X</TD>\n"%span)
                g.write("</TR>\n")
                g.write("<TR><TD COLSPAN=\"%d\">%s</TD></TR>\n"%(span,node.instr.getDagDisplayText()))
                g.write("<TR>")
                if len(node.instr.read):
                    for v in node.instr.read:
                        g.write("<TD>%s</TD>"%v)
                else:
                    g.write("<TD>X</TD>")
                g.write("</TR>\n")
                
                g.write("</TABLE\n>")
                g.write(">];\n")
            for n in dg.nodes:
                for other in n.outs:
                    g.write("%s -> %s;\n"%(nodenames[n],nodenames[other]))
            
            for n in dg.nodes:
                for other in n.control:
                    g.write("%s -> %s [style=dotted];\n"%(nodenames[n],nodenames[other]))
            g.write("}")
            g.finalize()
            g.show()
