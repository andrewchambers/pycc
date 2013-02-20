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
            g.write("rankdir=\"TB\";\n")
            for node in dg.nodes:
                span = max(len(node.instr.read),1)
                g.write("%s [shape=none, margin 0,label=<\n" % nodenames[node] )
                g.write("<TABLE>\n")
                g.write("<TR>")
                
                if len(node.ins):
                    for port in node.ins:
                        portname = nodenames[node] + "IN" + str(port.idx)
                        g.write("<TD PORT=\"%s\" >%s</TD>"%(portname,port.var))
                else:
                    g.write("<TD>X</TD>")
                
                g.write("</TR>\n")
                g.write("<TR><TD COLSPAN=\"%d\">%s</TD></TR>\n"%(span,node.instr.getDagDisplayText()))
                g.write("<TR>")
                
                if len(node.outs):
                    for port in node.outs:
                        portname = nodenames[node] + "OUT" + str(port.idx)
                        g.write("<TD PORT=\"%s\" COLSPAN=\"%d\">%s</TD>"%(portname,span,port.var))
                else:
                    g.write("<TD COLSPAN=\"%d\">X</TD>\n"%span)
                g.write("</TR>\n")
                g.write("</TABLE\n>")
                g.write(">];\n")
            for n in dg.nodes:
                for port in n.outs:
                    startport = nodenames[n] + "OUT" + str(port.idx)
                    for edge in port.edges:
                        otherport = edge.head
                        othernode = otherport.parent
                        endport = nodenames[othernode] + "IN" + str(otherport.idx)
                        g.write("%s:%s:s -> %s:%s:n;\n"%(nodenames[n],startport,nodenames[othernode],endport))
            
            for n in dg.nodes:
                for other in n.control:
                    g.write("%s -> %s [style=dotted];\n"%(nodenames[n],nodenames[other]))
            g.write("}")
            g.finalize()
            g.show()
