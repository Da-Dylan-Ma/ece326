#!/usr/bin/python3
#
# orm get command test for assignment 3
# Assume student's db constructor, connect, and close are working.
# Assume student's orm basic functionality (orm basic test) is working.
#

import asst3
import socket
import tester
import random
import importlib

asst3_schema = asst3.load_module('asst3_schema')

TOTAL_MARK = 3

def main():
	# Set up the tester.
	test = asst3.start_test('orm get command test', TOTAL_MARK)

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

	# ===== CASE 1: Get id which does not exist. =====

	print("CASE {}: Get id which does not exist.".format(case_number).format(case_number))
	(mark, result) = asst3.run_test_case(asst3_schema.User.get, (db, 777), case_number, 1, mark, True, orm.exceptions.ObjectDoesNotExist) # This should raise an ObjectDoesNotExist error.
	case_number = case_number + 1

	# ===== CASE 2: Get a row object with no error. =====

	id_number = random.randint(1, 3)

	if id_number == 1:
		age = 38
	elif id_number == 2:
		age = 48
	else:
		age = 21

	print("CASE {}: Get a row object with no error.".format(case_number))

	# This should not raise any error.
	try:
		user1 = asst3_schema.User.get(db, id_number)

		if user1.age == age:
			print("CASE {} PASS".format(case_number))
			mark = mark + 1
		else:
			print("CASE {} FAIL: the field value of the row object is not correct".format(case_number))
	except Exception as e:
		print("CASE {} FAIL: {}".format(case_number, str(e)))

	case_number = case_number + 1

	# ===== CASE 3: Get a row object which has foreign key field with no error. =====

	id_number = random.randint(1, 4)

	if id_number == 1:
		firstName = "James"
	else:
		firstName = "Alice"

	print("CASE {}: Get a row object which has foreign key field with no error.".format(case_number))

	# This should not raise any error.
	try:
		account1 = asst3_schema.Account.get(db, id_number)

		if (account1.type == "Normal") and (account1.user.firstName == firstName):
			print("CASE {} PASS".format(case_number))
			mark = mark + 1
		else:
			print("CASE {} FAIL: the field value of the row object is not correct".format(case_number))
	except Exception as e:
		print("CASE 2 FAIL: {}".format(case_number, str(e)))
		
	db.close()

	server.end()

	test.add_mark(mark)

if __name__ == '__main__':
    main()

