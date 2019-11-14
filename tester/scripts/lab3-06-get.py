#!/usr/bin/python3
#
# easydb get command test for assignment 3
# Assume student's db constructor, connect, and close are working.
#

import asst3
import socket

TOTAL_MARK = 3

def main():
    # Set up the tester.
    test = asst3.start_test('easydb get command test', TOTAL_MARK)

    # Import student's code.
    from orm import easydb, exceptions

    mark = 0
    case_number = 1

    # Start the server.
    server = asst3.Server()
    server.start(datafile="preload.txt")

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

    # Set up student's database object and connect to the database.
    db = easydb.Database(tb)
    asst3.try_connect(db, server)

    # ===== CASE 1: Get non-existing row. =====

    print("CASE {}: Get non-existing row.".format(case_number))
    (mark, result) = asst3.run_test_case(db.get, ("User", 300), case_number, 1, mark, True, exceptions.ObjectDoesNotExist) # This should raise an ObjectDoesNotExist error.
    case_number = case_number + 1

    # ===== CASE 2: Table name does not exist. =====

    print("CASE {}: Table name does not exist.".format(case_number))
    (mark, result) = asst3.run_test_case(db.get, ("Hahaha", 1), case_number, 1, mark, True, ValueError) # This should raise an ValueError error.
    case_number = case_number + 1

    # ===== CASE 2: Everything is ok. =====

    print("CASE {}: Everything is ok.".format(case_number))

    # This should not raise any error.
    try:
        values, version = db.get("User", 1)
    except Exception as e:
        db.close()
        print("CASE {} FAIL: {}".format(case_number, str(e)))
    else:
        db.close()
        if values == ["James", "Hartley", 180.3, 38]:
            if server.expect('Request { table_id: 1, command: Get(1) }') is not None:
                print("CASE {} PASS".format(case_number))
                mark = mark + 1
            else:
                print("CASE {} FAIL: server did not receive the Get command".format(case_number))
        else:
            print("CASE {} FAIL: the received row is not correct".format(case_number))
    
    server.end()

    test.add_mark(mark)

if __name__ == '__main__':
    main()

