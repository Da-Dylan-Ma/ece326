#!/usr/bin/python3
#
# table.py
#
# Definition for an ORM database table and its metaclass
#
import orm
from orm.easydb import *
import collections
from orm.exceptions import InvalidReference
from orm.fields import Field, Integer, Float, String, Foreign, DateTime, Coordinate, datetime

op_dict = {"eq": 1, "ne": 2, "lt": 3, "gt": 4}


def list_intersection(l1, l2):
    return [elm for elm in l1 if elm in l2]


def list_union(l1, l2):
    for elm in l2 :
        if elm not in l1:
            l1.append(elm)
    return l1


# metaclass of table
class MetaTable(type):
    _instances = {}
    _table_classes = []

    def __init__(cls, name, bases, attrs):
        if cls not in cls._table_classes:
            cls._table_classes.append(cls)
        type.__init__(cls, name, bases, attrs)

    def __new__(mcs, name, bases, classdict):
        result = type.__new__(mcs, name, bases, collections.OrderedDict(classdict))
        result.__fields__ = [k for k in classdict.keys() if k[0] != "_"]
        return result

    # ordered introspection of class members
    @classmethod
    def __prepare__(mcs, name, bases):
        return collections.OrderedDict()

    # Returns an existing object from the table, if it exists.
    #   db: database object, the database to get the object from
    #   pk: int, primary key (ID)
    # usage: City.get(db, 1)
    def get(cls, db, pk):
        if not type(db) == Database:
            raise TypeError
        if not type(pk) == int:
            raise TypeError
        if pk < 1:
            raise ValueError
        if cls not in MetaTable._instances:
            MetaTable._instances[cls] = {}
        table_name = cls.__name__
        # any other exceptions should be raised here
        db_cols, version = db.get(table_name, pk)
        kwargs = {}
        i = 0
        for f_name in cls.__fields__:
            f_obj = cls.__dict__[f_name]
            if isinstance(f_obj, Field):
                # if foreign then need to extract
                if isinstance(f_obj, Foreign):
                    kwargs[f_name] = f_obj.table.get(db, db_cols[i])
                    i += 1
                else:
                    values = []
                    for j in range(len(f_obj.db_model(f_name))):
                        values.append(db_cols[i])
                        i += 1
                    kwargs[f_name] = values
        if pk in MetaTable._instances[cls]:
            MetaTable._instances[cls][pk].refresh_state(**kwargs)
        else:
            MetaTable._instances[cls][pk] = cls.__call__(db, **kwargs)
        MetaTable._instances[cls][pk].pk = pk
        MetaTable._instances[cls][pk].version = version
        return MetaTable._instances[cls][pk]

    def remove_from_cache(cls, pk):
        print(cls)

    # results = [[col1_cmp_results...], [col2_cmp_results...]]
    @staticmethod
    def combine_scan_results(op_str, results):
        # non composed type
        if len(results) == 0:
            return []
        if len(results) == 1:
            return results[0]
        ret = results[0]
        for r in results[1:]:
            if op_str == "eq":
                ret = list_intersection(ret, r)
            else:
                ret = list_union(ret, r)
        return ret

    def filter_count_helper(cls, db, **kwarg):
        # Implement me.
        if not type(db) == Database:
            raise TypeError
        table_name = cls.__name__
        queries = []
        op_str = "eq"
        if kwarg is None or len(kwarg) == 0:
            # scan for pk not equal to 0,
            # suppose non object with pk equal to 0
            # so it will return all objects in table
            queries.append(("pk", OP_NE, -1))
        else:
            for col_query, rvalue in kwarg.items():
                if "__" in col_query:
                    # retrive op
                    f_name, op_str = col_query.split("__")
                else:
                    f_name = col_query
                    op_str = "eq"

                op = op_dict[op_str]
                # first check left side
                if f_name == "pk":
                    if not type(rvalue) == int:
                        raise ValueError
                    if op_str not in ("eq", "ne"):
                        raise ValueError
                    queries.append((f_name, op, rvalue))
                elif f_name not in cls.__dict__ or not isinstance(cls.__dict__[f_name], Field):
                    raise ValueError
                else:
                    f_obj = cls.__dict__[f_name]
                    if op_str not in f_obj.supported_op():
                        raise ValueError
                    # for Foreign, rvalue could be its field type
                    # or a int
                    if isinstance(f_obj, Foreign):
                        if isinstance(rvalue, f_obj.table):
                            if rvalue.pk is None:
                                raise ValueError
                            queries.append((f_name, op, rvalue.pk))
                        elif isinstance(rvalue, int):
                            queries.append((f_name, op, rvalue))
                        else:
                            raise TypeError
                    # composed type, need to decompose
                    elif f_obj.composed:
                        decom_rvals = f_obj.decompose(rvalue)
                        i = 0
                        for col_name, col_type in f_obj.db_model(f_name):
                            queries.append((col_name, op, decom_rvals[i]))
                            i += 1
                    else:
                        queries.append((f_name, op, rvalue))
                break
        return cls.combine_scan_results(op_str, [db.scan(table_name, query) for query in queries])



    # Returns a list of objects that matches the query. If no argument is given,
    # returns all objects in the table.
    # db: database object, the database to get the object from
    # kwarg: the query argument for comparing
    # usage: Account.filter(db, balance__lt=210.3)
    def filter(cls, db, **kwarg):
        return [cls.get(db, pk) for pk in cls.filter_count_helper(db, **kwarg)]

    # Returns the number of matches given the query. If no argument is given,
    # return the number of rows in the table.
    # db: database object, the database to get the object from
    # kwarg: the query argument for comparing
    def count(cls, db, **kwarg):
        return len(cls.filter_count_helper(db, **kwarg))


# table class
class Table(object, metaclass=MetaTable):
    # constructor
    def __init__(self, db, **kwargs):
        self.version = None
        self.pk = None  # ID (primary key)
        if not (type(db) == Database):
            raise TypeError
        self.db = db
        all_fields = type(self).__dict__
        for f_name in type(self).__fields__:
            if f_name not in all_fields:
                continue
            f_obj = all_fields[f_name]
            if not isinstance(f_obj, Field):
                continue
            if f_name in kwargs:
                self.__setattr__(f_name, kwargs[f_name])
            elif f_obj.blank:
                self.__setattr__(f_name, f_obj.default)
            else:
                raise AttributeError

    def refresh_state(self, **kwargs):
        all_fields = type(self).__dict__
        for f_name in type(self).__fields__:
            if f_name not in all_fields:
                continue
            f_obj = all_fields[f_name]
            if not isinstance(f_obj, Field):
                continue
            if f_name in kwargs:
                self.__setattr__(f_name, kwargs[f_name])
            elif f_obj.blank and f_obj.default is not None:
                self.__setattr__(f_name, f_obj.default)

    # Save the row by calling insert or update commands.
    # atomic: bool, True for atomic update or False for non-atomic update
    def save(self, atomic=True):
        tb_name = type(self).__name__
        row = []
        all_fields = type(self).__dict__
        for f_name in type(self).__fields__:
            if f_name not in all_fields:
                continue
            f_obj = all_fields[f_name]
            if not isinstance(f_obj, Field):
                continue
            if not isinstance(f_obj, Field):
                continue
            if isinstance(f_obj, Foreign):
                ref_obj = self.__getattribute__(f_name) # ref_obj is table type
                if ref_obj is not None:
                    try:
                        ref_obj.save(atomic)
                    except ObjectDoesNotExist:
                        raise InvalidReference
            for col_name, col_val in f_obj.db_value(self, f_name):
                row.append(col_val)
        # then check self status
        if self.pk is None:
            # call insert
            self.pk, self.version = self.db.insert(tb_name, row)
        else:
            # call update
            if atomic:
                ver = self.version
            else:
                ver = None
            try:
                self.version = self.db.update(tb_name, self.pk, row, ver)
            except InvalidReference:
                self.pk = None
                raise InvalidReference
            except ObjectDoesNotExist:
                self.pk = None
                raise InvalidReference
        pass

    # Delete the row from the database.
    def delete(self):
        table_name = type(self).__name__
        self.db.drop(table_name, self.pk)
        self.pk = None
        self.version = None
        pass

#fcuk