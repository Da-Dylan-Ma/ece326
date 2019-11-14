#!/usr/bin/python3
#
# performance test for assignment 1
#

import tester

TEST_CASES = [
    
    # according to wizard of odds
    # https://wizardofodds.com/games/blackjack/appendix/16/
    #
    (0, "wizard.txt", 2000000, 'Hands Played: 2000000',
        'Final Balance: \+\$200494\.50', 'Player Advantage: 10\.02%',
        25,
    ),
    
    # no bust strategy (only on hard 12-19, surrender if possible)
    #
    (1, "nobust.txt", 2000000, 'Hands Played: 2000000',
        'Final Balance: \+\$177492\.50', 'Player Advantage: 8\.875%',
        20,
    ),

    # mimic the dealer (surrender if losing with hand above h17/s18)
    #
    (2, "mimic.txt", 2000000, 'Hands Played: 2000000',
        'Final Balance: \+\$63428\.00', 'Player Advantage: 3\.171%',
        15,
    ),
    
    # assume 10 comes next (surrender if will lose under the assumption)
    #
    (3, "only10.txt", 2000000, 'Hands Played: 2000000',
        'Final Balance: \+\$159741\.50', 'Player Advantage: 7\.987%',
        10,
    ),
]

def run_test_case(test, case):
    path = tester.datapath(case[1], 'asst1')
    test.start_program('./asst1 -s -i %d -a %s %d'%(case[0], path, case[2]),
        timeout=case[6])
    
    # speed up error detection (otherwise it'd take 30 seconds to fail)
    if test.lookA(case[3], 0) == 0:
        test.lookA(case[4], 4)
        test.lookA(case[5], 1)

def main():
    test = tester.Core('performance test', 20)
    for testcase in TEST_CASES:
        run_test_case(test, testcase)
    
if __name__ == '__main__':
    main()
    
