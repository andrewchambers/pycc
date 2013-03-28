
def DAG2Text(dag):
    for n in dag.getNodes():
        for o in n.getOutNodes():
            print "%s -> %s" % (n.__class__.__name__, o.__class__.__name__)