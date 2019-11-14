#!/usr/bin/python3
#
# orm custom types (Datetime and Coordinate) test for assignment 3
# Assume student's db constructor, connect, and close are working.
# Assume student's all orm functionalities (basic operations and functions) are working.
#

import asst3
import tester
import os
from datetime import datetime

asst3_schema = asst3.load_module('asst3_schema2')

TOTAL_MARK = 14

STUDENT_FILE = "student_export.txt"

def main():
    # Set up the tester.
    test = asst3.start_test('orm custom types (Datetime and Coordinate) test', TOTAL_MARK)

    # Import student's code.
    import orm 

    mark = 0
    case_number = 1

    output = orm.export("easydb", asst3_schema) 
    with open(STUDENT_FILE, "wt") as f:
        f.write(output)

    # Start the server.
    server = asst3.Server(filename="student_export.txt")
    if not server.start("preload.txt"):
        print("ERROR: server could not start.\n" \
            "HINT: Check the correctness of the exported schema file")
        os.remove(STUDENT_FILE)
        return

    # Set up student's database object and connect to the database.
    db = orm.setup("easydb", asst3_schema)
    asst3.try_connect(db, server)

    # ===== CASE 1: Create a row object with Coordinate field with no error. =====

    print("CASE {}: Create a row object with Coordinate field with no error.".format(case_number))

    # This should not raise any error.
    try:
        toronto = asst3_schema.City(db, name="Toronto", location=(12.3, 12.3))

        if toronto.location == (12.3, 12.3):
            print("CASE {} PASS".format(case_number))
            mark = mark + 1
        else:
            print("CASE {} FAIL: the field is not set properly".format(case_number))
    except Exception as e:
        print("CASE {} FAIL: {}".format(case_number, str(e)))

    case_number = case_number + 1

    # ===== CASE 2: Create a row object with Coordinate field whose blank is set to True. =====

    print("CASE {}: Create a row object with Coordinate field whose blank is set to True.".format(case_number))

    # This should not raise any error.
    try:
        toronto = asst3_schema.City(db, name="Toronto")

        if toronto.location == (0.0, 0.0):
            print("CASE {} PASS".format(case_number))
            mark = mark + 1
        else:
            print("CASE {} FAIL: the filed is not set properly".format(case_number))
    except Exception as e:
        print("CASE {} FAIL: {}".format(case_number, str(e)))

    case_number = case_number + 1

    # ===== CASE 3: Assign the Coordinate field with wrong type. =====

    print("CASE {}: Assign the Coordinate field with wrong type.".format(case_number))

    # This should raise an TypeError or ValueError error.
    try:
        toronto.location = 3
    except TypeError:
        print("CASE {} PASS".format(case_number))
        mark = mark + 1
    except ValueError:
        print("CASE {} PASS".format(case_number))
        mark = mark + 1
    else:
        print("CASE {} FAIL: {}".format(case_number, "expected TypeError or ValueError"))

    case_number = case_number + 1

    # ===== CASE 4: Assign and save the row object with Coordinate field with invalid value. =====

    print("CASE {}: Assign and save the row object with Coordinate field with invalid value.".format(case_number))

    # This should raise a ValueError error.
    try:
        toronto.location = (200.2, 500.3)
        toronto.save()
    except ValueError:
        print("CASE {} PASS".format(case_number))
        mark = mark + 1
    except Exception as e:
        print("CASE {} FAIL: {}".format(case_number, str(e)))
    else:
        print("CASE {} FAIL: {}".format(case_number, "expected ValueError"))

    case_number = case_number + 1

    # ===== CASE 5: Save and get the row object with Coordinate field with no error. =====

    print("CASE {}: Save and get the row object with Coordinate field with no error.".format(case_number))

    # This should not raise any error.
    try:
        toronto.location = (43.74, -79.37)
        toronto.save()
    except Exception as e:
        print("CASE {} FAIL: {}".format(case_number))
    else:
        try:
            city1 = asst3_schema.City.get(db, 1)

            if city1.location == (43.74, -79.37):
                print("CASE {} PASS".format(case_number))
                mark = mark + 1
            else:
                print("CASE {} FAIL: the saved and received field do not match".format(case_number))
        except Exception as e:
            print("CASE {} FAIL: {}".format(case_number, str(e)))

    case_number = case_number + 1

    # ===== CASE 6: Filter the row object with Coordinate field. =====

    print("CASE {}: Filter the row object with Coordinate field.".format(case_number))

    # This should not raise any error.
    try:
        not_toronto_A = asst3_schema.City(db, name="NotTorontoA", location=(43.74, 12.3))
        not_toronto_B = asst3_schema.City(db, name="NotTorontoB", location=(12.3, -79.37))
        not_toronto_A.save()
        not_toronto_B.save()

        results1 = asst3_schema.City.filter(db, location=(43.74, -79.37))
        results2 = asst3_schema.City.filter(db, location__ne=(43.74, -79.37))

        # equal case
        if results1[0].name == "Toronto" and len(results1) == 1:

            # not equal case
            if results2[0].name in ["NotTorontoA", "NotTorontoB"] and results2[1].name in ["NotTorontoA", "NotTorontoB"] and len(results2) == 2: 
                print("CASE {} PASS".format(case_number))
                mark = mark + 1
            else:
                print("CASE {} FAIL: the filter result (not equal case) is not correct".format(case_number))
        
        else:
            print("CASE {} FAIL: the filter result (equal case) is not correct".format(case_number))
    except Exception as e:
        print("CASE {} FAIL: {}".format(case_number, str(e)))

    case_number = case_number + 1

    # ===== CASE 7: Create a row object with DateTime field with no error. =====

    print("CASE {}: Create a row object with Datetime field with no error.".format(case_number))

    # This should not raise any error.
    try:
        midterm = asst3_schema.Event(db, location=toronto, start=datetime(2019, 10, 29, 16, 0), end=datetime(2019, 10, 29, 17, 30))

        if midterm.start == datetime(2019, 10, 29, 16, 0) and midterm.end == datetime(2019, 10, 29, 17, 30):
            print("CASE {} PASS".format(case_number))
            mark = mark + 1
        else:
            print("CASE {} FAIL: the field is not set properly".format(case_number))
    except Exception as e:
        print("CASE {} FAIL: {}".format(case_number, str(e)))

    case_number = case_number + 1

    # ===== CASE 8: Create a row object with DateTime field whose blank is set to True is set properly. =====

    print("CASE {}: Create a row object with DateTime field whose blank is set to True.".format(case_number))

    # This should not raise any error.
    try:
        due = asst3_schema.Event(db, location=toronto, start=datetime(2019, 11, 17, 23, 59))

        if due.end == datetime.fromtimestamp(0):
            print("CASE {} PASS".format(case_number))
            mark = mark + 1
        else:
            print("CASE {} FAIL: the field is not set properly".format(case_number))
    except Exception as e:
        print("CASE {} FAIL: {}".format(case_number, str(e)))

    case_number = case_number + 1

    # ===== CASE 9: Create a row object with DateTime field whose default is set properly (calling a function). =====

    print("CASE {}: Create a row object with DateTime field whose default is set properly (calling a function).".format(case_number))

    # This should not raise any error.
    try:
        event1 = asst3_schema.Event(db, location=toronto, end=datetime(2019, 11, 17, 12))

        if type(event1.start) is datetime:
            print("CASE {} PASS".format(case_number))
            mark = mark + 1
        else:
            print("CASE {} FAIL: the field is not set properly".format(case_number))
    except Exception as e:
        print("CASE {} FAIL: {}".format(case_number, str(e)))

    case_number = case_number + 1

    # ===== CASE 10: Assign the Datetime field with wrong type. =====

    print("CASE {}: Assign the Datetime field with wrong type.".format(case_number))

    # This should raise a TypeError error.
    try:
        event1.start = 3
    except TypeError:
        print("CASE {} PASS".format(case_number))
        mark = mark + 1
    except Exception as e:
        print("CASE {} FAIL: {}".format(case_number, str(e)))
    else:
        print("CASE {} FAIL: {}".format(case_number, "expected TypeError"))

    case_number = case_number + 1

    # ===== CASE 11: Assign the Datetime field with correct type. =====

    print("CASE {}: Assign the Datetime field with correct type.".format(case_number))

    # This should not raise any error.
    try:
        event1.start = datetime(2019, 9, 15, 12)
    
        if event1.start == datetime(2019, 9, 15, 12):
            print("CASE {} PASS".format(case_number))
            mark = mark + 1
        else:
            print("CASE {} FAIL: the field is not set properly".format(case_number))
    except Exception as e:
        print("CASE {} FAIL: {}".format(case_number, str(e)))
    
    case_number = case_number + 1
        
    # ===== CASE 12: Save and get the row object with Datetime field with no error. =====

    print("CASE {}: Save and get the row object with Datetime field with no error.".format(case_number))

    # This should not raise any error.
    try:
        event1.save()
    except Exception as e:
        print("CASE {} FAIL: {}".format(case_number, str(e)))
    else:
        # This should not raise any error.
        try:
            event2 = asst3_schema.Event.get(db, 1)

            if event2.start == datetime(2019, 9, 15, 12):
                print("CASE {} PASS".format(case_number))
                mark = mark + 1
            else:
                print("CASE {} FAIL: the saved and received field do not match".format(case_number))
        except Exception as e:
            print("CASE {} FAIL: {}".format(case_number, str(e)))

    case_number = case_number + 1

    # ===== CASE 13: Filter the row object with Datetime field. =====

    print("CASE {}: Filter the row object with Datetime field.".format(case_number))

    # This should not raise any error.
    try:
        results = asst3_schema.Event.filter(db, start=datetime(2019, 9, 15, 12))

        if (results[0].location.name == "Toronto") and (len(results) == 1):
            mark = mark + 1
            print("CASE {} PASS".format(case_number))
        else:
            print("CASE {} FAIL: filter result is not correct".format(case_number))
    except Exception as e:
        print("CASE {} FAIL: {}".format(case_number, str(e)))

    case_number = case_number + 1

    # ===== CASE 14: Count the row object with Datetime field. =====

    print("CASE {}: Count the row object with Datetime field.".format(case_number))

    # This should not raise any error.
    try:
        results = asst3_schema.Event.filter(db, start__gt=datetime(2019, 7, 15, 12))

        if (results[0].location.name == "Toronto") and (len(results) == 1):
            mark = mark + 1
            print("CASE {} PASS".format(case_number))
        else:
            print("CASE {} FAIL: count result is not correct".format(case_number))
    except Exception as e:
        print("CASE {} FAIL: {}".format(case_number, str(e)))

    test.add_mark(mark)
    db.close()
    server.end()
    os.remove(STUDENT_FILE)
    

if __name__ == '__main__':

    main()
