#!/usr/bin/python3
#
# table test for assignment 2
#

import tester
import random
import string

def main():
    test = tester.Core('table test', 5)
    tester.includepath()
    import table
    t = table.Table(int, "abcdefg", range(7))
    
    init = random.randint(0, 99)
    skip = random.randint(1, 9)
    curr = init
    for x in t.xlabels:
        for y in t.ylabels:
            t[y,x] = curr
            curr += skip
    
    curr = init
    for x in t.xlabels:
        for y in t.ylabels:
            if t[y,x] != curr:
                print("table value mismatch (what is set cannot be gotten)")
                return
            curr += skip
    
    test.add_mark(2)
    
    t2 = table.Table(float, string.digits, range(10))
    for x in t2.xlabels:
        for y in t2.ylabels:
            t2[y,x] = random.random()*2 - .8
            
    curr = init
    for x in t.xlabels:
        for y in t.ylabels:
            if t[y,x] != curr:
                print("write to another table affects this table!")
                return
            curr += skip
        
    test.add_mark(2)
           
    del t[3,'b']            
    if t[3,'b'] is not None:
        print("cannot delete from table")
        return
        
    test.add_mark(1)

if __name__ == '__main__':
    main()
    
