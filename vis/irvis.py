import gv


" [shape=none, margin 0,label=<"
"<TABLE>"
"</TABLE>"
">];"

def showFunction(f):
        with gv.GraphViz() as g:
            g.write("digraph g {\n")
            for block in f:
                g.write(block.name)
                g.write(" [shape=none, margin 0,label=<\n")
                g.write("<TABLE>\n")
                g.write("<TR><TD>%s:</TD></TR>\n"%block.name)
                for i in block:
                    insStr = str(i)
                    insStr = insStr.replace('>','gt').replace('<','lt')
                    g.write("<TR><TD>%s</TD></TR>\n"%insStr)
                g.write("</TABLE>\n")
                g.write(">];\n")
                
                if len(block):
                    for successor in block[-1].getSuccessors():
                        g.write("%s -> %s;"%(block.name,successor.name))
                   
            g.write("}")
            g.finalize()
            g.show()
