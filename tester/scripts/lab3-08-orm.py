#!/usr/bin/python3
#
# orm basic test for assignment 3
# Assume student's db constructor, connect, and close are working.
#

import asst3
import socket
import tester
import importlib

asst3_schema = asst3.load_module('asst3_schema')

TOTAL_MARK = 15

def main():
    # Set up the tester.
    test = asst3.start_test('orm basic test', TOTAL_MARK)

    # Import student's code.
    import orm
    import orm.exceptions

    mark = 0
    case_number = 1

    # ===== CASE 1: Default value is not the correct type. =====

    print("CASE {}: Default value is not the correct type.".format(case_number))

    # This should raise an TypeError error.
    try:
        asst3_schema_bad1 = asst3.load_module('asst3_schema_bad1')
        orm.setup("easydb", asst3_schema_bad1)
    except TypeError:
        print("CASE {} PASS".format(case_number))
        mark = mark + 1
    except Exception as e:
        print("CASE {} FAIL: {}".format(case_number, str(e)))
    else:
        print("CASE {} FAIL: {}".format(case_number, "expected TypeError"))

    case_number = case_number + 1

    # ===== CASE 2: Choices value is not the correct type. =====

    print("CASE {}: Choices value is not the correct type.".format(case_number))

    # This should raise an TypeError error.
    try:
        asst3_schema_bad2 = asst3.load_module('asst3_schema_bad2')
        orm.setup("easydb", asst3_schema_bad2)
    except TypeError:
        print("CASE {} PASS".format(case_number))
        mark = mark + 1
    except Exception as e:
        print("CASE {} FAIL: {}".format(case_number, str(e)))
    else:
        print("CASE {} FAIL: {}".format(case_number, "expected TypeError"))

    case_number = case_number + 1

    # ===== CASE 3: Field name contains underscore. =====

    print("CASE {}: Field name contains underscore.".format(case_number))

    # This should raise an AttributeError error.
    try:
        asst3_schema_bad3 = asst3.load_module('asst3_schema_bad3')
        orm.setup("easydb", asst3_schema_bad3)
    except AttributeError:
        print("CASE {} PASS".format(case_number))
        mark = mark + 1
    except Exception as e:
        print("CASE {} FAIL: {}".format(case_number, str(e)))
    else:
        print("CASE {} FAIL: {}".format(case_number, "expected AttributeError"))

    case_number = case_number + 1

    # ===== CASE 4: Field name use reserved word. =====

    print("CASE {}: Field name use reserved word.".format(case_number))

    # This should raise an AttributeError error.
    try:
        asst3_schema_bad4 = asst3.load_module('asst3_schema_bad4')
        orm.setup("easydb", asst3_schema_bad4)
    except AttributeError:
        print("CASE {} PASS".format(case_number))
        mark = mark + 1
    except Exception as e:
        print("CASE {} FAIL: {}".format(case_number, str(e)))
    else:
        print("CASE {} FAIL: {}".format(case_number, "expected AttributeError"))

    case_number = case_number + 1

    # ===== CASE 5: Setup with a correct schema =====

    print("CASE {}: Setup with a correct schema".format(case_number))

    # This should not raise any error.
    try:
        db = orm.setup("easydb", asst3_schema)
    except Exception as e:
        print("CASE {} FAIL: {}".format(case_number, str(e)))
    else:
        contain = False
        
        for key in db.__dict__:
            # Check if the object saves the inpputed schema by checking if there is a tuple, list, or dict attribute.
            if isinstance(db.__dict__[key], (tuple, list, dict)):
                if len(db.__dict__[key]) > 0:
                    contain = True
                    break

        if contain:
            print("CASE {} PASS".format(case_number))
            mark = mark + 1
        else:
            print("CASE {} FAIL: no tuple, list, or dict is found in the Database object indicating that the inputted schema is saved".format(case_number))

    case_number = case_number + 1

    #  ===== CASE 6: Create a row object with missing field. =====

    print("CASE {}: Create a row object with missing field.".format(case_number))

    # This should raise an AttributeError error.
    try:
        jeffrey = asst3_schema.User(db, firstName="Jeffrey", height=999.9)
    except AttributeError:
        print("CASE {} PASS".format(case_number))
        mark = mark + 1
    except Exception as e:
        print("CASE {} FAIL: {}".format(case_number, str(e)))
    else:
        print("CASE {} FAIL: {}".format(case_number, "expected AttributeError"))

    case_number = case_number + 1

    #  ===== CASE 7: Create a row object with no error. =====

    print("CASE {}: Create a row object with no error".format(case_number))

    # This should not raise any error.
    try:
        jeffrey = asst3_schema.User(db, firstName="Jeffrey", lastName="Fang", height=999.9)
    except Exception as e:
        print("CASE {} FAIL: {}".format(case_number, str(e)))
    else:
        try:
            if jeffrey.firstName == "Jeffrey":
                print("CASE {} PASS".format(case_number))
                mark = mark + 1
            else:
                print("CASE {} FAIL: the stored field of the row object is not correct".format(case_number))
        except Exception as e:
            print("CASE {} FAIL: while accessing the field of the row object: {}".format(case_number, str(e)))

    case_number = case_number + 1

    #  ===== CASE 8: Create object with a foreign key. =====

    print("CASE {}: Create object with a foreign key.".format(case_number))

    # This should not raise any error.
    try:
        account1 = asst3_schema.Account(db, user=jeffrey)
    except Exception as e:
        print("CASE {} FAIL: {}".format(case_number, str(e)))
    else:
        try:
            if account1.user.lastName == "Fang":
                print("CASE {} PASS".format(case_number))
                mark = mark + 1
            else:
                print("CASE {} FAIL: the field of stored foreign key field of the row object is not correct".format(case_number))
        except Exception as e:
            print("CASE {} FAIL: while accessing the field of the row object: {}".format(case_number, str(e)))

    case_number = case_number + 1

    # ==== CASE 9: Check if the field with blank set to True is set properly. =====

    print("CASE {}: Check if the field with blank set to True is set properly.".format(case_number))

    # This should not raise any error.
    try:
        if jeffrey.age == 0:
            print("CASE {} PASS".format(case_number))
            mark = mark + 1
        else:
            print("CASE {} FAIL: the field is not set properly".format(case_number))
    except Exception as e:
        print("CASE {} FAIL: while accessing the field of the row object: {}".format(case_number, str(e)))

    case_number = case_number + 1

    # ==== CASE 10: Check if the field with default is set properly. =====

    print("CASE {}: Check if the field with default is set properly.".format(case_number))

    # This should not raise any error.
    try:
        if account1.type == "Normal":
            print("CASE {} PASS".format(case_number))
            mark = mark + 1
        else:
            print("CASE {} FAIL: the field is not set properly".format(case_number))
    except Exception as e:
        print("CASE {} FAIL: while accessing the field of the row object: {}".format(case_number, str(e)))

    case_number = case_number + 1

    # ===== CASE 11: Set the field value to wrong type. =====

    print("CASE {}: Set the field value to wrong type.".format(case_number))

    # This should raise a TypeError error.
    try:
        jeffrey.age = 3.5
    except TypeError:
        print("CASE {} PASS".format(case_number))
        mark = mark + 1
    except Exception as e:
        print("CASE {} FAIL: {}".format(case_number, str(e)))
    else:
        print("CASE {} FAIL: {}".format(case_number, "expected TypeError"))

    case_number = case_number + 1

    # ===== CASE 12: Set a float field with int. =====

    print("CASE {}: Set a float field with int.".format(case_number))

    # This should not raise any error.
    try:
        jeffrey.height = 50
    except Exception as e:
        print("CASE {} FAIL: {}".format(case_number, str(e)))
    else:
        if isinstance(jeffrey.height, float) and (jeffrey.height == 50.0):
            print("CASE {} PASS".format(case_number))
            mark = mark + 1
        else:
            print("CASE {} FAIL: the field is not set properly (maybe field is not a float anymore?)".format(case_number))

    case_number = case_number + 1

    # ===== CASE 13: Set the field value whose blank is True to None. =====

    print("CASE {}: Set the field value whose blank is True to None.".format(case_number))

    # This should not raise any error.
    try:
        jeffrey.height = None
    except Exception as e:
        print("CASE {} FAIL: {}".format(case_number, str(e)))
    else:
        if jeffrey.height == 0.0:
            print("CASE {} PASS".format(case_number))
            mark = mark + 1
        else:
            print("CASE {} FAIL: the field is not set properly (should set to default value of the type)".format(case_number))

    case_number = case_number + 1
        
    # ===== CASE 14: Set the field value whose blank is False to None. =====

    print("CASE {}: Set the field value whose blank is False to None.".format(case_number))

    # This should raise an error.
    try:
        jeffrey.firstName = None
    except:
        print("CASE {} PASS".format(case_number))
        mark = mark + 1
    else:
        print("CASE {} FAIL: {}".format(case_number, "expected an error"))

    case_number = case_number + 1

    # ===== CASE 15: Export =====

    print("CASE {}: Export".format(case_number))

    # This should not raise any error.
    try:
        output = orm.export("easydb", asst3_schema)
    except Exception as e:
        print("CASE {} FAIL: {}".format(case_number, str(e)))
    else:
        # Read the solution.
        with open(tester.datapath('export.txt', 'asst3'), 'r') as file:
            data = file.read()

        # Check if the format is correct.
        if output == data:
            print("CASE {} PASS".format(case_number))
            mark = mark + 1
        else:
            print("CASE {} FAIL: the format is not correct".format(case_number))

    test.add_mark(mark)

if __name__ == '__main__':
    main()

