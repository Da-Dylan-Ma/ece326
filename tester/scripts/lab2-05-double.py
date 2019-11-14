#!/usr/bin/python3
#
# double ev table test for assignment 2
#

import tester
import asst2

total = 10

def check_double(conn, verbose):    
    result, refobj = asst2.load_result('double')
    val = asst2.similarity(result, refobj, verbose)
    conn.send(total*val**2)
    

def main():
    test = tester.Proc('double test', total)
    mark = test.run_process(check_double)
    test.add_mark(mark)

if __name__ == '__main__':
    main()

    
