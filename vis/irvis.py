

def IR2Text(module):
    for f in module:
        print "func %s: "%f.getName()
        for block in f:
            print "\tblock %s:"%block.getName()
            for i in block:
                print "\t\t%s"%i