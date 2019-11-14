#!/usr/bin/python3
#
# fields.py
#
# Definitions for all the fields in easyORM
#
# On Descriptors:
# https://docs.python.org/3/reference/datamodel.html#implementing-descriptors

from datetime import datetime

# base field type, generic field
class Field:
    implemented = True # boolean to check whether the field is implemented
    _values = {}

    def __init__(self, blank=True, default=None, choices=()):
        self.blank = blank
        self.choices = choices
        self.default = default
        Field._values[self] = {}

    def __get__(self, obj, objtype=None):
        return Field._values[self][obj]

    def __set__(self, obj, value):
        if not self.blank and value is None and self.default is None: # reject blank entries\
            raise AttributeError("Field cannot be blank.")
        if value is None: # set as default value if none provided
            value = self.default
        self.type_check(value) # sorry for calling static methods like that :>
        if self.choices and value not in self.choices:
            raise ValueError("`{}` is not an allowed value.".format(value))
        Field._values[self][obj] = value


    def __delete__(self, obj):
        if not self.blank:
            raise AttributeError("Field cannot be blank.")
        Field._values[self][obj] = None

    @staticmethod
    def type_check(value):
        pass # all generic values allowed

# INTEGER TYPE
class Integer(Field):
    def __init__(self, blank=False, default=0, choices=()):
        super().__init__(blank, default, choices)

    @staticmethod
    def type_check(value):
        if type(value) is not int:
            raise TypeError("`{}` is not an integer.".format(value))

# FLOAT TYPE
class Float(Field):
    def __init__(self, blank=False, default=0., choices=()):
        super().__init__(blank, default, choices)

    @staticmethod
    def type_check(value):
        if type(value) not in (int, float):
            raise TypeError("`{}` is not an integer/float.".format(value))

# STRING TYPE
class String(Field):
    def __init__(self, blank=False, default="", choices=()):
        super().__init__(blank, default, choices)

    @staticmethod
    def type_check(value):
        if type(value) is not str:
            raise TypeError("`{}` is not a string.".format(value))

# FOREIGN KEY TYPE
class Foreign(Field): # CHANGE ME
    def __init__(self, table, blank=False):
        super().__init__(blank)
        self.table = table

    def type_check(self, value):
        if type(value) is not self.table:
            raise TypeError("`{}` is not a valid foreign key reference.".format(value))

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
