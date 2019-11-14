#!/usr/bin/python3
#
# easydb insert command test for assignment 3
# Assume student's db constructor, connect, and close are working.
#

import asst3
import socket
import random
import string

TOTAL_MARK = 6

def main():
    # Set up the tester.
    test = asst3.start_test('easydb insert command test', TOTAL_MARK)
    
    # Import student's code.
    from orm import easydb, exceptions

    mark = 0
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

    # Set up student's database object and connect to the database.
    db = easydb.Database(tb)
    asst3.try_connect(db, server)

    # ===== CASE 1: There is an extra element in the inserted row. =====

    print("CASE {}: There is an extra element in the inserted row.".format(case_number))
    (mark, result) = asst3.run_test_case(db.insert, ("User", ["Jay", "Sung", 5.5, 31, 33]), case_number, 1, mark, True, ValueError) # This should raise a ValueError error.
    case_number = case_number + 1

    # ===== CASE 2: There is missing an element in the inserted row. =====

    print("CASE {}: There is missing an element in the inserted row.".format(case_number))
    (mark, result) = asst3.run_test_case(db.insert, ("User", ["Jay", "Sung", 5.5]), case_number, 1, mark, True, ValueError) # This should raise a ValueError error.
    case_number = case_number + 1

    # ===== CASE 3: Type of the column in the inserted row does not match. =====

    print("CASE {}: Type of the column in the inserted row does not match.".format(case_number))
    (mark, result) = asst3.run_test_case(db.insert, ("User", ["Jay", "Sung", "Dog", 31]), case_number, 1, mark, True, ValueError) # This should raise a ValueError error.
    case_number = case_number + 1

    # ===== CASE 4: Table name is not a string. =====

    print("CASE {}: Table name is not a string.".format(case_number))
    (mark, result) = asst3.run_test_case(db.insert, (123, ["Jay", "Sung", 5.5, 31]), case_number, 1, mark, True, ValueError) # This should raise a ValueError error.
    case_number = case_number + 1

    # ===== CASE 5: Table name does not exist in the database. =====

    print("CASE 5: Table name does not exist in the database.".format(case_number))
    (mark, result) = asst3.run_test_case(db.insert, ("Test", ["Jay", "Sung", 5.5, 31]), case_number, 1, mark, True, ValueError) # This should raise a ValueError error.
    case_number = case_number + 1

    # ===== CASE 6: Everything is ok. =====

    print("CASE {}: Everything is ok.".format(case_number))

    # Randomly generate attribute information.
    first_name = ''.join(random.choice(string.ascii_lowercase) for i in range(6)).capitalize()
    last_name = ''.join(random.choice(string.ascii_lowercase) for i in range(6)).capitalize()
    height = random.randint(1200, 2000) / 10
    age = random.randint(1, 100) 

    # This should not raise any error.
    try:
        pk, version = db.insert("User", [first_name, last_name, height, age])
    except Exception as e:
        db.close()
        print("CASE {} FAIL: {}".format(case_number, str(e)))
    else:
        db.close()
    
        # Dump database rows.
        rows = asst3.dump(server, 1)

        if [str(pk), str(version), first_name, last_name, str(height), str(age)] in rows or [str(pk), str(version), first_name, last_name, str(int(height)), str(age)] in rows:
            print("CASE {} PASS".format(case_number))
            mark = mark + 1
        else:
            print("CASE {} FAIL: the inserted row cannot be found on the server".format(case_number))

    server.end()

    test.add_mark(mark)

if __name__ == '__main__':
    main()
    
