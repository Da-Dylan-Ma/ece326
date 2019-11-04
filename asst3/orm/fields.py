#!/usr/bin/python3
#
# fields.py
#
# Definitions for all the fields in easyORM
#
# On Descriptors:
# https://docs.python.org/3/reference/datamodel.html#implementing-descriptors

from datetime import datetime

# base field type
class Field:
    implemented = True # boolean to check whether the field is implemented

    def __init__(self, blank=True, default=None, choices=()):
        self.blank = blank
        self.choices = choices
        if not hasattr(self, "mapper"): self.mapper = {}
        self.mapper[self] = default

    def __get__(self, obj, objtype=None):
        return self.mapper[obj]

    def __set__(self, obj, value):
        if self.choices:
            if value not in self.choices:
                raise ValueError("`{}` is an invalid value.".format(value))
        self.mapper[obj] = value

    def __delete__(self, obj):
        print("parent delete")
        if not self.blank:
            raise AttributeError("Field cannot be blank.")
        self.mapper[obj] = None

# INTEGER TYPE
class Integer(Field):
    def __init__(self, blank=False, default=0, choices=()):
        super().__init__(blank, default, choices)

    def __set__(self, obj, value):
        if type(value) is not int:
            raise TypeError("`{}` is not an integer.".format(value))
        super().__set__(obj, value)

# FLOAT TYPE
class Float(Field):
    def __init__(self, blank=False, default=0., choices=()):
        super().__init__(blank, default, choices)

    def __set__(self, obj, value):
        if type(value) not in (int, float):
            raise TypeError("`{}` is not a float.".format(value))
        super().__set__(obj, value)

# STRING TYPE
class String(Field):
    def __init__(self, blank=False, default="", choices=()):
        super().__init__(blank, default, choices)

    def __set__(self, obj, value):
        if type(value) is not str:
            raise TypeError("`{}` is not a string.".format(value))
        super().__set__(obj, value)

# FOREIGN KEY TYPE
class Foreign(Field):
    def __init__(self, table, blank=False):
        super().__init__(blank)
        self.table = table

    def __set__(self, obj, value):
        raise NotImplemented
        if type(value) is not int:
            raise TypeError("`{}` is not a valid foreign key reference.".format(value))
        super().__set__(obj, value)

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
