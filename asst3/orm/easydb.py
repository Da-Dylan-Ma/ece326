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

    def __init__(self, tables):
        """ Constructor
            tables -- all the tables (and their structures) in the database
        """
        db_tables = {}
        for table_name, cols in tables:
            if type(table_name) is not str:
                raise TypeError("Table name `{}` is not of type str".format(table_name))

            table = {}
            for col_name, col_type in cols:
                if type(col_name) is not str:
                    raise TypeError("Column name `{}` is not of type str".format(col_name))
                if col_name in ("id", "pk"):
                    raise ValueError("Column name `{}` is not allowed".format(col_name))
                if col_type in (str, float, int):
                    table[col_name] = col_type
                elif type(col_type) is str:
                    if col_type in db_tables:
                        table[col_name] = col_type
                    else:
                        raise IntegrityError("Foreign key reference `{}` does not exist".format(col_type))
                else:
                    raise ValueError("Column type `{}` is not allowed".format(col_type))
            db_tables[table_name] = table # commit to table after

        self.tables = db_tables

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
