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
                #output node labels
                g.write("%s [shape=none, margin 0,label=<\n" % nodenames[node] )
                g.write("<TABLE>\n")
                g.write("<TR>")
                
                if len(node.children):
                    for idx,child in enumerate(node.children):
                        portname = nodenames[node] + "IN" + str(idx)
                        g.write("<TD PORT=\"%s\" >%s</TD>"%(portname,node.instr.read[idx]))
                else:
                    g.write("<TD>X</TD>")
                
                g.write("</TR>\n")
                g.write("<TR><TD COLSPAN=\"%d\">%s</TD></TR>\n"%(span,node.instr.getDagDisplayText()))
                g.write("<TR>")
                
                if len(node.instr.assigned):
                    for idx,v in enumerate(node.instr.assigned):
                        portname = nodenames[node] + "OUT" + str(idx)
                        g.write("<TD PORT=\"%s\" COLSPAN=\"%d\">%s</TD>"%(portname,span,v))
                else:
                    g.write("<TD COLSPAN=\"%d\">X</TD>\n"%span)
                g.write("</TR>\n")
                g.write("</TABLE>\n")
                g.write(">];\n")
            for n in dg.nodes:
                for inidx,inputtuble in enumerate(n.children):
                    outidx,othernode = inputtuble
                    startport = nodenames[othernode] + "OUT" + str(outidx)
                    endport = nodenames[n] + "IN" + str(inidx)
                    g.write("%s:%s:s -> %s:%s:n;\n"%(nodenames[othernode],startport,nodenames[n],endport))
            
            for n in dg.nodes:
                for other in n.control:
                    g.write("%s -> %s [style=dotted];\n"%(nodenames[other],nodenames[n]))
            g.write("}")
            g.finalize()
            g.show()
