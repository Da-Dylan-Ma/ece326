#!/usr/bin/python3
#
# table.py
#
# Definition for an ORM database table and its metaclass
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


import orm.easydb
from collections import OrderedDict
from orm.exceptions import InvalidReference
from orm.fields import Integer, Float, String, Foreign, DateTime, Coordinate, datetime

# metaclass of table
# Implement me or change me. (e.g. use class decorator instead?)
class MetaTable(type):

    # Returns an existing object from the table, if it exists.
    #   db: database object, the database to get the object from
    #   pk: int, primary key (ID)
    def get(self, db, pk):
        # Implement me.
        pass

    # Returns a list of objects that matches the query. If no argument is given,
    # returns all objects in the table.
    # db: database object, the database to get the object from
    # kwarg: the query argument for comparing
    def filter(self, db, **kwarg):
        # Implement me.
        pass

    # Returns the number of matches given the query. If no argument is given,
    # return the number of rows in the table.
    # db: database object, the database to get the object from
    # kwarg: the query argument for comparing
    def count(self, db, **kwarg):
        # Implement me.
        pass

# table class
# Implement me.
class Table(object, metaclass=MetaTable):

    # constructor
    def __init__(self, db, **kwargs):
        # Implement me.

        self.pk = None # ID (primary key)
        self.version = None # version
        self.db = db # database object

    # Save the row by calling insert or update commands.
    # atomic: bool, True for atomic update or False for non-atomic update
    def save(self, atomic=True):
        # Implement me.
        pass

    # Delete the row from the database.
    def delete(self):
        # Implement me.
        pass



########################################
##  HACK TO RUN SCRIPT IN PKG : BEGIN ##
########################################
# Any unit testing code goes here
import sys
if len(sys.argv) == 1 and sys.argv[0] == "-m":
    pass
    #print("\n{}\nTest: table.py\n".format("-"*30))
    #print("No unit tests written")
#######################################
##  HACK TO RUN SCRIPT IN PKG : END  ##
#######################################
