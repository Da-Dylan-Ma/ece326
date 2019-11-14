#!/usr/bin/python3
#
# easydb scan command test for assignment 3
# Assume student's db constructor, connect, and close are working.
#

import asst3
import socket

TOTAL_MARK = 14

def main():
    # Set up the tester.
    test = asst3.start_test('easydb scan command test', TOTAL_MARK)

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

    # ===== CASE 1: Table name does not exist. =====

    print("CASE {}: Table name does not exist.".format(case_number))
    (mark, result) = asst3.run_test_case(db.scan, ("Bob", ("firstName", easydb.OP_EQ, "James")), case_number, 1, mark, True, ValueError) # This should raise an ValueError error.
    case_number = case_number + 1

    # ===== CASE 2: Query is not a tuple. =====

    print("CASE {}: Query is not a tuple.".format(case_number))
    (mark, result) = asst3.run_test_case(db.scan, ("User", 3), case_number, 1, mark, True, Exception) # This should raise an error.
    case_number = case_number + 1

    # ===== CASE 3: Query has more than 3 elements. =====

    print("CASE {}: Query has more than 3 elements.".format(case_number))
    (mark, result) = asst3.run_test_case(db.scan, ("User", ("age", easydb.OP_EQ, 27, 90)), case_number, 1, mark, True, Exception) # This should raise an error.
    case_number = case_number + 1

    # ===== CASE 4: Query has less than 3 elements. =====

    print("CASE {}: Query has less than 3 elements.".format(case_number))
    (mark, result) = asst3.run_test_case(db.scan, ("User", ("age", easydb.OP_EQ)), case_number, 1, mark, True, Exception) # This should raise an error.
    case_number = case_number + 1

    # ===== CASE 5: Column name is not a string. =====

    print("CASE {}: Column name is not a string.".format(case_number))
    (mark, result) = asst3.run_test_case(db.scan, ("User", (3, easydb.OP_EQ, 27)), case_number, 1, mark, True, Exception) # This should raise an error.
    case_number = case_number + 1

    # ===== CASE 6: Column name does not exist. =====

    print("CASE {}: Column name does not exist.".format(case_number))
    (mark, result) = asst3.run_test_case(db.scan, ("User", ("bob", easydb.OP_EQ, 27)), case_number, 1, mark, True, ValueError) # This should raise an ValueError error.
    case_number = case_number + 1

    # ===== CASE 7: Operator is not supported. =====

    print("CASE {}: Operator is not supported.")    
    (mark, result) = asst3.run_test_case(db.scan, ("User", ("age", 10, 27)), case_number, 1, mark, True, ValueError) # This should raise an ValueError error.
    case_number = case_number + 1

    # ===== CASE 8: Type of operand does not match. =====

    print("CASE {}: Type of operand does not match.".format(case_number))
    (mark, result) = asst3.run_test_case(db.scan, ("User", ("age", easydb.OP_EQ, "27")), case_number, 1, mark, True, ValueError) # This should raise an ValueError error.
    case_number = case_number + 1

    # ===== CASE 9: Operator of a foreign key operand is not OP_EQ or OP_NE. =====

    print("CASE {}: Operator of a foreign key column is not OP_EQ or OP_NE.".format(case_number))
    (mark, result) = asst3.run_test_case(db.scan, ("Account", ("user", easydb.OP_GT, 10)), case_number, 1, mark, True, ValueError) # This should raise an ValueError error.
    case_number = case_number + 1

    # ===== CASE 10: Operand of a foreign key column is not an integer. =====   

    print("CASE {}: Operand of a foreign key column is not an integer.".format(case_number))
    (mark, result) = asst3.run_test_case(db.scan, ("Account", ("user", easydb.OP_EQ, "Bob")), case_number, 1, mark, True, ValueError) # This should raise an ValueError error.
    case_number = case_number + 1

    # ===== CASE 11: Everything is ok with equal operator. =====

    print("CASE {}: Everything is ok with equal operator.".format(case_number))

    # This should not raise any error.
    try:
        IDs = db.scan("User", ("firstName", easydb.OP_EQ, "James"))
    except Exception as e:
        print("CASE {} FAIL: {}".format(case_number, str(e)))
    else:
        if [1] == IDs:
            print("CASE {} PASS".format(case_number))
            mark = mark + 1
        else:
            print("CASE {} FAIL: the scan result is not correct".format(case_number))

    case_number = case_number + 1

    # ===== CASE 12: Everything is ok with not equal operator. =====

    print("CASE {}: Everything is ok with not equal operator.".format(case_number))

    # This should not raise any error.
    try:
        IDs = db.scan("User", ("firstName", easydb.OP_NE, "James"))
    except Exception as e:
        print("CASE {} FAIL: {}".format(case_number, str(e)))
    else:
        if IDs is not None and all(ID in IDs for ID in [2, 3]) and len(IDs) == 2:
            print("CASE {} PASS".format(case_number))
            mark = mark + 1
        else:
            print("CASE {} FAIL: the scan result is not correct".format(case_number))

    case_number = case_number + 1

    # ===== CASE 13: Everything is ok with less than operator. =====

    print("CASE {}: Everything is ok with less than operator.".format(case_number))

    # This should not raise any error.
    try:
        IDs = db.scan("User", ("age", easydb.OP_LT, 100))
    except Exception as e:
        print("CASE {} FAIL: {}".format(case_number, str(e)))
    else:
        if IDs is not None and all(ID in IDs for ID in [1, 2, 3]) and len(IDs) == 3:
            print("CASE {} PASS".format(case_number))
            mark = mark + 1
        else:
            print("CASE {} FAIL: the scan result is not correct".format(case_number))

    case_number = case_number + 1

    # ===== CASE 14: Everything is ok with greater than operator. =====

    print("CASE {}: Everything is ok with greater than operator.".format(case_number))

    # This should not raise any error.
    try:
        IDs = db.scan("User", ("height", easydb.OP_GT, 190.0))
    except Exception as e:
        db.close()
        print("CASE {} FAIL: {}".format(case_number, str(e)))
    else:
        db.close()
        if IDs is not None and len(IDs) == 0:
            line = 'Request { table_id: 1, command: Query(3, 4, Float(190.0)) }'
            if server.expect(line) is not None:
                print("CASE {} PASS".format(case_number))
                mark = mark + 1
            else:
                print("CASE {} FAIL: server did not receive the Scan command".format(case_number))
        else:
            print("CASE {} FAIL: the scan result is not correct".format(case_number))
            
    server.end()
    
    test.add_mark(mark)
    
if __name__ == '__main__':
    main()

