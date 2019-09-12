#!/usr/bin/python
#
# arguments test for assignment 1
#
# tests combination of invalid command line arguments
#

import tester
import random, os
from sys import maxint

def check_and_wait(test, expr, wait_mark=1):
    if test.lookA(expr, 1) == 0:
        test.wait_until_end(wait_mark)

def main():
    test = tester.Core('arguments test', 15)
    wizard = tester.datapath('wizard.txt', 'asst1')
    shoe = tester.datapath('shoe.txt', 'asst1')
    
    test.start_program('./asst1 -i %d'%(random.randint(-maxint, 0)))   
    check_and_wait(test, r'Error: SEED must be a non-negative integer\.')
       
    test.start_program('./asst1 -a %s 0'%wizard)
    check_and_wait(test, r'Error: NUM must be a natural number\.')
    
    test.start_program('./asst1 -a %s'%wizard)
    check_and_wait(test, 
        r'Error: must specify number of hands when playing automatically\.')
    
    test.start_program('./asst1 -s')
    check_and_wait(test, 
        r'Error: silent mode is only available when playing automatically\.')
    
    seed = 123
    test.start_program('./asst1 -f %s -i %d'%(shoe, seed))
    check_and_wait(test, 
        r'Error: cannot choose both file and random-based shoe\.', 0)
        
    temp = "record.txt"
    test.start_program('./asst1 -f %s -r %s'%(shoe, temp))
    check_and_wait(test, 
        r'Error: recording is only available for random-based shoe\.', 0)
    try:
        os.remove(temp)
    except OSError, e:
        # the student may not have created this file yet
        pass   
        
    test.start_program('./asst1 -f')
    check_and_wait(test, r"\.\/asst1: option requires an argument -- 'f'", 0)

    test.start_program('./asst1 -r')
    check_and_wait(test, r"\.\/asst1: option requires an argument -- 'r'", 0)
    
    test.start_program('./asst1 -i')
    check_and_wait(test, r"\.\/asst1: option requires an argument -- 'i'", 0)
    
    test.start_program('./asst1 -a')
    check_and_wait(test, r"\.\/asst1: option requires an argument -- 'a'", 0)
    
    test.start_program('\./asst1 -h')
    check_and_wait(test, 
        r"usage: \.\/asst1 \[-h\] \[-f FILE\|-i SEED \[-r FILE\]\] \[\[-s\] -a FILE NUM\]", 0)
    
if __name__ == '__main__':
	main()
    
