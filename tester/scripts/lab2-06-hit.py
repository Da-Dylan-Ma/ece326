#!/usr/bin/python3
#
# hit ev table test for assignment 2
#

import tester
import asst2

total = 20

def check_hit(conn, verbose):    
    result, refobj = asst2.load_result('hit')
    val = asst2.similarity(result, refobj, verbose)
    conn.send(total*val**2)
    

def main():
    test = tester.Proc('hit test', total)
    mark = test.run_process(check_hit)
    test.add_mark(mark)

if __name__ == '__main__':
    main()

    
