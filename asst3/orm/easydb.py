#!/usr/bin/python3
#
# easydb.py
#
# Definition for the Database class for EasyDB
#

import socket
import struct
from orm.exceptions import *

# EasyDB query operators
OP_EQ = 1  # equal
OP_NE = 2  # not equal
OP_LT = 3  # less than
OP_GT = 4  # greater than
OP_LE = 5  # (optional): less than or equal
OP_GE = 6  # (optional): greater than or equal

# EasyDB database implementation
class Database:

    def __repr__(self):
        return "<EasyDB Database object>"

    def __init__(self, tables):
        """ Constructor
            tables -- all the tables (and their structures) in the database
        """
        # Purely error checking
        table_names = []
        for table_name, cols in tables:
            if type(table_name) is not str:
                raise TypeError("Table name `{}` is not of type str".format(table_name))

            for col_name, col_type in cols:
                if type(col_name) is not str:
                    raise TypeError("Column name `{}` is not of type str".format(col_name))
                if col_name in ("id", "pk"):
                    raise ValueError("Column name `{}` is not allowed".format(col_name))
                if type(col_type) is str:
                    if col_type not in table_names:
                        raise IntegrityError("Foreign key reference `{}` does not exist".format(col_type))
                elif col_type not in (str, float, int):
                    raise ValueError("Column type `{}` is not allowed".format(col_type))
            table_names.append(table_name) # prevent cyclical references

        self.tables = [None] + list(tables) # considered dict, but need preserve order
        self.table_names = [None] + table_names

    # Connect to the database.
    #   host: str, host name
    #   port: int, port number.
    def connect(self, host, port):
        # socket.AF_INET -> IPv4 addresses
        # socket.SOCK_STREAM -> TCP
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, int(port)))

    # Close the connection to the database.
    def close(self):
        self.send(self.REQUEST("EXIT", 0))
        self.socket.close()

    # Make the database to add a new row to a database table.
    #   table_name: str, name of the table
    #   values: sequence, the new row to insert to the table
    def insert(self, table_name, values):
        # Basic error checking
        # Table must exist
        if table_name not in self.table_names:
            raise ValueError("`{}` does not exist.".format(table_name))
        expected_argc = self.get_table_argc(table_name)
        # Length of arguments must match
        if len(values) != expected_argc:
            raise ValueError("Number of values do not match: expected {} instead of {}.".format(expected_argc, len(values)))
        # Must be accepted type
        for value in values:
            if type(value) not in (str, int, float):
                raise ValueError("Invalid type: `{}` is of type {}".format(value, type(value)))

        # Send message
        table_id = self.get_table_id(table_name)
        msg = self.REQUEST("INSERT", table_id) + self.ROW(values)
        self.send(msg)

        # Get response
        response = self.receive()
        code = self.read_response_code(response[:4])
        if code != "OK":
            if code == "BAD_FOREIGN":
                raise InvalidReference("Referenced row does not exist.")
            elif code in ("BAD_TABLE", "BAD_VALUE", "BAD_ROW"):
                raise PacketError("`{}` raised.".format(code))
            else:
                raise RuntimeError("Unexpected code: `{}`".format(code))

        return self.read_key(response[4:])

    # Make the database to update an existing row in a table.
    #   table_name: str, name of the table
    #   pk: int, row ID
    #   values: sequence, the new row to update to the table
    #   version: int, version of the row
    def update(self, table_name, pk, values, version=None):
        # Basic error checking
        # Table must exist
        if table_name not in self.table_names:
            raise ValueError("`{}` does not exist.".format(table_name))
        expected_argc = self.get_table_argc(table_name)
        # Length of arguments must match
        if len(values) != expected_argc:
            raise ValueError("Number of values do not match: expected {} instead of {}.".format(expected_argc, len(values)))
        # Must be accepted type
        for value in values:
            if type(value) not in (str, int, float):
                raise ValueError("Invalid type: `{}` is of type {}".format(value, type(value)))

        # Send message
        table_id = self.get_table_id(table_name)
        version = 0 if version is None else version
        msg = self.REQUEST("UPDATE", table_id) + self.KEY(pk, version) + self.ROW(values)
        self.send(msg)

        # Get response
        response = self.receive()
        code = self.read_response_code(response[:4])
        if code != "OK":
            if code == "BAD_FOREIGN":
                raise InvalidReference("Referenced row does not exist.")
            elif code == "TXN_ABORT":
                raise TransactionAbort("Atomic update failed.")
            elif code == "NOT_FOUND":
                raise ObjectDoesNotExist("Specified row does not exist.")
            elif code in ("BAD_TABLE", "BAD_VALUE", "BAD_ROW"):
                raise PacketError("`{}` raised.".format(code))
            else:
                raise RuntimeError("Unexpected code: `{}`".format(code))

        return self.read_version(response[4:])

    # Make the database to delete a row in table.
    #   table_name: str, name of the table
    #   pk: int, row ID
    def drop(self, table_name, pk):
        # Basic error checking
        # Table must exist
        if table_name not in self.table_names:
            raise ValueError("`{}` does not exist.".format(table_name))

        # Send message
        table_id = self.get_table_id(table_name)
        msg = self.REQUEST("DROP", table_id) + self.ID(pk)
        self.send(msg)

        # Get response
        response = self.receive()
        code = self.read_response_code(response[:4])
        if code != "OK":
            if code == "NOT_FOUND":
                raise ObjectDoesNotExist("Specified row does not exist.")
            elif code in ("BAD_TABLE", "BAD_VALUE", "BAD_ROW"):
                raise PacketError("`{}` raised.".format(code))
            else:
                raise RuntimeError("Unexpected code: `{}`".format(code))

        return

    # Make the database to retrieve a row from a table, which requires
    # specifying the id of the row.
    #   table_name: str, name of the table
    #   pk: int, row ID
    def get(self, table_name, pk):
        # Basic error checking
        # Table must exist
        if table_name not in self.table_names:
            raise ValueError("`{}` does not exist.".format(table_name))

        # Send message
        table_id = self.get_table_id(table_name)
        msg = self.REQUEST("GET", table_id) + self.ID(pk)
        self.send(msg)

        # Get response
        response = self.receive()
        code = self.read_response_code(response[:4])
        if code != "OK":
            if code == "NOT_FOUND":
                raise ObjectDoesNotExist("Specified row does not exist.")
            elif code in ("BAD_TABLE", "BAD_VALUE", "BAD_ROW"):
                raise PacketError("`{}` raised.".format(code))
            else:
                raise RuntimeError("Unexpected code: `{}`".format(code))

        version = self.read_version(response[4:8])
        values = self.read_row(response[8:])
        return values, version

    # Make the database to compare a column of every row in a table against
    # a value and returns the id of all rows that matched.
    #   table_name: str, name of the table
    #   query: tuple, a tuple of 3 elements: name of column, the operator,
    #          and the right operand, respectively
    def scan(self, table_name, query):
        # Basic error checking
        # Table must exist
        if table_name not in self.table_names:
            raise ValueError("`{}` does not exist.".format(table_name))
        if len(query) != 3:
            raise PacketError("Invalid number of query arguments: expected 3 not {}".format(len(query)))
        attr_name, operator, comparison = query
        if type(attr_name) is not str:
            raise ValueError("`{}` is not a string.")
        if not (1 <= operator <= 6):
            raise ValueError("Invalid operator value: {}".format(operator))
        if type(value) not in (str, int, float):
            raise ValueError("Invalid comparison value: {}".format(comparison))

        # Send message
        table_id = self.get_table_id(table_name)
        raise NotImplementedError("Column number needs to be obtained, order!?")
        # Also need to check type of value...
        column_id = None
        msg = self.REQUEST("SCAN", table_id) + self.COLUMN(column_id) \
            + self.OPERATOR(operator) + self.VALUE(query)
        self.send(msg)

        # Get response
        response = self.receive()
        code = self.read_response_code(response[:4])
        if code != "OK":
            if code == "NOT_FOUND":
                raise ObjectDoesNotExist("Specified row does not exist.")
            elif code in ("BAD_TABLE", "BAD_VALUE", "BAD_ROW"):
                raise PacketError("`{}` raised.".format(code))
            else:
                raise RuntimeError("Unexpected code: `{}`".format(code))

        count = self.read_int(response[4:8])
        response = response[8:]
        row_ids = []
        for i in range(count):
            row_ids.append(self.read_int(response[:4]))
            response = response[4:]
        return row_ids

    def get_table_id(self, table_name):
        return self.table_names.index(table_name)

    def get_table_argc(self, table_name):
        return len(self.tables[self.get_table_id(table_name)][1])

    # primitives
    def send(self, msg):
        self.socket.sendall(msg)

    def receive(self):
        return self.socket.recv(1024)

    def read_response_code(self, code):
        code = struct.unpack(">i", code)[0]
        return_vals = [None, "OK", "NOT_FOUND", "BAD_TABLE", "BAD_QUERY",
                       "TXN_ABORT", "BAD_VALUE", "BAD_ROW", "BAD_REQUEST",
                       "BAD_FOREIGN", "UNIMPLEMENTED"]
        return return_vals[code]

    def read_key(self, response):
        return struct.unpack(">qq", response)

    def read_version(self, response):
        return struct.unpack(">q", response)

    def read_row(self, response):
        count = self.read_int(response[:4])
        response = response[4:]
        values = []
        for i in range(count):
            val_type = self.read_int(response[:4])
            size = self.read_int(response[4:8])
            value_b = response[8:8+size]
            response = response[8+size:]
            if val_type == 1:
                value = self.read_int(value_b)
            elif val_type == 2:
                value = self.read_float(value_b)
            elif val_type == 3:
                value = self.read_string(value_b, size)
            elif val_type == 4:
                value = self.read_long(value_b)
            values.append(value)
        return tuple(values)

    def read_int(self, response):
        return struct.unpack(">i", response)

    def read_long(self, response):
        return struct.unpack(">q", response)

    def read_float(self, response):
        return struct.unpack(">f", response)

    def read_string(self, response, size):
        return struct.unpack(">{}s".format(size), response)

    def REQUEST(self, command_str, table_num):
        commands = [None, "INSERT", "UPDATE", "DROP", "GET", "SCAN", "EXIT"]
        assert type(table_num) is int
        assert -2147483648 <= table_num <= 2147483647
        assert command_str in commands
        return struct.pack(">ii", commands.index(command_str), table_num)

    def KEY(self, id, version):
        return struct.pack(">qq", id, version)

    def VALUE(self, value, attr_type):
        if type(attr_type) is str:
            return struct.pack(">iiq", 1, 8, value) # row id
        if attr_type is int:
            if type(value) is not int:
                raise ValueError("`{}` is not an integer.".format(value))
            return struct.pack(">iii", 1, 8, value)
        if attr_type is float:
            if type(value) not in (int, float):
                raise ValueError("`{}` is not a float.".format(value))
            return struct.pack(">iif", 2, 8, value)
        if attr_type is str:
            if type(value) is not str:
                raise ValueError("`{}` is not a string.".format(value))
            buffer_size = len(value)
            if buffer_size % 4 != 0:
                buffer_size = 4*(buffer_size//4 + 1) # 4-byte aligned
            return struct.pack(">ii{}s".format(buffer_size),
                               3, buffer_size, value.encode("ascii"))
        raise RuntimeError("Unexpected attr_type: `{}`".format(attr_type))

    def VALUE(self, value, foreign=False):
        if foreign:
            return struct.pack(">iiq", 1, 8, value) # row id
        if type(value) is int:
            if type(value) is not int:
                raise ValueError("`{}` is not an integer.".format(value))
            return struct.pack(">iii", 1, 8, value)
        if type(value) is float:
            if type(value) not in (int, float):
                raise ValueError("`{}` is not a float.".format(value))
            return struct.pack(">iif", 2, 8, value)
        if type(value) is str:
            if type(value) is not str:
                raise ValueError("`{}` is not a string.".format(value))
            buffer_size = len(value)
            if buffer_size % 4 != 0:
                buffer_size = 4*(buffer_size//4 + 1) # 4-byte aligned
            return struct.pack(">ii{}s".format(buffer_size),
                               3, buffer_size, value.encode("ascii"))
        raise RuntimeError("Unexpected attr_type: `{}`".format(type(value)))

    def ROW(self, values, val_types):
        msg = struct.pack(">i", len(values))
        for value, val_types in list(zip(values, val_types)):
            msg += self.VALUE(value, val_types)
        return msg

    def ROW(self, values):
        msg = struct.pack(">i", len(values))
        for value in values:
            msg += self.VALUE(value)
        return msg

    def ID(self, pk):
        return struct.pack(">q", pk)

    def VERSION(self, ver): # alias
        return struct.pack(">q", ver)

    def COLUMN(self, value):
        return struct.pack(">i", value)

    def OPERATOR(self, value):
        return struct.pack(">i", value)
