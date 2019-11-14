#!/usr/bin/python3
#
# easydb update command test for assignment 3
# Assume student's db constructor, connect, and close are working.
#

import asst3
import socket
import random
import string

TOTAL_MARK = 4

def main():
    # Set up the tester.
    test = asst3.start_test('easydb update command test', TOTAL_MARK)

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

    # ===== CASE 1: pk is not an integer. =====

    print("CASE {}: pk is not an integer.".format(case_number))
    (mark, result) = asst3.run_test_case(db.update, ("User", "Bob", ["Jay", "Sung", 5.5, 25], 1), case_number, 1, mark, True, exceptions.PacketError, True) # This should raise an error other than PacketError.
    case_number = case_number + 1

    # ===== CASE 2: version is not an integer. =====

    print("CASE {}: version is not an integer.".format(case_number))
    (mark, result) = asst3.run_test_case(db.update, ("User", 1, ["Jay", "Sung", 5.5, 25], "Bob"), case_number, 1, mark, True, exceptions.PacketError, True) # This should raise an error other than PacketError.
    case_number = case_number + 1

    # ===== CASE 3: Everything is ok. =====

    # Randomly generate attribute information.
    first_name = ''.join(random.choice(string.ascii_lowercase) for i in range(6)).capitalize()
    last_name = ''.join(random.choice(string.ascii_lowercase) for i in range(6)).capitalize()
    height = random.randint(1200, 2000) / 10
    age = random.randint(1, 100) 

    print("CASE {}: Everything is ok.".format(case_number))

    # This should not raise any error.
    try:
        version = db.update("User", 1, [first_name, last_name, height, age], 1)
    except Exception as e:
        print("CASE {} FAIL: {}".format(case_number, str(e)))
    else:
        db.close()

        # Dump database rows.
        rows = asst3.dump(server, 1)

        values1 = [str(1), str(2), first_name, last_name, str(height), str(age)]
        values2 = [str(1), str(2), first_name, last_name, str(int(height)), str(age)]
        if values1 in rows or values2 in rows:
            print("CASE {} PASS".format(case_number))
            mark = mark + 1
        else:
            print("CASE {} FAIL: the updated row cannot be found on the server".format(case_number))

        db.connect(server.host, server.port)

    case_number = case_number + 1

    # ===== CASE 4: non-atomic update =====

    # Randomly generate attribute information.
    first_name = ''.join(random.choice(string.ascii_lowercase) for i in range(6)).capitalize()
    last_name = ''.join(random.choice(string.ascii_lowercase) for i in range(6)).capitalize()
    height = random.randint(1200, 2000) / 10
    age = random.randint(1, 100) 

    print("CASE {}: non-atomic update".format(case_number))

    # This may raise a TransactionAbort error.
    try:
        version = db.update("User", 1, [first_name, last_name, height, age], None)
    except exceptions.TransactionAbort:
        db.close()
        mark = mark + 1
        print("CASE {} PASS".format(case_number))
    except Exception as e:
        db.close()
        print("CASE {} FAIL: {}".format(case_number, str(e)))
    else:
        db.close()

        # Dump database rows.
        rows = asst3.dump(server, 1)

        if [str(1), str(3), first_name, last_name, str(height), str(age)] in rows or [str(1), str(3), first_name, last_name, str(int(height)), str(age)] in rows:
            print("CASE {} PASS".format(case_number))
            mark = mark + 1
        else:
            print("CASE {} FAIL: the updated row cannot be found on the server".format(case_number))

    server.end()
    
    test.add_mark(mark)

if __name__ == '__main__':
    main()
    
