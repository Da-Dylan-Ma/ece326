#!/usr/bin/python3
#
# __init__.py
#
# Definition for setup and export function, as well as the Table class
#

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

