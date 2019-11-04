#!/usr/bin/python3
#
# table.py
#
# Definition for an ORM database table and its metaclass
#

import orm.easydb
from collections import OrderedDict
from orm.exceptions import InvalidReference
from orm.fields import Integer, Float, String, Foreign, DateTime, Coordinate, datetime, Field

print("WARNING: Does not work with concurrent database accesses, due to nature of\n",
      "        globals/class creation. Unit testing difficult due state changes.")

# metaclass of table
# used to implement methods only for the class itself?
# Implement me or change me. (e.g. use class decorator instead?)
class MetaTable(type):
    
    table_register = []
    table_name_register = []

    def __prepare__(mcls, bases):
        # {} insertion-ordered in python3.7 lang spec
        # for cross-compatibility, OrderedDict would be better
        return OrderedDict()

    def __new__(mcls, cls_name, bases, kwargs):
        cls = super().__new__(mcls, cls_name, bases, kwargs) # initialize class
        if cls_name != "Table": # ignore immediate Table base class
            cls._fields = []
            for k, v in kwargs.items():
                if not isinstance(v, Field): continue
                cls._fields.append((k, v))

            if cls_name in MetaTable.table_name_register:
                raise RuntimeError("Duplicate tables defined: {}.".format(cls_name))
            MetaTable.table_register.append(cls) # add to register
            MetaTable.table_name_register.append(cls_name)
            cls._register = MetaTable.table_register
        globals()[cls_name] = cls # define class in global namespace
        return cls

    # Returns an existing object from the table, if it exists.
    #   db: database object, the database to get the object from
    #   pk: int, primary key (ID)
    def get(self, db, pk):
        #values, version = db.get(self.__class__.__name__, pk)
        pass

    # Returns a list of objects that matches the query. If no argument is given,
    # returns all objects in the table.
    # db: database object, the database to get the object from
    # kwarg: the query argument for comparing
    def filter(self, db, **kwarg):
        #ids = db.scan(self.__class__.__name__, pk)
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

    _counter = {}

    # constructor
    def __init__(self, db, **kwargs):
        self.pk = None # ID (primary key)
        self.version = None # version
        self.db = db # database object

        fields = self.__class__._fields
        bad_fields = set(kwargs)-set(dict(fields))
        if len(bad_fields) != 0:
            raise AttributeError("Unknown attributes {} found.".format(bad_fields))
            
        for k, obj in fields:
            setattr(self, k, kwargs[k] if k in kwargs else None)

    # Save the row by calling insert or update commands.
    # atomic: bool, True for atomic update or False for non-atomic update
    def save(self, atomic=True):
        # Implement me.
        pass

    # Delete the row from the database.
    def delete(self):
        # Implement me.
        pass
