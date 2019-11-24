#!/usr/bin/python3
#
# fields.py
#
# Definitions for all the fields in easyORM
#

from datetime import datetime
import time


# base field type
class Field:
    # Implement or change me.
    implemented = True  # boolean to check whether the field is implemented

    def __init__(self, composed=False):
        self.default = None
        self.composed = composed
        self.blank = None
        self.choices = ()


    # which op it supported
    @classmethod
    def supported_op(cls):
        return ("eq", "ne", "gt", "lt")

    # decomp
    def decompose(self, rval):
        return ()

    # return data base cols
    # how it should be saved to
    # database
    def db_model(self, field_name):
        return []

    # return to database values
    def db_value(self, instance,  field_name):
        return []


# notes about __set__ and __get___
# set type could be the type it designated, for example Datetime the type could be datetime
# and also could be a list of columns type for example, Coordinate the type could be list or tuple
# and also can be other type, Float (int, float) both works
# INTEGER TYPE
class Integer(Field):
    def __init__(self, blank=False, default=None, choices=()):
        # check choices right type
        Field.__init__(self)
        if len(choices) != 0:
            for c in choices:
                if not type(c) == int:
                    raise TypeError
        if default is not None:
            if not type(default) == int:
                raise TypeError
            blank = True
        elif blank:
            default = 0
        self.default = default
        self.blank = blank
        self.choices = choices
        self._values = {}
        pass

    def __set__(self, instance, value):
        # check value type
        if value is None:
            if self.blank:
                value = self.default
            else:
                raise ValueError
        elif type(value) == list and len(value) == 1:
            self.__set__(instance, value[0])
            return
        elif type(value) == int:
            self._values[instance] = value
        else:
            raise TypeError
        pass

    def __get__(self, instance, owner):
        if instance not in self._values:
            return self.default
        return self._values[instance]

    def db_model(self, field_name):
        return (field_name, int),

    def db_value(self, instance, field_name):
        val = instance.__getattribute__(field_name)
        if not len(self.choices) == 0:
            if val not in self.choices:
                raise ValueError
        return [(field_name, val)]

    @classmethod
    def supported_op(cls):
        return ("eq", "ne", "gt", "lt")


# FLOAT TYPE
class Float(Field):
    def __init__(self, blank=False, default=None, choices=()):
        # check choices right type
        Field.__init__(self)
        self.choices = set()
        if len(choices) != 0:
            for c in choices:
                if not (type(c) == float or type(c) == int):
                    raise TypeError
                self.choices.add(float(c))
        if default is not None:
            if not type(default) == float and not type(default) == int:
                raise TypeError
            default = float(default)
            blank = True
        elif blank:
            default = 0.0
        self.default = default
        self.blank = blank
        self._values = {}
        pass

    def __set__(self, instance, value):
        # check value type
        if value is None:
            if self.blank is not None and self.blank:
                self._values[instance] = self.default
            else:
                raise ValueError
        elif type(value) == list and len(value) == 1:
            self.__set__(instance, value[0])
            return
        elif type(value) == float or type(value) == int:
            self._values[instance] = float(value)
        else:
            raise TypeError
        pass

    def __get__(self, instance, owner):
        if instance not in self._values:
            return self.default
        val = self._values[instance]
        return val

    def db_model(self, field_name):
        return (field_name, float),

    def db_value(self, instance, field_name):
        val = instance.__getattribute__(field_name)
        if not len(self.choices) == 0:
            if val not in self.choices:
                raise ValueError
        return [(field_name, val)]

    @classmethod
    def supported_op(cls):
        return ("eq", "ne", "gt", "lt")


# STRING TYPE
class String(Field):
    def __init__(self, blank=None, default=None, choices=()):
        Field.__init__(self)
        # check choices right type
        if len(choices) != 0:
            for c in choices:
                if not (type(c) == str):
                    raise TypeError
        if default is not None:
            if not type(default) == str:
                raise TypeError
            blank = True
        elif blank:
            default = ""
        self.default = default
        self.blank = blank
        self.choices = choices
        self._values = {}
        pass

    def __set__(self, instance, value):
        # check value type
        if value is None:
            if self.blank is not None and self.blank:
                self._values[instance] = self.default
            else:
                raise ValueError
        elif type(value) == list and len(value) == 1:
            self.__set__(instance, value[0])
            return
        elif type(value) == str:
            self._values[instance] = value
        else:
            raise TypeError
        pass

    def __get__(self, instance, owner):
        if instance not in self._values:
            return self.default
        val = self._values[instance]
        return val

    def db_model(self, field_name):
        return (field_name, str),

    def db_value(self, instance, field_name):
        val = instance.__getattribute__(field_name)
        if not len(self.choices) == 0:
            if val not in self.choices:
                raise ValueError
        return[(field_name, val)]

    @classmethod
    def supported_op(cls):
        return ("eq", "ne", "gt", "lt")


# FOREIGN KEY TYPE
class Foreign(Field):
    def __init__(self, tb, blank=False):
        Field.__init__(self)
        from orm.table import MetaTable
        if not type(tb) == MetaTable:
            raise TypeError
        self.blank = blank
        self.table = tb
        self._values = {}
        pass

    def __set__(self, instance, value):
        from orm.table import MetaTable
        # check value type
        if value is None:
            if self.blank:
                self._values[instance] = self.default
            else:
                raise ValueError
        if type(value) == list and len(value) == 1:
            self.__set__(instance, value[0])
            return
        elif type(value) == self.table:
            self._values[instance] = value
        else:
            raise TypeError
        pass

    def __get__(self, instance, owner):
        if instance not in self._values:
            return None
        # check refs
        obj = self._values[instance]
        return obj

    def db_model(self, field_name):
        return (field_name, self.table.__name__),

    def db_value(self, instance, field_name):
        value = instance.__getattribute__(field_name)
        if value is None:
            pk = 0
        else:
            pk = value.pk
        return [(field_name, pk)]

    @classmethod
    def supported_op(cls):
        return ("eq", "ne")


# DATETIME TYPE
class DateTime(Field):
    def __init__(self, blank=False, default=None):
        Field.__init__(self, True)
        if default is not None:
            if not type(default) == datetime:
                if not callable(default):
                    raise TypeError
            blank = True
        elif blank:
            default = datetime.fromtimestamp(0)
        self.default = default
        self.blank = blank
        self._values = {}
        pass
        # composed field

    def __set__(self, instance, value):
        # check value type
        if value is None:
            if self.blank:
                self._values[instance] = self.default
            else:
                raise ValueError
        if type(value) == datetime:
            self._values[instance] = float(time.mktime(value.timetuple()))
        elif callable(value):
            self._values[instance] = float(time.mktime(value().timetuple()))
        elif type(value) == list and len(value) == 1:
            db_val = value[0]
            if type(db_val) == int or type(db_val) == float:
                self._values[instance] = float(db_val)
                return
            else:
                raise ValueError
        else:
            raise TypeError
        pass

    def __get__(self, instance, owner):
        if instance not in self._values:
            return self.get_default()
        # retrive value, from time stamp
        return datetime.fromtimestamp(float(self._values[instance]))

    def get_default(self):
        if callable(self.default):
            return self.default()
        else:
            return self.default

    def db_model(self, field_name):
        return (field_name, float),

    def db_value(self, instance, field_name):
        if instance in self._values:
            value = self._values[instance]
        else:
            value = float(time.mktime(self.get_default().timetuple()))
        return [(field_name, value)]

    @classmethod
    def supported_op(cls):
        return ("eq", "ne", "gt", "lt")

    # decomp
    def decompose(self, rval):
        return (int(time.mktime(rval.timetuple())), )

    def compose(self, tb_obj, values):
        self._values[tb_obj] = values[0]


# COORDINATE TYPE
class Coordinate(Field):
    def __init__(self, blank=False, default=None):
        Field.__init__(self, True)
        if default is not None:
            self.check_value(default)
            blank = True
        elif blank:
            default = (0.0, 0.0)
        self._lat_values = {}
        self._lon_values = {}
        self.default = default
        self.blank = blank
        self._values = {}
        pass

    def check_value(self, value):
        if not type(value) == tuple and not type(value) == list:
            raise ValueError
        if len(value) != 2:
            raise ValueError
        for p in value:
            if not type(p) == int and not type(p) == float:
                raise ValueError
            if p < -180.0 or p > 180.0:
                raise ValueError

    def __set__(self, instance, value):
        # check value type
        if value is None:
            if self.blank:
                self._values[instance] = self.default
            else:
                raise ValueError
        self.check_value(value)
        self._lat_values[instance] = value[0]
        self._lon_values[instance] = value[1]
        pass

    def __get__(self, instance, owner):
        if instance not in self._lat_values:
            return self.default
        return self._lat_values[instance], self._lon_values[instance]

    def db_model(self, field_name):
        return (field_name + '_lat', float), (field_name + '_lon', float)

    def db_value(self, instance, field_name):
        if instance in self._lat_values:
            lat = self._lat_values[instance]
            lon = self._lon_values[instance]
        else:
            lat = self.default[0]
            lon = self.default[1]
        return [(field_name + '_lat', lat), (field_name + '_lon', lon)]

    @classmethod
    def supported_op(cls):
        return ("eq", "ne")

    # decomp
    def decompose(self, rval):
        return rval

