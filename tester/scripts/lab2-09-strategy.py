#!/usr/bin/python3
#
# strategy table test for assignment 2
#

import tester
import asst2

total = 5

def check_strategy(conn, verbose):    
    result, refobj = asst2.load_result('strategy')
    val = asst2.similarity(result, refobj, verbose)
    conn.send(total*val**2)
    

def main():
    test = tester.Proc('strategy test', total)
    mark = test.run_process(check_strategy)
    test.add_mark(mark)

if __name__ == '__main__':
    main()

