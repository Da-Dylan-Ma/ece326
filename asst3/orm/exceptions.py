#!/usr/bin/python3
#
# exceptions.py
#
# Definitions for all the errors in EasyORM and EasyDB
#

# customized exception for a foreign key error (e.g. cycle) in database schema 
class IntegrityError(Exception):
	pass

# customized exception for foreign key not found in the database (BAD_FOREIGN)
class InvalidReference(Exception):
	pass

# customized exception for the error code NOT_FOUND (id not found)
class ObjectDoesNotExist(Exception):   
    pass

# customized exception for the error code TXN_ABORT (update aborted)	
class TransactionAbort(Exception):	
	pass

# customized exception for the error code BAD_TABLE, BAD_QUERY, BAD_VALUE, BAD_ROW, and BAD_REQUEST.
class PacketError(Exception):
	pass

