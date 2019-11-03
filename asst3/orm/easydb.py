#!/usr/bin/python3
#
# easydb.py
#
# Definition for the Database class for EasyDB
#

import socket
import struct
from orm.exceptions import *
import orm.easydb_io as io

ISTREAM_BUFFER = 1024

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
                if io.is_foreign(col_type):
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
        self.send(io.REQUEST("EXIT", 0))
        self.socket.close()

    # Make the database to add a new row to a database table.
    #   table_name: str, name of the table
    #   values: sequence, the new row to insert to the table
    def insert(self, table_name, values):
        # Basic error checking
        # Table must exist
        if table_name not in self.table_names:
            raise ValueError("`{}` does not exist.".format(table_name))
        # Length of arguments must match
        expected_argc = self.get_table_argc(table_name)
        if len(values) != expected_argc:
            raise ValueError("Number of values do not match: expected {} instead of {}.".format(expected_argc, len(values)))
        # Types of arguments must match
        expct_types = self.get_table_arg_types(table_name)
        try:
            row = io.ROW(values, expct_types) # eager type checking
        except ValueError as e:
            raise e

        # Parse message
        table_id = self.get_table_id(table_name)
        msg = io.REQUEST("INSERT", table_id) + row

        # Parse response
        reply = self.send_receive(msg)
        code, reply = io.next_response(reply)
        if code != "OK":
            if code == "BAD_FOREIGN":
                raise InvalidReference("Referenced row does not exist.")
            elif code in ("BAD_TABLE", "BAD_VALUE", "BAD_ROW"):
                raise PacketError("`{}` raised.".format(code))
            else:
                raise RuntimeError("Unexpected code: `{}`".format(code))

        return io.read_key(reply)

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
        # pk must be integer
        if type(pk) is not int:
            raise ValueError("pk is not of type int, got `{}`.".format(type(pk)))
        expected_argc = self.get_table_argc(table_name)
        # Length of arguments must match
        if len(values) != expected_argc:
            raise ValueError("Number of values do not match: expected {} instead of {}.".format(expected_argc, len(values)))
        # Types of arguments must match
        expct_types = self.get_table_arg_types(table_name)
        try:
            row = io.ROW(values, expct_types) # eager type checking
        except ValueError as e:
            raise e

        # Parse message
        table_id = self.get_table_id(table_name)
        if version is None: version = 0
        msg = io.REQUEST("UPDATE", table_id) + io.KEY(pk, version) + row

        # Parse response
        reply = self.send_receive(msg)
        code, reply = io.next_response(reply)
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

        return io.read_version(reply)

    # Make the database to delete a row in table.
    #   table_name: str, name of the table
    #   pk: int, row ID
    def drop(self, table_name, pk):
        # Basic error checking
        # Table must exist
        if table_name not in self.table_names:
            raise ValueError("`{}` does not exist.".format(table_name))

        # Parse message
        table_id = self.get_table_id(table_name)
        msg = io.REQUEST("DROP", table_id) + io.ID(pk)

        # Parse response
        reply = self.send_receive(msg)
        code = io.read_response(reply)
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

        # Parse message
        table_id = self.get_table_id(table_name)
        msg = io.REQUEST("GET", table_id) + io.ID(pk)

        # Parse response
        reply = self.send_receive(msg)
        code, reply = io.next_response(reply)
        if code != "OK":
            if code == "NOT_FOUND":
                raise ObjectDoesNotExist("Specified row does not exist.")
            elif code in ("BAD_TABLE", "BAD_VALUE", "BAD_ROW"):
                raise PacketError("`{}` raised.".format(code))
            else:
                raise RuntimeError("Unexpected code: `{}`".format(code))

        version, reply = io.next_version(reply)
        values = io.read_row(reply)
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
            raise ValueError("Invalid number of query arguments: expected 3 not {}".format(len(query)))
        column_name, operator, comparison = query
        if type(column_name) is not str:
            raise ValueError("`{}` is not a string.".format(column_name))
        if type(operator) is not int:
            raise ValueError("`{}` is not a valid operator.".format(operator))
        if not (1 <= operator <= 6):
            raise ValueError("Invalid operator value: {}".format(operator))
        if type(comparison) not in (str, int, float):
            raise ValueError("Invalid comparison value: {}".format(comparison))

        # Get type of column and check
        column_id, column_type = self.get_column_id_type(table_name, column_name)
        # Operator only EQ or NE for foreign
        if io.is_foreign(column_type):
            if operator not in (OP_EQ, OP_NE):
                raise ValueError("Comparison of foreign keys support only EQ or NE.")
        try:
            value = io.VALUE(comparison, column_type) # eager type checking
        except ValueError as e:
            raise e


        # Parse message
        table_id = self.get_table_id(table_name)
        msg = io.REQUEST("SCAN", table_id) + io.COLUMN(column_id) \
            + io.OPERATOR(operator) + value

        # Parse response
        reply = self.send_receive(msg)
        code, reply = io.next_response(reply)
        if code != "OK":
            if code == "NOT_FOUND":
                raise ObjectDoesNotExist("Specified row does not exist.")
            elif code in ("BAD_TABLE", "BAD_VALUE", "BAD_ROW"):
                raise PacketError("`{}` raised.".format(code))
            else:
                raise RuntimeError("Unexpected code: `{}`".format(code))
        return io.read_ids(reply)

    def get_table_id(self, table_name):
        return self.table_names.index(table_name)

    def get_table_args(self, table_name):
        return self.tables[self.get_table_id(table_name)][1]

    def get_table_argc(self, table_name):
        return len(self.get_table_args(table_name))

    def get_table_arg_types(self, table_name):
        return list(map(lambda v: v[1], self.get_table_args(table_name)))

    def get_column_id_type(self, table_name, column_name):
        if column_name == "id": return 0, "" # foreign key, id
        args = self.get_table_args(table_name) # 0-indexed
        column_names = list(map(lambda v: v[0], args)) # 0-indexed
        if column_name not in column_names:
            raise ValueError("Column `{}` does not exist.".format(column_name))
        arg_id = column_names.index(column_name)
        column_type = args[arg_id][1]
        column_id = arg_id + 1 # 1-indexed
        return column_id, column_type

    def send(self, msg):
        self.socket.sendall(msg)

    def receive(self):
        # To receive unknown stream, we know easydb returns are 4-byte aligned
        # we increase buffer size by 1, and if maxed out => stream not terminated
        reply = self.socket.recv(ISTREAM_BUFFER + 1)
        if len(reply) == ISTREAM_BUFFER + 1:
            while True:
                part = self.socket.recv(ISTREAM_BUFFER)
                reply += part
                if len(part) != ISTREAM_BUFFER: break
        return reply

    def send_receive(self, msg):
        self.send(msg)
        return self.receive()
