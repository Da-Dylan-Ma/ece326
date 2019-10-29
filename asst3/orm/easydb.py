#!/usr/bin/python3
#
# easydb.py
#
# Definition for the Database class for EasyDB
#

########################################
##  HACK TO RUN SCRIPT IN PKG : BEGIN ##
########################################
# Required to run module from within package directory itself, by obtaining
# reference to `orm` package using cd, then pipelining output using temp stdout
# Harmless if not deleted: only footprint is `import sys`
# Note that the unit tests for the other modules will be printed as well
if __name__ == "__main__":
    import subprocess, pathlib, sys, os
    cwd = pathlib.Path.cwd()
    if cwd.stem == "orm": # currently still in package directory
        module_name = pathlib.Path(__file__).resolve().stem
        temp_stdout = "{}.out".format(module_name)
        with open(temp_stdout, "w") as outfile:
            cmd = "python -m orm.{}".format(module_name)
            subprocess.call(cmd.split(), cwd=cwd.parent, stdout=outfile)
        with open(temp_stdout, "r") as infile: print(infile.read(), end="")
        os.remove(temp_stdout)
    quit() # gracefully terminate thread
#######################################
##  HACK TO RUN SCRIPT IN PKG : END  ##
#######################################


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
        self.tables = {}
        for table_name, columns in tables:
            if type(table_name) is not str:
                raise TypeError("")
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



########################################
##  HACK TO RUN SCRIPT IN PKG : BEGIN ##
########################################
# Any unit testing code goes here
# Note that the unit tests for the other modules will be printed as well
import sys
if len(sys.argv) == 1 and sys.argv[0] == "-m":
    pass
    #print("\n{}\nTest: easydb.py\n".format("-"*30))
    #print("No unit tests written")
#######################################
##  HACK TO RUN SCRIPT IN PKG : END  ##
#######################################
