#!/usr/bin/python3
#
# memory leak test for assignment 1
#

import tester
import sys

def find_or_exit(test, regex):
    idx = test.look([regex, tester.pexpect.TIMEOUT])
    if idx != 0:
        sys.exit(0)

def exit_on_leak(test, regex):
    idx = test.look([regex, tester.pexpect.TIMEOUT, tester.pexpect.EOF])
    if idx == 0:
        nbytes = int(test.program.match.group(1))
        # leak detected
        if nbytes > 0:
            sys.exit(0)

def main():
    test = tester.Core('memory test', 5)
    path = tester.datapath("wizard.txt", 'asst1')
    test.start_program('valgrind ./asst1 -s -i %d -a %s %d'%(4, path, 10000),
        timeout=10)
    
    find_or_exit(test, 'Hands Played: 10000')
    find_or_exit(test, 'Final Balance: \+\$1103\.00')
    find_or_exit(test, 'Player Advantage: 11\.03\%')
    
    test.set_timeout(1)
    exit_on_leak(test, 'definitely lost: .+? bytes in (\d+) blocks')
    exit_on_leak(test, 'indirectly lost: .+? bytes in (\d+) blocks')
    exit_on_leak(test, 'possibly lost: .+? bytes in (\d+) blocks')
    test.add_mark(3)
    exit_on_leak(test, 'still reachable: .+? bytes in (\d+) blocks')
    test.add_mark(2)
    
if __name__ == '__main__':
    main()
    
