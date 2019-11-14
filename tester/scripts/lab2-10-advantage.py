#!/usr/bin/python3
#
# player advantage test for assignment 2
#

import tester
import asst2

total = 5
cutoff = 0.005

def check_advantage(conn, verbose):
    result, refobj = asst2.load_result('advantage')
    diff = abs(refobj - result)
    if asst2.isclose(diff, 0):
        conn.send(total)
        return
    
    if diff < cutoff:
        if verbose:
            print("Almost correct player advantage.")
        mark = int(total * (cutoff - diff) / cutoff)
    else:
        if verbose:
            print("Incorrect player advantage.")
        mark = 0
    conn.send(mark)


def main():
    test = tester.Proc('advantage test', total)
    mark = test.run_process(check_advantage)
    test.add_mark(mark)

if __name__ == '__main__':
    main()
