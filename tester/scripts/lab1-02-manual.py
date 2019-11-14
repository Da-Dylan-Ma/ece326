#!/usr/bin/python3
#
# manual test for assignment 1
#
# Tests manual mode
#

import tester

OPTIONS = [
    ("S", "Stand \(S\)"),
    ("H", "Hit \(H\)"),
    ("D", "Double \(D\)"),
    ("P", "Split \(P\)"),
    ("R", "Surrender \(R\)"),
]

def action(test, ops, cmd, mark=0):
    regex = " ".join([s for c, s in OPTIONS if c in ops])
    test.look(regex, mark)
    test.send_command(cmd)

def begin(test, shoefile):
    shoe = tester.datapath(shoefile, 'asst1')
    test.start_program('./asst1 -f %s'%shoe)

def prompt(test, cmd=''):
    test.look('Press Any Key to Continue, \(Q to Quit\):')
    test.send_command(cmd)

def main():
    test = tester.Core('manual test', 40)
    
    # test if either or both have blackjack
    begin(test, 'bjshoe.txt')
    test.look('Dealer: A K \(blackjack\)', 1)
    test.look('Result: -\$1\.00', 1)
    prompt(test)
    test.look('Hand 1: T A \(blackjack\)', 1)
    test.look('Result: \+\$1\.50', 1)
    prompt(test)
    test.look('Result: \$0\.00', 1)
    prompt(test, 'Q')
    
    # test output of hitting
    begin(test, 'hitshoe.txt')
    action(test, "SHDR", 'H', 1)
    action(test, "SH", 'H')
    action(test, "SH", 'r')         # not allowed
    action(test, "SH", 'p')         # not allowed
    action(test, "SH", 'd')         # not allowed
    action(test, "SH", 'H')
    action(test, "SH", 'x')         # random character
    action(test, "SH", 'hit', 1)    # test if lowercase accepted
    # bust, no more action
    test.look('Result: -\$1\.00', 1)
    prompt(test)

    action(test, "SHDR", 'H')
    # got 21, should have no more action
    test.look('Dealer: A 6 8 8 \(bust\)', 1)
    test.look('Result: \+\$1\.00', 1)
    prompt(test)
    
    action(test, "SHDR", 'H')
    action(test, "SH", 'S', 1)
    test.look('Dealer: 7 8 6 \(21\)', 1)
    test.look('Result: -\$1\.00', 1)
    prompt(test, 'Q')
    
    begin(test, 'dblshoe.txt')
    action(test, "SHDR", 'please')
    action(test, "SHDR", 'd', 1)
    test.look('Dealer: K 6 3 \(19\)', 1)
    test.look('Hand 1: 5 6 Q \(21\)', 1)
    test.look('Result: \+\$2\.00', 1)
    prompt(test)
    
    action(test, "SHDR", 'r')
    # dealer should not hit after a surrender
    test.look('Dealer: 2 9 \(11\)', 1)
    test.look('Hand 1: 5 J \(15\) SURRENDER', 1)
    test.look('Result: -\$0\.50', 1)
    prompt(test)
    action(test, "SHDPR", 'ddd')
    test.look('Dealer: 7 7 \(14\)', 1)
    test.look('Hand 1: 6 6 Q \(bust\) DOUBLE', 1)
    test.look('Result: -\$2\.00', 1)
    prompt(test, 'Q')
    
    # test output of splitting
    begin(test, 'splshoe.txt')
    action(test, "SHDPR", 'P', 1)
    action(test, "SHDP", 'P', 1)
    action(test, "SHDP", 'P')
    # no more split now
    action(test, "SHD", 'P', 1)
    # should not be allowed
    action(test, "SHD", 'R')
    action(test, "SHD", 'S', 1)
    action(test, "SHD", 'D')
    action(test, "SHD", 'h')
    action(test, "SH", 'h', 1)
    action(test, "SHD", 'HIT')
    action(test, "SH", 'stand')
    test.look('Hand 1: 8 8 \(16\)', 1)
    test.look('Hand 2: 8 8 2 \(18\) DOUBLE', 1)
    test.look('Hand 3: 8 8 A J \(bust\)', 1)
    test.look('Hand 4: 8 8 A \(17\)', 1)
    test.look('Result: -\$5\.00', 1)
    prompt(test)
    
    action(test, "SHDPR", 'P')
    test.look('Dealer: A A 7 \(soft 19\)', 1)
    test.look('Hand 1: A 5 \(soft 16\)', 1)
    test.look('Hand 2: A 6 \(soft 17\)')
    test.look('Result: -\$2\.00', 1)
    test.look('Current Balance: -\$7\.00', 1)
    prompt(test)
    
    # after split, soft 21 is not blackjack
    action(test, "SHDPR", 'P')
    test.look('Hand 1: A J \(soft 21\)', 1)
    prompt(test)
    
    # dealer should not hit after double bust
    action(test, "SHDPR", 'P')
    action(test, "SHD", 'h', 1)
    action(test, "SHD", 'h')
    test.look('Dealer: T 3 \(13\)', 1)
    prompt(test, 'Q')
    
if __name__ == '__main__':
    main()
    
