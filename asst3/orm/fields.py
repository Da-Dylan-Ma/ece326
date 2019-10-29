#!/usr/bin/python3
#
# fields.py
#
# Definitions for all the fields in easyORM
#

from datetime import datetime

# base field type
class Field:
    # Implement or change me.
    implemented = True # boolean to check whether the field is implemented

# INTEGER TYPE
class Integer(Field):
    # Implement me.
     def __init__(self, blank=False, default=0, choices=()):
        # Implement or change me.
        pass

# FLOAT TYPE
class Float(Field):
    # Implement me.
    def __init__(self, blank=False, default=0., choices=()):
        # Implement or change me.
        pass

# STRING TYPE
class String(Field):
    # Implement me.
    def __init__(self, blank=False, default="", choices=()):
        # Implement or change me.
        pass

# FOREIGN KEY TYPE
class Foreign(Field):
    # Implement me.
    def __init__(self, table, blank=False):
        # Implement or change me.
        pass

# DATETIME TYPE
class DateTime(Field):
    # Implement me.
    implemented = False

# COORDINATE TYPE
class Coordinate(Field):
    # Implement me.
    implemented = False



if __name__ == "__main__":
    pass
