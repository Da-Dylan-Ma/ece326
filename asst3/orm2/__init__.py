#!/usr/bin/python3
#
# __init__.py
#
# Definition for setup and export function, as well as the Table class
#

import orm.easydb
import inspect

# all the classes that we export as a package
from orm.table import Table
from orm.fields import Integer, Float, String, Foreign, DateTime, Coordinate, datetime

# Return a database object that is initialized, but not yet connected.
#   database_name: str, database name
#   module: module, the module that contains the schema
def setup(database_name, module):
    if database_name != "easydb":
        raise NotImplementedError("EasyORM has not implemented " + str(database_name))

    schema = module2schema(module)
    return orm.easydb.Database(schema)

# Return a string which can be read by the underlying database to create the
# corresponding database tables.
#   database_name: str, database name
#   module: module, the module that contains the schema
def export(database_name, module):
    if database_name != "easydb":
        raise NotImplementedError("EasyORM has not implemented " + str(database_name))

    schema = module2schema(module)
    schema_txt = ""
    conversion = {str: "string", int: "integer", float: "float"}
    for cls_name, cls in schema:
        schema_txt += "{} {{\n".format(cls_name)
        for name, attr in cls:
            if attr in conversion: attr = conversion[attr]
            schema_txt += "    {}: {};\n".format(name, attr)
        schema_txt += "}\n"
        if cls_name != schema[-1][0]:
            schema_txt += "\n" # aesthetics
    return schema_txt

def module2schema(module):
    schema = []
    for cls_name, obj in inspect.getmembers(module):
        if not inspect.isclass(obj): continue
        table_register = obj._register # assume all tables are valid
        break
    else:
        raise RuntimeError("Empty schema.")

    # Create schema
    for cls in table_register:
        types = []
        field2type = {orm.String: str, orm.Float: float, orm.Integer: int}
        for name, attr in cls._fields:
            if "_" in name:
                raise ValueError("Cannot contain `_` in column name: `{}`".format(name))
            if type(attr) is orm.Foreign:
                primitive = attr.table.__name__
                types.append((name, primitive))
            elif type(attr) is orm.fields.DateTime:
                primitive = float # saving as POSIX timestamp
                types.append((name, primitive))
            elif type(attr) is orm.fields.Coordinate:
                types.append((name+"_lat", float))
                types.append((name+"_long", float))
            else:
                primitive = field2type[type(attr)]
                types.append((name, primitive))
        schema.append((cls.__name__, tuple(types)))
    return schema
