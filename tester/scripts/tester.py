#!/usr/bin/python3
#
# tester.py
#
# Core tester framework for ece326-tester
#

import pexpect
import sys, os
import argparse
import multiprocessing

def datapath(filename, asstdir):
    if 'TESTER_PATH' not in os.environ:
        print("WARNING: TESTER_PATH not in environment, trying ./" + str(filename))
        return filename
    return os.path.join(os.environ['TESTER_PATH'], 'data', asstdir, filename)

def includepath(path=None):
    if path is None:
        path = os.getcwd()
    if path not in sys.path:
        sys.path.append(path)

class Base:
    def __init__(self, message, total):
        parser = argparse.ArgumentParser(description='TestUnit')
        parser.add_argument('-v', '--verbose', action='store_true',
                            help='verbose mode')
        parser.add_argument('nr_times', metavar = 'N', type = int,
                            nargs = '?', choices = range(1, 100),
                            default = 3,
                            help = 'Nr of times to run test')
        args = vars(parser.parse_args())
        self.nr_times = args['nr_times']
        if (args['verbose']):
            self.verbose = 1
        else:
            self.verbose = 0
        self.message = message
        print(message)
        self.mark = 0
        self.total = total
        
    def __del__(self):
        if self.mark < 0:
            self.mark = 0
        if self.mark > self.total:
            print('mark = ' + str(self.mark) + ' is greater than ' \
                        'total = ' + str(self.total))
            print('\nPLEASE REPORT THIS TO THE INSTRUCTOR OR A TA\n')
        print('Mark for ' + self.message + ' is ' + \
              str(self.mark) + ' out of ' + str(self.total))
        marker = open('tester.out', 'a')
        marker.write(self.message + ', ' + str(self.mark) + \
                     ', ' + str(self.total) + '\n')
        marker.close()
        if self.mark == self.total:
            print('PASS')
        else:
            print('FAIL')        

    def add_mark(self, mark):
        self.mark += int(mark)

    def reset_mark(self):
        self.mark = 0

    def get_mark(self):
        return self.mark

class Proc(Base):
    def run_process(self, func, timeout=15):
        with open('tester.log', 'w') as f:
            f.write("\n")
        pconn, cconn = multiprocessing.Pipe()
        self.proc = multiprocessing.Process(target=func, args=(cconn, self.verbose))
        self.proc.start()
        self.proc.join(timeout)
        
        ret = 0
        if self.proc.exitcode is None:
            print("ERROR: TIMEOUT: function did not end")
        elif self.proc.exitcode is 0:
            if pconn.poll():
                ret = pconn.recv()
            else:
                print("ERROR: tester did not return a mark" \
                    "\nPLEASE REPORT THIS TO THE INSTRUCTOR OR A TA")
        self.proc.terminate()
        return ret

class Core(Base):
    def set_timeout(self, timeout):
        self.program.timeout = timeout
        if self.verbose > 0:
            print('This test has a timeout of ' + str(timeout) + ' seconds')

    def start_program(self, path, timeout=5):
        if self.verbose > 0:
            print('STARTING PROGRAM: ' + str(path))
        try:
            self.program = pexpect.spawn(path, [], timeout, encoding='utf-8')
            # pexpect copies all input and output to this file
            self.program.logfile = open('tester.log', 'a')
        except pexpect.ExceptionPexpect as e:
            print("ERROR: " + str(e.message))
            sys.exit(1)

    def shell_command(self, path, timeout=5):
        """
        starts a program under a shell
        """
        if self.verbose > 0:
                print('STARTING PROGRAM: ' + str(path))
        self.program = pexpect.spawn("/bin/bash", ["-c", path], timeout, 
                                     encoding='utf-8')
        # pexpect copies all input and output to this file
        self.program.logfile = open('tester.log', 'a')
    
    def wait_until_end(self, mark=0, exitcode=None):
        """
        wait until a program ends
        
        returns true if program ended successfuly, false otherwise
        
        exitcode: set if an exit code is also expected
        """
        try:
            self.program.expect(pexpect.EOF)
            if self.program.exitstatus is None:
                print('ERROR: program was killed with signal = ' + \
                            str(self.program.signalstatus))
            elif exitcode is not None and \
                self.program.exitstatus != exitcode:
                print('ERROR: program exited with status = ' + \
                            str(self.program.exitstatus))
            else:
                if mark > 0:
                    self.add_mark(mark)
                return True
        except pexpect.TIMEOUT as e:
                print('ERROR: TIMEOUT: program did not end')
        except IOError as e:
                print("ERROR: I/O error: " + str(e.strerror))
        except Exception as e:
                print('ERROR: unexpected problem - ', str(sys.exc_info()[0]))
                print('\nPLEASE REPORT THIS TO THE INSTRUCTOR OR A TA\n')
        if mark < 0:
            self.add_mark(mark)
        return False
    
    def __init__(self, message, total):
        super().__init__(message=message, total=total)
        self.cwd = os.getcwd()
        self.errors = {'EOF' : -1, 'TIMEOUT' : -2,
                       'INCONSISTENT' : -3, 'LOOPING' : -4,
                       'BUG' : -5 }

    def __del__(self):
        if hasattr(self, 'program'):
            self.program.logfile.close()
        super().__del__()

    def send_command(self, cmd=''):
        if self.verbose > 0:
            print('SENDING: ' + cmd)
        if len(cmd) > 0:
            self.program.send(cmd)
        self.program.send("\n")

    def look_internal(self, func, result, mark, report=1):
        try:
            index = func(self, result)
        except pexpect.TIMEOUT as e:
            if report:
                print('ERROR: TIMEOUT: not found: ' + str(result))
            return self.errors['TIMEOUT']
        except pexpect.EOF:
            if report:
                print('ERROR: EOF: not found: ' + str(result))
            return self.errors['EOF']
        except IOError as e:
            if report:
                print("ERROR: I/O error: " + e.strerror)
                print('ERROR: I/O error: not found: ' + str(result))
            return self.errors['EOF']
        except Exception as e:
            print('ERROR: unexpected problem - '+ str(e))
            print('\nPLEASE REPORT THIS TO THE INSTRUCTOR OR A TA\n')
            return self.errors['BUG']
        self.add_mark(mark)
        return index
            
    def _look(self, result):
        if self.verbose > 0:
            print('EXPECTING: ' + str(result))
        index = self.program.expect(result)
        if self.verbose > 0:
            if not hasattr(self.program.match, 'group'):
                print('FOUND: ' + str(self.program.match))
            else:
                print('FOUND: ' + self.program.match.group(0))
        return index
    
    def look(self, result, mark=0):
        return self.look_internal(Core._look, result, mark)

    def look_error(self, result, mark=0):
        # a match is an error,
        # so a non-match should not be reported as an error
        return self.look_internal(Core._look, result, mark, 0)

    def _look_exact(self, result):
        if self.verbose > 0:
            print('EXPECTING: ' + str(result))
        index = self.program.expect_exact(result)
        if self.verbose > 0:
            print('FOUND: ' + str(result))
        return index
    
    def look_exact(self, result, mark=0):
        return self.look_internal(Core._look_exact, result, mark)

    # look anchored by '^' and "\r\n"
    def lookA(self, result, mark = 0):
        return self.look('^' + result + '\r\n', mark)
	
