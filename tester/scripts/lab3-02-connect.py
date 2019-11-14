#!/usr/bin/python3
#
# easydb connection test for assignment 3
#

import asst3 
import socket

TOTAL_MARK = 2

def main():
    # Set up the tester.
    test = asst3.start_test('easydb connection test', TOTAL_MARK)
    
    # Import student's code.
    from orm import easydb

    case_number = 1

    # Start the server.
    server = asst3.Server()
    server.start()

    # database tables
    tb = (
        ("User", ( # table_name
            ("firstName", str), # (column_name, type)
            ("lastName", str),
            ("height", float),
            ("age", int),
        )),
        
        ("Account", (
            ("user", "User"), # (column_name, table_reference)
            ("type", str),
            ("balance", float),
        ))
    )

    # ===== CASE 1: Connect to the database. =====

    print("CASE {}: Connect to the database.".format(case_number))

    try:
        db = easydb.Database(tb)
        asst3.try_connect(db, server)
    except OSError:
        print("CASE {} FAIL: could not connect to database".format(case_number))
        server.end()
        return
    else:
        if server.expect("Connected to 127.0.0.1:") is None:
            print("CASE {} FAIL: server did not receive connection".format(case_number))
            server.end()
            return
        else:
            test.add_mark(1)
            print("CASE 1 PASS")
    
    case_number = case_number + 1

    # ===== CASE 2: Close the connection to database. =====

    print("CASE {}: Close the connection to database.".format(case_number)) 

    db.close()
    if server.look(r"Request { table_id: \d+, command: Exit }") is None:
        print("CASE {} FAIL: server did not receive the Exit command".format(case_number))
    else:
        print("CASE {} PASS".format(case_number))
        test.add_mark(1)

    server.end()

if __name__ == '__main__':
    main()
    
