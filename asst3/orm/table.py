#!/usr/bin/python3
#
# table.py
#
# Definition for an ORM database table and its metaclass
#
# IMPORTANT NOTICE:
# - Very hackish nature of Coordinate. Suggest to formalize by specifying number
#   of DB fields required per field, and the parser for respective fields,
#   within the orm.fields classes themselves.

import orm.easydb
from collections import OrderedDict
from orm.exceptions import InvalidReference
from orm.fields import Integer, Float, String, Foreign, DateTime, Coordinate, datetime, Field

# print("WARNING: Does not work with concurrent database accesses, due to nature of\n",
#       "        globals/class creation. Unit testing difficult due state changes.")

def flatten(lst):
    # simple flattener, cannot handle cyclical lists
    if len(lst) == 0: return []
    if type(lst[0]) in (tuple, list):
        return flatten(lst[0]) + flatten(lst[1:])
    return [lst[0]] + flatten(lst[1:])


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
    def get(cls, db, pk):
        values, version = db.get(cls.__name__, pk)
        kwargs = {}
        values_idx = 0
        for field_name, obj in cls._fields:
            if type(obj) is orm.fields.Coordinate:
                kwargs[field_name] = (values[values_idx], values[values_idx+1])
                values_idx += 2
            else:
                kwargs[field_name] = values[values_idx]
                values_idx += 1
        assert values_idx == len(values) # list exhausted
        kwargs["pk"] = pk
        kwargs["version"] = version
        return cls(db, **kwargs)

    # Returns a list of objects that matches the query. If no argument is given,
    # returns all objects in the table.
    # db: database object, the database to get the object from
    # kwarg: the query argument for comparing
    def filter(cls, db, **kwargs):
        for column, value in kwargs.items():
            if "__" in column:
                column_name, op = column.split("__")
                try:
                    op = {"ne": orm.easydb.OP_NE,
                          "gt": orm.easydb.OP_GT,
                          "lt": orm.easydb.OP_LT}[op]
                except KeyError:
                    raise ValueError("Operation `{}` not supported!".format(op))
            else:
                column_name = column
                op = orm.easydb.OP_EQ


        # Auto unboxing of object pk / datetime
        if isinstance(value, Table): value = value.pk
        if isinstance(value, datetime): value = value.timestamp()
        if isinstance(value, tuple) or isinstance(value, list):
            # Trust in the fact that only Coordinate uses tuple :>
            assert len(value) == 2
            assert op in (orm.easydb.OP_EQ, orm.easydb.OP_NE)
            if op == orm.easydb.OP_EQ:
                ids_1 = set(db.scan(cls.__name__, (column_name+"_lat", op, value[0])))
                ids_2 = set(db.scan(cls.__name__, (column_name+"_long", op, value[1])))
                ids = list(sorted(list(ids_1.intersection(ids_2))))
            elif op == orm.easydb.OP_NE: # different logic
                ids_1 = set(db.scan(cls.__name__, (column_name+"_lat", op, value[0])))
                ids_2 = set(db.scan(cls.__name__, (column_name+"_long", op, value[1])))
                ids = list(sorted(list(ids_1.union(ids_2))))
            return [cls.get(db, obj_id) for obj_id in ids]

        ids = db.scan(cls.__name__, (column_name, op, value))
        return [cls.get(db, obj_id) for obj_id in ids]

    # Returns the number of matches given the query. If no argument is given,
    # return the number of rows in the table.
    # db: database object, the database to get the object from
    # kwarg: the query argument for comparing
    def count(cls, db, **kwargs):
        for column, value in kwargs.items():
            if "__" in column:
                column_name, op = column.split("__")
                try:
                    op = {"ne": orm.easydb.OP_NE}[op]
                except KeyError:
                    raise ValueError("Operation `{}` not supported!".format(op))
            else:
                column_name = column
                op = orm.easydb.OP_EQ

        # Auto unboxing of object pk / datetime
        if isinstance(value, Table): value = value.pk
        if isinstance(value, datetime): value = value.timestamp()
        if isinstance(value, tuple) or isinstance(value, list):
            # Trust in the fact that only Coordinate uses tuple :>
            assert len(value) == 2
            assert op in (orm.easydb.OP_EQ, orm.easydb.OP_NE)
            if op == orm.easydb.OP_EQ:
                ids_1 = set(db.scan(cls.__name__, (column_name+"_lat", op, value[0])))
                ids_2 = set(db.scan(cls.__name__, (column_name+"_long", op, value[1])))
                ids = list(sorted(list(ids_1.intersection(ids_2))))
            elif op == orm.easydb.OP_NE: # different logic
                ids_1 = set(db.scan(cls.__name__, (column_name+"_lat", op, value[0])))
                ids_2 = set(db.scan(cls.__name__, (column_name+"_long", op, value[1])))
                ids = list(sorted(list(ids_1.union(ids_2))))
            return len(ids)

        ids = db.scan(cls.__name__, (column_name, op, value))
        return len(ids)

# table class
class Table(object, metaclass=MetaTable):

    # constructor
    def __init__(self, db, **kwargs):
        self.pk = None # ID (primary key)
        self.version = None # version
        if "pk" in kwargs: # override
            self.pk = kwargs["pk"]
            self.version = kwargs["version"]
        self.db = db # database object
        self._table_name = self.__class__.__name__

        fields = self.__class__._fields
        bad_fields = set(kwargs)-set(dict(fields))-set(["pk","version"])
        if len(bad_fields) != 0:
            raise AttributeError("Unknown attributes {} found.".format(bad_fields))
        self._field_names = tuple(zip(*fields))[0] # ORM

        # Type conversion occurs here, i.e. Foreign, Datetime, Coordinate
        # when specifying as alternative form, e.g. user=2 instead of user='joe'
        for k, obj in fields:
            if k in kwargs:
                if type(obj) is orm.fields.Foreign:
                    if type(kwargs[k]) is int: # parse from int to foreign key
                        kwargs[k] = obj.table.get(self.db, kwargs[k]) # recursive
                if type(obj) is orm.fields.DateTime:
                    if type(kwargs[k]) is float: # parse from float to datetime
                        kwargs[k] = datetime.fromtimestamp(kwargs[k])
                setattr(self, k, kwargs[k])
            else:
                setattr(self, k, None)

    def _values(self):
        # Parser for native DB
        # Need to parse foreign keys into database friendly int values
        values = list(map(lambda field: getattr(self, field), self._field_names))
        new_values = []
        for i in range(len(values)):
            value = values[i]
            if isinstance(value, Table): # foreign key parsing
                new_values.append(value.pk)
            elif type(value) is datetime:
                new_values.append(value.timestamp()) # convert to POSIX timestamp
            else:
                new_values.append(value)
        # hackish, but we rely on the fact that our implementation
        # uses continguous _lat and _long for storage, so simply flatten the
        # ordered list will do.
        return flatten(new_values)

    def _save_subroutine(self, atomic):
        # New entry
        if self.pk is None:
            self.pk, self.version = self.db.insert(self._table_name, self._values())
        else:
            args = [self._table_name, self.pk, self._values()]
            if atomic: args.append(self.version)
            self.version = self.db.update(*args)

    # Save the row by calling insert or update commands.
    # atomic: bool, True for atomic update or False for non-atomic update
    def save(self, atomic=True):
        # TODO: Error checking
        # Cascaded saving, check if foreign key referenced, and if its pk is None
        values = list(map(lambda field: getattr(self, field), self._field_names))
        for i in range(len(values)):
            value = values[i]
            if isinstance(value, Table): # foreign key
                if value.pk is None: # not saved yet
                    value.save(atomic)
        self._save_subroutine(atomic)

    # Delete the row from the database.
    def delete(self):
        self.db.drop(self._table_name, self.pk)
        self.pk = None
        self.version = None
