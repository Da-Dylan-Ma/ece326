import tester # tester
import random
import pexpect
import time
import struct
import sys
import socket
import importlib.util

EASYDB_PATH = "/cad2/ece326f/tester/bin/easydb"

def load_module(modname):
    path = tester.datapath(modname + ".py", 'asst3')
    spec = importlib.util.spec_from_file_location(modname, path)
    mod = importlib.util.module_from_spec(spec)
    tester.includepath()
    spec.loader.exec_module(mod)
    return mod


def try_connect(db, server):
    retry = 0
    while retry < 3:
        try:
            return db.connect(server.host, server.port)
        except ConnectionRefusedError:
            retry += 1
            print("Connection Refused -- retrying in 1 second")
            time.sleep(1)
    db.connect(server.host, server.port)        

class Client:
    def __init__(self, server):
        # make sure server is running
        assert(server.program)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((server.host, server.port)) 
    
    # Dump rows of a table from the database.
    # table_id: int, table id of the table.   
    def dump(self, table_id):
        self.sock.send(bytearray([0, 0, 0, 42, 0, 0, 0, table_id]))
        resp = self.sock.recv(4096)

        if struct.unpack("!i", resp[:4])[0] == 1:
            rows = resp[4:].decode("utf-8").split('\n')
            return [ row.split('\t') for row in rows if len(row) > 0 ]
        
        return None
    
    def close(self):
        self.sock.close()
        del self.sock
        
    def __del__(self):
        if hasattr(self, 'sock'):
            self.sock.close()

# convenience function
def dump(server, table_id):
    client = Client(server)
    return client.dump(table_id)
 
class Server:
    def __init__(self, filename=None):
        self.host = "localhost"
        self.port = random.randint(1024, 9999)
        if filename is None:
            self.schema = tester.datapath('export.txt', 'asst3')
        else:
            self.schema = filename
       
    def start(self, datafile=None):
        if datafile is not None:
            self.datafile = tester.datapath(datafile, 'asst3')
        else:
            self.datafile = ""
        path = "%s -g %d %s localhost %s"%(EASYDB_PATH, self.port, self.schema,
            self.datafile)
        self.program = pexpect.spawn(path, [], encoding='utf-8')
        self.program.logfile = open('tester.log', 'a')
        self.program.logfile.write("\n-------- %s --------\n\n"%sys.argv[0])
        idx = self.program.expect([r"\]", pexpect.EOF])
        self.program.logfile.flush()
        if idx != 0:
            self.program.close(force=True)
            self.program.logfile.close()
            del self.program
            return False
        return True

    def expect(self, substr, timeout=3):
        try:
            return self.program.expect_exact(substr, timeout=timeout)
        except:
            return None     

    def look(self, regex, timeout=3):
        try:
            return self.program.expect(regex, timeout=timeout)
        except:
            return None    

    def end(self):
        self.program.terminate(force=True)
        self.program.expect(pexpect.EOF)
        self.program.logfile.flush()
        self.program.close(force=True)
        self.program.logfile.close()
        del self.program

    def __del__(self):
        if hasattr(self, 'program'):
            self.end()
            
def start_test(testname, marks):
    test = tester.Core(testname, marks)
    tester.includepath()
    return test

# Run the test case of a given function and return updated total mark.
# func: python function, function to run the test case on; funcArgs: tuple, arguments of the function to run; case_number: int or str, case number; 
# mark:int, mark of this test case; total_mark: int, total mark so far; error_raise: bool, True if an given error should raise in the test casek;
# error: error that should / should not raise in the test case; false_error: bool, False if other errors can raise but not this one.
def run_test_case(func, funcArgs, case_number, mark, total_mark, error_raise, error, false_error=False):
    result = None

    try:

        # Run the funcion with given arguments.
        result = func(*funcArgs)

    except error as e:

        # If other errors can raise but not this one...
        if false_error:
            print("CASE {} FAIL: an error except {} should raise, but {} raises instead: {}".format(case_number, error, error, str(e)))

        # If the given error should raise...
        elif error_raise and (not false_error):
            total_mark = total_mark + mark
            print("CASE {} PASS".format(case_number))

        # If an error should not raise...
        else:
            print("CASE {} FAIL: no error should raise, but an errror raises: {}".format(case_number, str(e)))

    except Exception as e:

        # If other errors raise but not this particular one...
        if false_error:
            total_mark = total_mark + mark
            print("CASE {} PASS".format(case_number))
        else:

            # If a particular error should raise but other error raise instead...
            if error_raise:
                print("CASE {} FAIL: {} should raise, but other error raises instead: {}".format(case_number, error, str(e)))
            # If an error raises while the code should not raise any error...
            else:
                print("CASE {} FAIL: no error should raise, but an error raises: {}".format(case_number, str(e)))

    else:
        
        # If an error should raise...
        if error_raise:
            if false_error:
                print("CASE {} FAIL: an error except {} should raise, but no error raises".format(case_number, error))
            else:
                print("CASE {} FAIL: {} should raise, but no error raises".format(case_number, error))

        # If an error should not raise...
        else:
            total_mark = total_mark + mark
            print("CASE {} PASS".format(case_number))

    # Return the updated total mark.
    return (total_mark, result)
