#!/usr/bin/python3
#
# easydb drop command test for assignment 3
# Assume student's db constructor, connect, and close are working.
#

import asst3
import socket

TOTAL_MARK = 3

def main():
    # Set up the tester.
    test = asst3.start_test('easydb drop command test', TOTAL_MARK)

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

    # ===== CASE 1: Drop non-existing row. =====

    print("CASE {}: Drop non-existing row.".format(case_number))
    (mark, result) = asst3.run_test_case(db.drop, ("User", 300), case_number, 1, mark, True, exceptions.ObjectDoesNotExist) # This should raise an ObjectDoesNotExist error.
    case_number = case_number + 1

    # ===== CASE 2: Table name does not exist. =====

    print("CASE {}: Table name does not exist.".format(case_number))
    (mark, result) = asst3.run_test_case(db.drop, ("Hahaha", 1), case_number, 1, mark, True, ValueError) # This should raise an ValueError error.
    case_number = case_number + 1

    # ===== CASE 3: Everything is ok. =====

    print("CASE {}: Everything is ok.".format(case_number))

    # This should not raise any error.
    try:
        db.drop("User", 2)
    except Exception as e:
        print("CASE {} FAIL: {}".format(case_number, str(e)))
        db.close()    
    else:
        db.close()
        
        # Dump database rows.
        rows = asst3.dump(server, 1)
    
        not_deleted = False
        for row in rows:
            if row[0] == "2":
                not_deleted = True
                break

        if not_deleted:
            print("CASE {} FAIL: the dropped row is still on the server".format(case_number))
        else:
            print("CASE {} PASS".format(case_number))
            mark = mark + 1

    server.end()

    test.add_mark(mark)

if __name__ == '__main__':
    main()
    
