#!/usr/bin/python3
#
# initial probability table test for assignment 2
#

import tester
import asst2

total = 5

def check_initial(conn, verbose):    
    result, refobj = asst2.load_result('initial')
    val = asst2.similarity(result, refobj, verbose)
    conn.send(total*val**2)
    

def main():
    test = tester.Proc('initial test', total)
    mark = test.run_process(check_initial)
    test.add_mark(mark)

if __name__ == '__main__':
    main()
    
