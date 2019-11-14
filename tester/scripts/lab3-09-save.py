#!/usr/bin/python3
#
# orm save command test for assignment 3
# Assume student's db constructor, connect, and close are working.
# Assume student's orm basic functionalities (orm basic test) are working.
#

import asst3
import socket
import tester
import importlib

asst3_schema = asst3.load_module('asst3_schema')

TOTAL_MARK = 6

def main():
    # Set up the tester.
    test = asst3.start_test('orm save command test', TOTAL_MARK)

    # Import student's code.
    import orm 

    mark = 0
    case_number = 1

    # Start the server.
    server = asst3.Server()
    server.start()

    # Set up student's database object and connect to the database.
    db = orm.setup("easydb", asst3_schema)
    asst3.try_connect(db, server)

    # Create some row objects for testing.
    joe = asst3_schema.User(db, firstName="Joe", lastName="Harris", age=32)
    jeffrey = asst3_schema.User(db, firstName="Jeffrey", lastName="Fang", height=999.9)
    alice = asst3_schema.User(db, firstName="Alice", lastName="Stuart", age=18)
    account1 = asst3_schema.Account(db, user=alice, type="Yes")
    account2 = asst3_schema.Account(db, user=jeffrey, type="Special")

    # ===== CASE 1: Save a row object whose field is not in choices. =====

    print("CASE {}: Save a row object whose field is not in choices.".format(case_number))
    (mark, result) = asst3.run_test_case(account1.save, (), case_number, 1, mark, True, ValueError) # This should raise a ValueError error.
    case_number = case_number + 1

    # ===== CASE 2: Save a new row object to the database with no error (insert). =====

    print("CASE {}: Save a new row object to the database with no error (insert).".format(case_number))

    # This should not raise any error.
    try:
        joe.save()
    except Exception as e:
        print("CASE {} FAIL: {}".format(case_number, str(e)))
    else:
        db.close()

        # Dump database rows.
        rows = asst3.dump(server, 1)

        if [str(1), str(1), "Joe", "Harris", "0", "32"] in rows or [str(2), str(1), "Joe", "Harris", "0", "32"] in rows:
            print("CASE {} PASS".format(case_number))
            mark = mark + 1
        else:
            print("CASE {} FAIL: the saved row cannot be found on the server".format(case_number))

        db.connect(server.host, server.port)

    case_number = case_number + 1

    # ===== CASE 3: Cascade save new row objects to the database with no error (insert). =====

    print("CASE {}: Cascade save new row objects to the database with no error (insert).".format(case_number))

    # This should not raise any error.
    try:
        account2.save()
    except Exception as e:
        print("CASE {} FAIL: {}".format(case_number, str(e)))
    else:
        db.close()

        # Dump database rows.
        client = asst3.Client(server)
        user_rows = client.dump(1)
        account_rows = client.dump(2)
        client.close()

        if ([str(2), str(1), "Jeffrey", "Fang", "999.9", "0"] in user_rows or [str(3), str(1), "Jeffrey", "Fang", "999.9", "0"] in user_rows) \
        and ([str(1), str(1), "2", "Special", "0"] in account_rows or [str(2), str(1), "2", "Special", "0"] in account_rows \
        or [str(1), str(1), "3", "Special", "0"] in account_rows or [str(2), str(1), "3", "Special", "0"] in account_rows):
            print("CASE {} PASS".format(case_number))
            mark = mark + 1
        else:
            print("CASE {} FAIL: the saved row cannot be found on the server".format(case_number))

        db.connect(server.host, server.port)

    case_number = case_number + 1

    # ===== CASE 4: Save a existing row object to the database (update). =====

    joe.height = 663.1

    print("CASE {}: Save a existing row object to the database (update).".format(case_number))

    # This should not raise any error.
    try:
        joe.save()
    except Exception as e:
        print("CASE {} FAIL: {}".format(case_number, str(e)))
    else:
        db.close()

        # Dump database rows.
        rows = asst3.dump(server, 1)

        if [str(1), str(2), "Joe", "Harris", "663.1", "32"] in rows or [str(2), str(2), "Joe", "Harris", "663.1", "32"] in rows:
            print("CASE {} PASS".format(case_number))
            mark = mark + 1
        else:
            print("CASE {} FAIL: the saved row cannot be found on the server".format(case_number))

        db.connect(server.host, server.port)

    case_number = case_number + 1

    # ===== CASE 5: Non-atomic save (non-atomic update) =====

    joe.age = 50

    print("CASE {}: Non-atomic save (non-atomic update)".format(case_number))

    # This may raise a TransactionAbort error.
    try:
        joe.save()
    except orm.TransactionAbort:
        print("CASE {} PASS".format(case_number))
        mark = mark + 1
    except Exception as e:
        print("CASE {} FAIL: {}".format(case_number, str(e)))
    else:
        db.close() 

        # Dump database rows.
        rows = asst3.dump(server, 1)

        if [str(1), str(3), "Joe", "Harris", "663.1", "50"] in rows or [str(2), str(3), "Joe", "Harris", "663.1", "50"] in rows:
            print("CASE {} PASS".format(case_number))
            mark = mark + 1
        else:
            print("CASE {} FAIL: the saved row cannot be found on the server".format(case_number))

        db.connect(server.host, server.port)

    case_number = case_number + 1

    # ===== CASE 6: Row object's id does not exist in the database anymore (invalid reference). =====

    jeffrey.pk = 888

    print("CASE {}: Row object's id does not exist in the database anymore (invalid reference).".format(case_number))

    # This should raise an InvalidReference error.
    try:
        account2.save()
    except orm.exceptions.InvalidReference:
        if jeffrey.pk is None:
            mark = mark + 1
            print("CASE {} PASS".format(case_number))
        else:
            print("CASE {} FAIL: pk is not set back to None".format(case_number))
    except Exception as e:
        print("CASE {} FAIL: {}".format(case_number, str(e)))
    else:
        print("CASE {} FAIL: {}".format(case_number, "expected InvalidReference"))

    db.close()

    server.end()

    test.add_mark(mark)

if __name__ == '__main__':
    main()

