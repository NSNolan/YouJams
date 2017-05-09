from YJExceptions import *

class thing(object):
    def __init__(self, val, id):
        self.val = val
        self.id = id
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.val == other.val
        return False
    
    def __hash__(self):
        return hash((self.val))
    
    def __str__(self):
        return "poop"

    def foo(self):
        print "hi " + str(self)

t = thing(1, 'a')
t.foo()
print "hi " + str(t)

try:
    raise JamDownloadNoDirectoryError
except JamError as e:
    print "hi" + str(e)

#t1 = thing(1, 'a')
#t2 = thing(2, 'a')
#t3 = thing(2, 'b')
#
#s = set()
#s.add(t1)
#s.add(t2)
#
#for t in s:
#    t.printThing()
#
#print bool(t1 == t2)
#print bool(t2 == t3)
#
##print str(t1.hash())
##print str(t2.hash())
##print str(t3.hash())
#
#s.add(t3)
#
#for t in s:
#    t.printThing()
#
##array = [t1, t2]
##
##
##array.append(t3)
##
##for t in array:
##    t.printThing()
##
##t3.val = 10
##
##for t in array:
##    t.printThing()
