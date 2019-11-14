#!/usr/bin/python3
#
# easydb table format test for assignment 3
#

import asst3 

TOTAL_MARK = 16

def main():
	# Set up the tester.
	test = asst3.start_test('easydb table format test', TOTAL_MARK)
	
	# Load student's code.
	from orm import easydb, exceptions
	
	mark = 0
	case_number = 1

	# ===== CASE 1: All the table formats are ok. =====

	tb_1 = (
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

	print("CASE {}: All the table formats are ok.".format(case_number))

	# This should not raise any error.
	try:
		db = easydb.Database(tb_1)
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
	
	# ===== CASE 2: Table name is not a string. =====

	tb_2 = (
		("User", ( # table_name
			("firstName", str), # (column_name, type)
			("lastName", str),
			("height", float),
			("age", int),
		)),
	    
		(33333, (
			("user", "User"), # (column_name, table_reference)
			("type", str),
			("balance", float),
		))
	)

	print("CASE {}: Table name is not a string.".format(case_number))
	(mark, result) = asst3.run_test_case(easydb.Database, (tb_2,), case_number, 1, mark, True, TypeError) # This should raise a TypeError error.
	case_number = case_number + 1

	# ===== CASE 3: Column name is not a string. =====

	tb_3 = (
		("User", ( # table_name
			("firstName", str), # (column_name, type)
			("lastName", str),
			([1, 2], float),
			("age", int),
		)),
	    
		("Account", (
			("user", "User"), # (column_name, table_reference)
			("type", str),
			("balance", float),
		))
	)

	print("CASE {}: Column name is not a string.".format(case_number))
	(mark, result) = asst3.run_test_case(easydb.Database, (tb_3,), case_number, 1, mark, True, TypeError) # This should raise a TypeError error.
	case_number = case_number + 1

	# ===== CASE 4: Type is not one of str, float, int. =====

	tb_4 = (
		("User", ( # table_name
			("firstName", str), # (column_name, type)
			("lastName", str),
			("height", float),
			("age", tuple),
		)),
	    
		("Account", (
			("user", "User"), # (column_name, table_reference)
			("type", str),
			("balance", float),
		))
	)

	print("CASE {}: Type is not one of str, float, int.".format(case_number))
	(mark, result) = asst3.run_test_case(easydb.Database, (tb_4,), case_number, 1, mark, True, ValueError) # This should raise a ValueError error.
	case_number = case_number + 1

	# ===== CASE 5: Type is not a string referencing another table name (nonexistent table). =====

	tb_5 = (
		("User", ( # table_name
			("firstName", str), # (column_name, type)
			("lastName", str),
			("height", float),
			("age", int),
		)),
	    
		("Account", (
			("user", "Yes"), # (column_name, table_reference)
			("type", str),
			("balance", float),
		))
	)

	print("CASE {}: Type is not a string referencing another table name (nonexistent table).".format(case_number))
	(mark, result) = asst3.run_test_case(easydb.Database, (tb_5,), case_number, 1, mark, True, exceptions.IntegrityError) # This should raise a IntegrityError error.
	case_number = case_number + 1

	# ===== CASE 6: Length of tables are not exactly 2. =====

	tb_6 = (
		("User", ( # table_name
			("firstName", str), # (column_name, type)
			("lastName", str),
			("height", float),
			("age", int),
		), 3),
	    
		("Account", (
			("user", "User"), # (column_name, table_reference)
			("type", str),
			("balance", float),
		))
	)

	print("CASE {}: Length of tables are not exactly 2.".format(case_number))
	(mark, result) = asst3.run_test_case(easydb.Database, (tb_6,), case_number, 1, mark, True, Exception) # This should raise an error.
	case_number = case_number + 1

	# ===== CASE 7: Length of columns are not exactly 2. =====
	
	tb_7 = (
		("User", ( # table_name
			("firstName", str), # (column_name, type)
			("lastName", str),
			("height", float),
			("age", int),
		)),
	    
		("Account", (
			("user", "User"), # (column_name, table_reference)
			("type", str, 123, "nonono"),
			("balance", float),
		))
	)

	print("CASE {}: Length of columns are not exactly 2.".format(case_number))
	(mark, result) = asst3.run_test_case(easydb.Database, (tb_7,), case_number, 1, mark, True, Exception) # This should raise an error.
	case_number = case_number + 1

	# ===== CASE 8: Names of tables are not legal. =====

	tb_8 = (
		("_User", ( # table_name
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

	print("CASE {}: Names of tables are not legal.".format(case_number))
	(mark, result) = asst3.run_test_case(easydb.Database, (tb_8,), case_number, 1, mark, True, Exception) # This should raise an error.
	case_number = case_number + 1

	# ===== CASE 9: Names of columns are not legal. =====

	tb_9 = (
		("User", ( # table_name
			("firstName", str), # (column_name, type)
			("lastName", str),
			("3height", float),
			("age", int),
		)),
	    
		("Account", (
			("user", "User"), # (column_name, table_reference)
			("type", str),
			("balance", float),
		))
	)

	print("CASE {}: Names of columns are not legal.".format(case_number))
	(mark, result) = asst3.run_test_case(easydb.Database, (tb_9,), case_number, 1, mark, True, Exception) # This should raise an error.
	case_number = case_number + 1

	# ===== CASE 10: Table names are duplicated. =====

	tb_10 = (
		("User", ( # table_name
			("firstName", str), # (column_name, type)
			("lastName", str),
			("height", float),
			("age", int),
		)),
	    
		("User", (
			("user", str), # (column_name, table_reference)
			("type", str),
			("balance", float),
		))
	)

	print("CASE {}: Table names are duplicated.".format(case_number))
	(mark, result) = asst3.run_test_case(easydb.Database, (tb_10,), case_number, 1, mark, True, Exception) # This should raise an error.
	case_number = case_number + 1

	# ===== CASE 11: Column names are duplicated. =====

	tb_11 = (
		("User", ( # table_name
			("firstName", str), # (column_name, type)
			("lastName", str),
			("weight", float),
			("firstName", int),
		)),
	    
		("Account", (
			("user", str), # (column_name, table_reference)
			("type", str),
			("balance", float),
		))
	)

	print("CASE {}: Column names are duplicated.".format(case_number))
	(mark, result) = asst3.run_test_case(easydb.Database, (tb_11,), case_number, 1, mark, True, Exception) # This should raise an error.
	case_number = case_number + 1

	# ===== CASE 12: Column name is 'pk'. =====

	tb_12 = (
		("User", ( # table_name
			("firstName", str), # (column_name, type)
			("lastName", str),
			("weight", float),
			("pk", int),
		)),
	    
		("Account", (
			("user", str), # (column_name, table_reference)
			("type", str),
			("balance", float),
		))
	)

	print("CASE {}: Column name is 'pk'.".format(case_number))
	(mark, result) = asst3.run_test_case(easydb.Database, (tb_12,), case_number, 1, mark, True, Exception) # This should raise an error.
	case_number = case_number + 1

	# ===== CASE 13: Column name is 'id'. =====

	tb_13 = (
		("User", ( # table_name
			("firstName", str), # (column_name, type)
			("lastName", str),
			("weight", float),
			("age", int),
		)),
	    
		("Account", (
			("user", str), # (column_name, table_reference)
			("id", str),
			("balance", float),
		))
	)

	print("CASE {}: Column name is 'id'.".format(case_number))
	(mark, result) = asst3.run_test_case(easydb.Database, (tb_13,), case_number, 1, mark, True, Exception) # This should raise an error.
	case_number = case_number + 1

	# ===== CASE 14: Column name is 'save'. =====

	tb_14 = (
		("User", ( # table_name
			("firstName", str), # (column_name, type)
			("lastName", str),
			("weight", float),
			("age", int),
		)),
	    
		("Account", (
			("user", str), # (column_name, table_reference)
			("save", str),
			("balance", float),
		))
	)

	print("CASE {}: Column name is 'save'.".format(case_number))
	(mark, result) = asst3.run_test_case(easydb.Database, (tb_14,), case_number, 1, mark, True, Exception) # This should raise an error.
	case_number = case_number + 1
	
	# ===== CASE 15: Foreign keys are causing a cycle. =====

	tb_15 = (
		("User", ( # table_name
			("firstName", str), # (column_name, type)
			("lastName", str),
			("height", float),
			("age", int),
		)),
	    
		("Account", (
			("user", "Account"), # (column_name, table_reference)
			("type", str),
			("balance", float),
		)),

		("Test1", (
			("user", "Account"), # (column_name, table_reference)
			("type", str),
			("balance", float),
		)),

		("Test2", (
			("user", "Test1"), # (column_name, table_reference)
			("type", str),
			("balance", float),
		))
	)

	print("CASE {}: Foreign keys are causing a cycle.".format(case_number))
	(mark, result) = asst3.run_test_case(easydb.Database, (tb_15,), case_number, 1, mark, True, exceptions.IntegrityError) # This should raise an IntegrityError error.
	case_number = case_number + 1

	# ===== CASE 16: Table reference is out of order. =====

	tb_16 = (
		("Account", ( # table_name
			("user", "User"), # (column_name, table_reference)
			("type", str),
			("balance", float),
		)),

		("User", ( 
			("firstName", str), # (column_name, type)
			("lastName", str),
			("height", float),
			("age", int),
		))
	)

	print("CASE {}: Table reference is out of order.".format(case_number))
	(mark, result) = asst3.run_test_case(easydb.Database, (tb_16,), case_number, 1, mark, True, exceptions.IntegrityError) # This should raise an IntegrityError error.

	test.add_mark(mark)

if __name__ == '__main__':
    main()
    
