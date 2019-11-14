#!/usr/bin/python3
#
# orm count command test for assignment 3
# Assume student's db constructor, connect, and close are working.
# Assume student's orm basic functionality (orm basic test) is working.
#

import asst3
import socket
import tester
import importlib

asst3_schema = asst3.load_module('asst3_schema')

TOTAL_MARK = 4

def main():
	# Set up the tester.
	test = asst3.start_test('orm count command test', TOTAL_MARK)

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

	# ===== CASE 1: Count with no argument with no error. =====

	print("CASE {}: Count with no argument with no error.".format(case_number))

	# This should not raise any error.
	try:
		result = asst3_schema.Account.count(db)

		if result == 4:
			print("CASE {} PASS".format(case_number))
			mark = mark + 1
		else:
			print("CASE {} FAIL: count result is not correct".format(case_number))
	except Exception as e:
		print("CASE {} FAIL: {}".format(case_number, str(e)))

	case_number = case_number + 1

	# ===== CASE 2: Count with an argument with no error. =====

	print("CASE {}: Count with an argument with no error.".format(case_number))

	# This should not raise any error.
	try:
		result = asst3_schema.Account.count(db, balance__gt=89.1)

		if result == 2:
			print("CASE {} PASS".format(case_number))
			mark = mark + 1
		else:
			print("CASE {} FAIL: count result is not correct".format(case_number))
	except Exception as e:
		print("CASE {} FAIL: {}".format(case_number, str(e)))

	case_number = case_number + 1

	# ==== CASE 3: Count with an existing pk. =====

	print("CASE {}: Count with pk.".format(case_number))

	# This should not raise any error.
	try:
		result = asst3_schema.Account.count(db, pk=3)

		if result == 1:
			print("CASE {} PASS".format(case_number))
			mark = mark + 1
		else:
			print("CASE {} FAIL: count result is not correct".format(case_number))
	except Exception as e:
		print("CASE {} FAIL: {}".format(case_number, str(e)))

	case_number = case_number + 1

	# ==== CASE 4: Count with an non-existing pk. =====

	print("CASE {}: Count with pk.".format(case_number))

	# This should not raise any error.
	try:
		result = asst3_schema.Account.count(db, pk=100)

		if result == 0:
			print("CASE {} PASS".format(case_number))
			mark = mark + 1
		else:
			print("CASE {} FAIL: count result is not correct".format(case_number))
	except Exception as e:
		print("CASE {} FAIL: {}".format(case_number, str(e)))

	db.close()

	server.end()

	test.add_mark(mark)

if __name__ == '__main__':
    main()

