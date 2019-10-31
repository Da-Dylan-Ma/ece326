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
    # Check if the database name is "easydb".
    if database_name != "easydb":
        raise NotImplementedError("EasyORM has not implemented " + str(database_name))

    schema = module2schema(module)
    return orm.easydb.Database(schema)

# Return a string which can be read by the underlying database to create the
# corresponding database tables.
#   database_name: str, database name
#   module: module, the module that contains the schema
def export(database_name, module):
    # Check if the database name is "easydb".
    if database_name != "easydb":
        raise NotImplementedError("EasyORM has not implemented " + str(database_name))

    # TODO: String builder to improve performance?
    schema = module2schema(module)
    schema_txt = ""
    conversion = {str: "string", int: "integer", float: "float"}
    for cls_name, cls in schema:
        schema_txt += cls_name + " {\n"
        for name, attr in cls:
            if attr in conversion: attr = conversion[attr]
            schema_txt += "    " + name + " : " + attr + ";\n"
        schema_txt += "}\n"
        if cls_name != schema[-1][0]: schema_txt += "\n" # aesthetics
    return schema_txt

def module2schema(module):
    """ Converts from module classes to ORM accepted schema,
        i.e. str/int/float/Key """
    # TODO: Add implementation for DateTime and Coordinate objs
    # TODO: Improve efficiency of sorting
    schema = []
    for cls_name, obj in inspect.getmembers(module):
        if not inspect.isclass(obj): continue
        table_attrs = []
        for name, attr in inspect.getmembers(obj):
            if not isinstance(attr, orm.fields.Field): continue
            if type(attr) == orm.String:
                primitive = str
            elif type(attr) == orm.Float:
                primitive = float
            elif type(attr) == orm.Integer:
                primitive = int
            elif type(attr) == orm.Foreign:
                primitive = attr.table.__name__
            else:
                raise ValueError("Unknown obj: {}".format(attr.__name__))
            table_attrs.append((name, primitive))
        schema.append((cls_name, tuple(table_attrs)))
    return sort_schema(schema)

def sort_schema(schema):
    # Schema sort by order of entry, using reverse toposort
    dependencies = []
    for cls_name, cls_attrs in schema:
        parents = list(filter(lambda a: type(a) == str, map(lambda na: na[1], cls_attrs)))
        dependencies.append([cls_name] + parents)

    schema_order = list(reversed(linearize(dependencies)))
    for i in range(len(schema_order)):
        for cls_name, cls_attrs in schema:
            if cls_name == schema_order[i]:
                schema_order[i] = (cls_name, cls_attrs)
                break
    return tuple(schema_order)

def linearize(dependencies):
    # Use C3 linearization for topological sort
    # Remove all empty lists
    while [] in dependencies: dependencies.remove([])
    if not dependencies: return []
    # Next item must always be head
    for next_item in set(map(lambda x: x[0], dependencies)):
        for dependency in dependencies:
            if next_item in dependency[1:]:
                break # invalid found
        else:
            break # valid found
    else:
        raise ValueError("Cyclical dependency found! Invalid schema.")

    # Remove next_item
    for dependency in dependencies:
        if next_item in dependency:
            dependency.remove(next_item)
    return [next_item] + linearize(dependencies)
