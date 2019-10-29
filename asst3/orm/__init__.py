#!/usr/bin/python3
#
# __init__.py
#
# Definition for setup and export function, as well as the Table class
#

########################################
##  HACK TO RUN SCRIPT IN PKG : BEGIN ##
########################################
# Required to ignore RuntimeWarning from running orm.<modules>,
# since the module will be loaded multiple times due to the imports below
# Informative SO: https://stackoverflow.com/q/43393764
# Remember to delete before deployment, including the hacks in other scripts
import warnings
warnings.filterwarnings('ignore', category=RuntimeWarning, module='runpy')

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

# all the classes that we export as a package
from orm.table import Table
from orm.fields import Integer, Float, String, Foreign, DateTime, Coordinate, datetime

# Return a database object that is initialized, but not yet connected.
#   database_name: str, database name
#   module: module, the module that contains the schema
def setup(database_name, module):
    # Check if the database name is "easydb".
    if database_name != "easydb":
        raise NotImplementedError("EasyORM has not implemented " + str(database_name))

    # Implement me: read schema from module.
    schema = []

    return orm.easydb.Database(schema)

# Return a string which can be read by the underlying database to create the
# corresponding database tables.
#   database_name: str, database name
#   module: module, the module that contains the schema
def export(database_name, module):
    # Check if the database name is "easydb".
    if database_name != "easydb":
        raise NotImplementedError("EasyORM has not implemented " + str(database_name))

    # Implement me.
    return ""
