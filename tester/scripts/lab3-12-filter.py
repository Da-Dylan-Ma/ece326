#!/usr/bin/python3
#
# orm filter command test for assignment 3
# Assume student's db constructor, connect, and close are working.
# Assume student's orm basic functionality (orm basic test) is working.
#

import asst3
import socket
import tester
import importlib

asst3_schema = asst3.load_module('asst3_schema')

TOTAL_MARK = 8

def main():
	# Set up the tester.
	test = asst3.start_test('orm filter command test', TOTAL_MARK)

	# Import student's code.
	import orm 

	mark = 0
	case_number = 1

	# Start the server.
	server = asst3.Server()
	server.start("preload.txt")

	# Set up student's database object and connect to the database.
	db = orm.setup("easydb", asst3_schema)
	asst3.try_connect(db, server)

	# Create a row object for testing.
	charlie = asst3_schema.User(db, firstName="Charlie", lastName="George", height=180.3, age=26)
	alice = asst3_schema.User(db, firstName="Alice", lastName="Harris", height=163.2, age=21)
	alice.pk = 3
	alice.version = 1

	# ===== CASE 1: Filter with no argument with no error. =====

	print("CASE {}: Filter with no argument with no error.".format(case_number))

	# This should not raise any error.
	try:
		results = asst3_schema.User.filter(db)

		if len(results) == 3 and results[0].age in [38, 48, 21]:
			print("CASE {} PASS".format(case_number))
			mark = mark + 1
		else:
			print("CASE {} FAIL: filter result is not correct".format(case_number))
	except Exception as e:
		print("CASE {} FAIL {}".format(case_number, str(e)))

	case_number = case_number + 1

	# ===== CASE 2: Filter with equal operator with no error. =====

	print("CASE {}: Filter with equal operator with no error.".format(case_number))

	# This should not raise any error.
	try:
		results = asst3_schema.User.filter(db, age=21)

		if (results[0].height == 163.2) and (len(results) == 1):
			print("CASE {} PASS".format(case_number))
			mark = mark + 1
		else:
			print("CASE {} FAIL: filter result is not correct".format(case_number))
	except Exception as e:
		print("CASE {} FAIL {}".format(case_number, str(e)))

	case_number = case_number + 1

	# ===== CASE 3: Filter with not eqaul operator with no error. =====

	print("CASE {}: Filter with not eqaul operator with no error.".format(case_number))

	# This should not raise any error.
	try:
		results = asst3_schema.Account.filter(db, balance__ne=89.1)

		if len(results) == 4 and results[0].type == "Normal":
			print("CASE {} PASS".format(case_number))
			mark = mark + 1
		else:
			print("CASE {} FAIL: filter result is not correct".format(case_number))
	except Exception as e:
		print("CASE {} FAIL {}".format(case_number, str(e)))
		
	case_number = case_number + 1

	# ===== CASE 4: Filter with greater than operator with no error. =====

	print("CASE {}: Filter with greater than operator with no error.".format(case_number))

	# This should not raise any error.
	try:
		results = asst3_schema.Account.filter(db, balance__gt=89.1)

		if len(results) == 2 and results[0].type == "Normal":
			print("CASE {} PASS".format(case_number))
			mark = mark + 1
		else:
			print("CASE {} FAIL: filter result is not correct".format(case_number))
	except Exception as e:
		print("CASE {} FAIL {}".format(case_number, str(e)))
		
	case_number = case_number + 1

	# ===== CASE 5: Filter with less than operator with no error. =====

	print("CASE {}: Filter with less than operator with no error.".format(case_number))

	# This should not raise any error.
	try:
		results = asst3_schema.Account.filter(db, balance__lt=210.3)

		if len(results) == 3 and results[0].type == "Normal":
			print("CASE {} PASS".format(case_number))
			mark = mark + 1
		else:
			print("CASE {} FAIL: filter result is not correct".format(case_number))
	except Exception as e:
		print("CASE {} FAIL: {}".format(case_number, str(e)))
		
	case_number = case_number + 1

	# ==== CASE 6: Filter with a foreign key object. =====

	print("CASE {}: Filter with a foreign key object.".format(case_number))

	# This should not raise any error.
	try:
		results = asst3_schema.Account.filter(db, user=alice)

		if len(results) == 3 and results[0].user.firstName == "Alice":
			print("CASE {} PASS".format(case_number))
			mark = mark + 1
		else:
			print("CASE {} FAIL: filter result is not correct".format(case_number))
	except Exception as e:
		print("CASE {} FAIL: {}".format(case_number, str(e)))

	case_number = case_number + 1

	# ==== CASE 7: Filter with a foreign key pk value. =====

	print("CASE {}: Filter with a foreign key pk value.".format(case_number))

	# This should not raise any error.
	try:
		results = asst3_schema.Account.filter(db, user=3)

		if len(results) == 3 and results[0].user.firstName == "Alice":
			print("CASE {} PASS".format(case_number))
			mark = mark + 1
		else:
			print("CASE {} FAIL: filter result is not correct".format(case_number))
	except Exception as e:
		print("CASE {} FAIL: {}".format(case_number, str(e)))

	case_number = case_number + 1

	# ===== CASE 8: Filter with a foreign key object whose pk is None. =====

	print("CASE {}: Filter with a foreign key object whose pk is None.".format(case_number))

	# This should raise an error.
	try:
		results = asst3_schema.Account.filter(db, user=charlie)
	except:
		print("CASE {} PASS".format(case_number))
		mark = mark + 1
	else:
		print("CASE {} FAIL: {}".format(case_number, "expected an error"))

	db.close()

	server.end()

	test.add_mark(mark)

if __name__ == '__main__':
    main()

