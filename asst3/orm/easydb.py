#!/usr/bin/python3
#
# easydb.py
#
# Definition for the Database class for EasyDB
#

import socket
import struct
from orm.exceptions import *

# EasyDB query operators
OP_EQ = 1  # equal
OP_NE = 2  # not equal
OP_LT = 3  # less than
OP_GT = 4  # greater than
OP_LE = 5  # (optional): less than or equal
OP_GE = 6  # (optional): greater than or equal

# EasyDB database implementation
class Database:

    def __repr__(self):
        return "<EasyDB Database object>"

    # constructor
    #   tables: all the tables (and their structures) in the databse.
    def __init__(self, tables):
        # Implement me.
        pass

    # Connect to the database.
    #   host: str, host name
    #   port: int, port number.
    def connect(self, host, port):
        # Implement me.
        pass

    # Close the connection to the database.
    def close(self):
        # Implement me.
        pass

    # Make the database to add a new row to a database table.
    #   table_name: str, name of the table
    #   values: sequence, the new row to insert to the table
    def insert(self, table_name, values):
        # Implement me.
        pass

    # Make the database to update an existing row in a table.
    #   table_name: str, name of the table
    #   pk: int, row ID
    #   values: sequence, the new row to update to the table
    #   version: int, version of the row
    def update(self, table_name, pk, values, version=None):
        # Implement me.
        pass
    
    # Make the database to delete a row in table.
    #   table_name: str, name of the table
    #   pk: int, row ID
    def drop(self, table_name, pk):
        # Implement me.
        pass

    # Make the database to retrieve a row from a table, which requires 
    # specifying the id of the row.
    #   table_name: str, name of the table
    #   pk: int, row ID
    def get(self, table_name, pk):
        # Implement me.
        pass

    # Make the database to compare a column of every row in a table against 
    # a value and returns the id of all rows that matched.
    #   table_name: str, name of the table
    #   query: tuple, a tuple of 3 elements: name of column, the operator, 
    #          and the right operand, respectively
    def scan(self, table_name, query):
        # Implement me.
        pass

