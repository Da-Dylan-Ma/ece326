#!/usr/bin/python
#
# auto test for assignment 1
#
# Tests automatic mode
#

import tester

TEST_CASES = [    
    # assume 10 comes next (surrender if will lose under the assumption)
    #
    ("autoshoe1.txt", "only10.txt", 5, [
        'Hand 1: 7 4 9 \(20\) DOUBLE',
        'Hand 2: 7 K \(17\)',
        'Hand 3: 7 A \(soft 18\)',
        'Hand 4: 7 7 9 \(bust\)',
        'Hand 1: 2 3 A 3 \(soft 19\)',
        'Hand 1: 6 6 \(12\) SURRENDER',
        'Hand 1: Q K \(20\)',
        'Hand 1: A Q \(soft 21\)',
        'Hand 2: A 3 \(soft 14\)',
        'Final Balance: \+\$2\.50',
    ]),  
    ("autoshoe2.txt", "mimic.txt", 8, [
        'Hand 1: 9 9 \(18\) SURRENDER',
        'Hand 1: A A K K \(bust\)',
        'Hand 1: 5 5 7 \(17\) DOUBLE',
        'Hand 1: 2 K 8 \(20\)',
        'Hand 2: 2 8 6 \(16\)',
        'Hand 1: A Q \(blackjack\)',
        'Hand 1: K 6 5 \(21\)',
        'Hand 1: A 9 2 \(12\) DOUBLE',
        'Hand 1: K 9 \(19\) SURRENDER',
        'Final Balance: \$0\.00',
    ]),  
]

def run_test_case(test, case):
    shoe = tester.datapath(case[0], 'asst1') 
    strat = tester.datapath(case[1], 'asst1') 
    test.start_program('./asst1 -f %s -a %s %d'%(shoe, strat, case[2]))
    
    for output in case[-1]:
        test.look(output, 1)
    test.wait_until_end(-1)

def main():
    test = tester.Core('auto test', 20)
    for testcase in TEST_CASES:
        run_test_case(test, testcase)
    
if __name__ == '__main__':
	main()
    
