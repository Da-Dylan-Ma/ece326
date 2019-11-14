#!/usr/bin/python3
#
# orm delete command test for assignment 3
# Assume student's db constructor, connect, and close are working.
# Assume student's orm basic functionality (orm basic test) is working.
#

import asst3
import socket
import tester
import importlib

asst3_schema = asst3.load_module('asst3_schema')

TOTAL_MARK = 2

def main():
	# Set up the tester.
	test = asst3.start_test('orm delete command test', TOTAL_MARK)

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
	james = asst3_schema.User(db, firstName="James", lastName="Hartley", height=180.3, age=38)
	james.pk = 1
	james.version = 1

	# ===== CASE 1: Delete a row object with no error. =====

	print("CASE {}: Delete a row object with no error.".format(case_number))

	# This should not raise any error.
	try:
		james.delete()
	except Exception as e:
		print("CASE {} FAIL: {}".format(case_number, str(e)))
	else:
		db.close()

		# Dump database rows.
		rows = asst3.dump(server, 1)

		not_deleted = False

		for row in rows:
			if row[0] == "1":
				not_deleted = True
				break

		if not_deleted:
			print("CASE {} FAIL: the deleted row is still on the server".format(case_number))
		else:	
			print("CASE {} PASS".format(case_number))
			mark = mark + 1

		db.connect(server.host, server.port)

	case_number = case_number + 1

	# ===== CASE 2: Delete a row object whose pk is None. =====

	print("CASE {}: Delete a row object whose pk is None.".format(case_number))
	(mark, result) = asst3.run_test_case(james.delete, (), case_number, 1, mark, True, orm.exceptions.PacketError, True) # This should raise an error other than PacketError.
	
	db.close()

	server.end()

	test.add_mark(mark)

if __name__ == '__main__':
    main()
