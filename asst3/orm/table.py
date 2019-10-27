#!/usr/bin/python3
#
# table.py
#
# Definition for an ORM database table and its metaclass
#

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

