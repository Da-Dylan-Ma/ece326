#!/usr/bin/python3
#
# __init__.py
#
# Definition for setup and export function, as well as the Table class
#

import orm.easydb
import orm.table
import orm.exceptions
import orm.fields
import inspect

from orm.easydb import *
from orm.table import *
from orm.exceptions import *
from orm.fields import *


db_reserved_names = {"pk", "id", "version", "save", "delete"}

column_type_str_dict = {int: "integer", str: "string", float: "float"}


# Return a database object that is initialized, but not yet connected.
#   database_name: str, database name
#   module: module, the module that contains the schema
def setup(database_name, module):
    # Check if the database name is "easydb".
    if database_name != "easydb":
        raise NotImplementedError("EasyORM has not implemented " + str(database_name))
    # Implement me: read schema from module.
    schema = []
    created = set()
    tb_names = set()
    for name, cls in inspect.getmembers(module):
        tb_names.add(name)
    for tb_cls in MetaTable._table_classes:
        tb_name = tb_cls.__name__
        if tb_name in tb_names and tb_name not in created:
            tb_cls = module.__dict__[tb_name]
            if issubclass(type(tb_cls), type) and issubclass(tb_cls, Table) and not tb_cls == Table:
                # table name contains _
                if '_' in tb_name or tb_name in orm_reserved_words:
                    raise AttributeError
                created.add(tb_name)
                cols = []
                tb_fields = tb_cls.__fields__
                for f_name in tb_fields:
                    if f_name not in tb_cls.__dict__:
                        continue
                    f_obj = tb_cls.__dict__[f_name]
                    if not isinstance(f_obj, fields.Field):
                        continue
                    if '_' in f_name or f_name in orm_reserved_words:
                        raise AttributeError
                    for col_name, col_type in f_obj.db_model(f_name):
                        cols.append((col_name, col_type))
                schema.append((tb_name, cols))
    # other name checking is done in here
    return easydb.Database(schema)


orm_reserved_words = {"pk", "id", "version", "save", "delete"}


def table_str(tb_cls):
    tb_name = tb_cls.__name__
    if '_' in tb_name or tb_name in orm_reserved_words:
        raise AttributeError
    l_str = list()
    l_str.append(tb_name)
    l_str.append(" {\n")
    cols = tb_cls.__fields__
    for field_name in cols:
        if field_name not in tb_cls.__dict__:
            continue
        field_obj = tb_cls.__dict__[field_name]
        if not isinstance(field_obj, fields.Field):
            continue
        if '_' in field_name or field_name in orm_reserved_words:
            raise AttributeError
        for col_name, col_type in field_obj.db_model(field_name):
            # means forgein
            if type(col_type) == str:
                col_type_str = col_type
            elif type(col_type) == type:
                col_type_str = column_type_str_dict[col_type]
            else:
                raise TypeError
            l_str.append("    {}: {};\n".format(col_name, col_type_str))
    l_str.append("}\n")
    return "".join(l_str)


# Return a string which can be read by the underlying database to create the 
# corresponding database tables.
#   database_name: str, database name
#   module: module, the module that contains the schema
def export(database_name, module):
    # Check if the database name is "easydb".
    if database_name != "easydb":
        raise NotImplementedError("EasyORM has not implemented " + str(database_name))
    tb_str_l = []
    created_name = set()
    num = 0
    for tb_cls in MetaTable._table_classes:
        name = tb_cls.__name__
        if name in module.__dict__ and name not in created_name:
            if issubclass(tb_cls, Table) and not tb_cls == Table:
                if num > 0:
                    tb_str_l.append("\n")
                created_name.add(name)
                tb_str_l.append(table_str(tb_cls))
                num += 1
    return "".join(tb_str_l)

