#!/usr/bin/python3
#
# easydb.py
#
# Definition for the Database class for EasyDB
#

import socket
import struct
import orm.exceptions
from orm.exceptions import PacketError, TransactionAbort, ObjectDoesNotExist, InvalidReference, IntegrityError
import ctypes

# EasyDB command
CMD_INSERT = 1
CMD_UPDATE = 2
CMD_DROP = 3
CMD_GET = 4
CMD_SCAN = 5
CMD_EXIT = 6

# EasyDB query operators
OP_EQ = 1  # equal
OP_NE = 2  # not equal
OP_LT = 3  # less than
OP_GT = 4  # greater than
OP_LE = 5  # (optional): less than or equal
OP_GE = 6  # (optional): greater than or equal

# EasyDb response code
RES_OK = 1
RES_NOT_FOUND = 2
RES_BAD_TABLE = 3
RES_BAD_QUERY = 4
RES_TXN_ABORT = 5
RES_BAD_VALUE = 6
RES_BAD_ROW = 7
RES_BAD_REQUEST = 8
RES_BAD_FOREIGN = 9
RES_UNIMPLEMENTED = 10


COL_TYPE_INT = 1
COL_TYPE_FLOAT = 2
COL_TYPE_STRING = 3
COL_TYPE_FOREIGN = 4


col_type_code_dict = {int: COL_TYPE_INT, float: COL_TYPE_FLOAT, str: COL_TYPE_STRING}

column_format_dict = {COL_TYPE_INT: "!q", COL_TYPE_FLOAT: "!d", COL_TYPE_FOREIGN: "!q"}

supported_op_dict = {COL_TYPE_INT: (OP_EQ, OP_NE, OP_GT, OP_LT), COL_TYPE_FLOAT: (OP_EQ, OP_NE, OP_GT, OP_LT), COL_TYPE_STRING: (OP_EQ, OP_NE, OP_GT, OP_LT), COL_TYPE_FOREIGN: (OP_EQ, OP_NE)}

db_reserverd_word = {"pk", "id", "save", "get", "update", "delete", "insert"}
def check_table_name(table_dict, table_name=""):
    if not type(table_name) == str:
        raise TypeError
    if table_name in table_dict:
        raise Exception
    if not table_name[0].isupper():
        raise Exception
    pass


def check_col_name(added_col_name, col_name=""):
    if not type(col_name) == str:
        raise TypeError

    # not start with letters
    if not col_name[0].isalpha():
        raise Exception
        # already added
    if col_name in db_reserverd_word:
        raise Exception
    if col_name in added_col_name:
        raise Exception

    # character other than alpha and number and _
    for c in col_name[1:]:
        if not c.isalnum() and not c == '_':
            raise Exception
    pass


def pack_str(buf, offset, val):
    for byte in str.encode(val):
        struct.pack_into('!b', buf, offset, byte)
        offset += 1
    return offset


def pack_value(buf, offset, col_type_code, value):
    # first check value type is right
    check_col_type(col_type_code, value)
    if type(value) == str:
        if len(value) % 4 == 0:
            buf_sz = len(value)
        else:
            buf_sz = (len(value) // 4 + 1) * 4
    else:
        buf_sz = 8
    # pack into buf
    struct.pack_into("!ii", buf, offset, col_type_code, buf_sz)
    offset += struct.calcsize("!ii")
    end_pos = offset + buf_sz
    if col_type_code == COL_TYPE_STRING:
        offset = pack_str(buf, offset, value)
    else:
        fmt = column_format_dict[col_type_code]
        struct.pack_into(fmt, buf, offset, value)
        offset += struct.calcsize(fmt)
    # padding with zero
    while offset < end_pos:
        struct.pack_into("!b", buf, offset, 0)
        offset += struct.calcsize("!b")
    return offset


def unpack_str(buf, offset, len_limit):
    for i in range(len_limit):
        if buf[offset + i] == 0:
            return bytes.decode(buf[offset: offset + i])
    return bytes.decode(buf[offset: offset + len_limit])


# checking if value is correct
def check_col_type(col_type_code, value):
    value_type = type(value)
    if col_type_code == COL_TYPE_FOREIGN:
        if not value_type == int:
            raise ValueError
    elif col_type_code_dict[value_type] != col_type_code:
        if not (value_type == int and col_type_code == COL_TYPE_FLOAT):
            raise ValueError
    pass


# unpack value based on col and len
# from buf, returned on diff type
# col col-type
def unpack_value_from(col_type_code, buf, offset, len_limit):
    if col_type_code == COL_TYPE_STRING:
        return unpack_str(buf, offset, len_limit)
    else:
        fmt = column_format_dict[col_type_code]
        return struct.unpack_from(fmt, buf, offset)[0]
    pass


# EasyDB database implementation
class Database:
    def __repr__(self):
        return "<EasyDB Database object>"

    # constructor
    #   tables: all the tables (and their structures) in the database.

    # ("User", (  # table_name
    #     ("firstName", str),  # (column_name, type)
    #     ("lastName", str), ("height", float), ("age", int),
    # )),
    # ("Account", (
    #     ("user", "User"), ("type", str), ("balance", float),
    # ))
    def __init__(self, tables):
        # create socket
        self.connection = None
        # create a buf for sending
        self.send_buf = ctypes.create_string_buffer(4096)
        # look up index by table name, dict {table_name: index}
        self.table_index_dict = {}

        # look up column element type by column name { table_name:{ col_name: col_type_code }}
        self.table_col_type_dict = {}
        # look up column element index by column name { table_name:{ col_name: col_index }}
        self.table_col_index_dict = {}
        # some times we need to know the order of column names {table_name: [ col_name1, col_name2]}
        self.table_col_order_dict = {}
        i_tb = 1
        # col index lut
        # tb =  ("Account", (
        #     ("user", "User"), ("type", str), ("balance", float),
        # ))
        # tb[0] = table_name
        # tb[1] = columns definition
        for tb in tables:
            if len(tb) != 2:
                raise Exception
            tb_name = tb[0]
            # checking table name
            check_table_name(self.table_index_dict, tb_name)

            # sub dic for cols
            # add pk for placeholder, since 0 is
            # an error code
            col_names_in_order = ["pk", ]
            col_type_dict = {"pk": COL_TYPE_FOREIGN, }
            col_idx_dict = {"pk": 0, }

            # start from one, 0 is for pk
            i_col = 1
            # convert col_def to inner lut
            # raise exception when error happens
            for pair in tb[1]:
                # type_code = COL_TYPE_INT, COL_TYPE_FLOAT, COL_TYPE_STRING, COL_TYPE_FOREIGN
                if len(pair) != 2:
                    raise Exception
                # check for col name,
                check_col_name(col_idx_dict, pair[0])
                # means foreign type
                if type(pair[1]) == str:
                    # check if table name already defined
                    if pair[1] not in self.table_index_dict:
                        # not a defined foreign key
                        raise IntegrityError
                    # no problem
                    col_type_code = COL_TYPE_FOREIGN
                elif type(pair[1]) == type:
                    if pair[1] not in col_type_code_dict:
                        raise ValueError
                    col_type_code = col_type_code_dict[pair[1]]
                else:
                    raise ValueError

                # append a column to cols of table
                col_names_in_order.append(pair[0])
                col_type_dict[pair[0]] = col_type_code
                col_idx_dict[pair[0]] = i_col
                i_col += 1
            # all ok for a table
            self.table_col_order_dict[tb_name] = col_names_in_order
            self.table_col_type_dict[tb_name] = col_type_dict
            self.table_col_index_dict[tb_name] = col_idx_dict
            self.table_index_dict[tb_name] = i_tb
            i_tb += 1
        pass

    # find table index by it's name
    def table_index(self, table_name):
        if not type(table_name) == str:
            raise ValueError
        if self.table_index_dict.__contains__(table_name):
            return self.table_index_dict[table_name]
        else:
            raise ValueError

    def num_column(self, table_name):
        return len(self.table_col_order_dict[table_name]) - 1

    def column_index(self, table_name, col_name):
        if not type(col_name) == str:
            raise TypeError
        if self.table_col_index_dict.__contains__(table_name):
            col_index_dict = self.table_col_index_dict[table_name]
            if col_index_dict.__contains__(col_name):
                return col_index_dict[col_name]
            else:
                raise ValueError
        else:
            raise ValueError

    def column_type(self, table_name, col_name):
        if not type(col_name) == str:
            raise TypeError
        if not self.table_col_type_dict.__contains__(table_name):
            raise TypeError
        if not self.table_col_type_dict[table_name].__contains__(col_name):
            raise TypeError
        return self.table_col_type_dict[table_name][col_name]

    # pack req to send buf
    # return the next offset
    def pack_request_to_sendbuf(self, cmd, tb_index, offset=0):
        struct.pack_into("!ii", self.send_buf, offset, cmd, tb_index)
        offset += struct.calcsize("!ii")
        return offset

    # pack values as a row to buf
    # also check value type
    # based on a table_cols template
    #    for example: cols = ("type", str), ("balance", float)
    #                 values = ("normal", 3.334 )
    # return the next offset start
    def pack_row_to_sendbuf(self, table_name, offset, values):
        # start from 1
        cols = self.table_col_order_dict[table_name][1:]
        count = len(cols)
        buf = self.send_buf
        # first pack the col count
        struct.pack_into("!i", buf, offset, count)
        offset += struct.calcsize("!i")
        # then pack row values
        for i in range(count):
            col_type_code = self.column_type(table_name, cols[i])
            value = values[i]
            # value type check is done by pack_value
            offset = pack_value(buf, offset, col_type_code, value)
        return offset

    # unpack row save result to value
    def unpack_row(self, row_buf, offset):
        i_bytes_cnt = struct.calcsize('!i')
        i_fmt = "!i"
        row_sz = struct.unpack_from(i_fmt, row_buf, offset)[0]
        offset += i_bytes_cnt
        values = []
        for i in range(row_sz):
            col_type_code = struct.unpack_from(i_fmt, row_buf, offset)[0]
            offset += i_bytes_cnt
            buf_sz = struct.unpack_from(i_fmt, row_buf, offset)[0]
            offset += i_bytes_cnt
            values.append(unpack_value_from(col_type_code, row_buf, offset, buf_sz))
            offset += buf_sz
        return values

    # function for debugging
    def print_send_buf(self, len):
        l = []
        for i in range(len):
            l.append(self.send_buf[i])
        print(l)

    # Connect to the database.
    #   host: str, host name
    #   port: int, port number.
    def connect(self, host, port):
        self.connection = socket.socket()
        self.connection.connect((host, port))

    def send_request(self, req_len):
        # sending request
        # print("sending...")
        # print("req len is {}".format(req_len))
        # print(self.send_buf[0:28])
        # print(struct.unpack("!f", self.send_buf[24:28])[0])
        self.connection.send(self.send_buf.raw[0:req_len])
        pass

    # wait and check response head
    # if success return response body to caller
    # otherwise it will raise exception accordingly
    def recv_check_response(self):
        # print("Receiving...")
        recv_bytes = self.connection.recv(4096)
        if recv_bytes is None:
            raise ConnectionError
        i_fmt = "!i"
        i_bytes_cnt = struct.calcsize("!i")
        res_code = struct.unpack_from(i_fmt, recv_bytes, 0)[0]
        if res_code is None:
            raise ConnectionError
        if res_code == RES_OK:
            # return rec body
            return recv_bytes[i_bytes_cnt:]
        if res_code == RES_NOT_FOUND:
            raise ObjectDoesNotExist
        elif res_code == RES_BAD_FOREIGN:
            raise InvalidReference
        elif res_code == RES_TXN_ABORT:
            raise TransactionAbort
        else:
            raise PacketError
        pass

    # Close the connection to the database.
    def close(self):
        send_len = self.pack_request_to_sendbuf(CMD_EXIT, 1, 0)
        self.send_request(send_len)

    # Make the database to add a new row to a database table.
    #   table_name: str, name of the table
    #   values: sequence, the new row to insert to the table
    #   ("User", ["Jay", "Sung", 5.5, 31])
    #   {
    #     {CMD_INSERT, 1},
    #     4,
    #     {
    #       {
    #         fil
    #       }
    #     }
    #   }
    def insert(self, table_name, values):
        tb_idx = self.table_index(table_name)
        offset = self.pack_request_to_sendbuf(CMD_INSERT, tb_idx, 0)
        if len(values) != self.num_column(table_name):
            raise ValueError
        # error checking is done here
        offset = self.pack_row_to_sendbuf(table_name, offset, values)
        self.send_request(offset)
        res_body = self.recv_check_response()
        l_fmt = "!q"
        l_bytes_cnt = struct.calcsize(l_fmt)
        pos = 0
        pk = struct.unpack_from(l_fmt, res_body, pos)[0]
        pos += l_bytes_cnt
        version = struct.unpack_from(l_fmt, res_body, pos)[0]
        return pk, version

    # Make the database to update an existing row in a table.
    #   table_name: str, name of the table
    #   pk: int, row ID
    #   values: sequence, the new row to update to the table
    #   version: int, version of the row
    def update(self, table_name, pk, values, version=0):
        # same as insert, need check table name
        # and values len
        if not type(pk) == int:
            raise TypeError
        if version is not None and not type(version) == int:
            raise TypeError
        if version is None:
            version = 0
        # get table index and check table name
        tb_idx = self.table_index(table_name)
        cols = self.table_col_type_dict[table_name]
        if len(values) != len(cols) - 1:
            raise ValueError
        offset = self.pack_request_to_sendbuf(CMD_UPDATE, tb_idx, 0)
        # pack into key and version
        struct.pack_into("!qq", self.send_buf, offset, pk, version)
        offset += struct.calcsize("!qq")
        offset = self.pack_row_to_sendbuf(table_name, offset, values)
        # perform atomic update if possible
        self.send_request(offset)
        res_body = self.recv_check_response()
        new_version = struct.unpack_from("!q", res_body)[0]
        return new_version

    # Make the database to delete a row in table.
    #   table_name: str, name of the table
    #   pk: int, row ID
    def drop(self, table_name, pk):
        if pk is None or not type(pk) == int:
            raise TypeError
        tb_idx = self.table_index(table_name)
        offset = self.pack_request_to_sendbuf(CMD_DROP, tb_idx, 0)
        id_fmt = "!q"
        struct.pack_into(id_fmt, self.send_buf, offset, pk)
        offset += struct.calcsize(id_fmt)
        self.send_request(offset)
        self.recv_check_response()
        pass

    # Make the database to retrieve a row from a table, which requires 
    # specifying the id of the row.
    #   table_name: str, name of the table
    #   pk: int, row ID
    def get(self, table_name, pk):
        # same as insert, need check table name
        # and values len
        if not type(pk) == int:
            raise TypeError
        tb_idx = self.table_index(table_name)

        offset = self.pack_request_to_sendbuf(CMD_GET, tb_idx, 0)
        id_fmt = "!q"
        id_bytes_cnt = struct.calcsize(id_fmt)
        struct.pack_into(id_fmt, self.send_buf, offset, pk)
        offset += id_bytes_cnt
        self.send_request(offset)
        res_body = self.recv_check_response()
        offset = 0
        version = struct.unpack_from(id_fmt, res_body, offset)[0]
        offset += id_bytes_cnt
        values = self.unpack_row(res_body, offset)
        return values, version

    # Make the database to compare a column of every row in a table against 
    # a value and returns the id of all rows that matched.
    #   table_name: str, name of the table
    #   query: tuple, a tuple of 3 elements: name of column, the operator, 
    #          and the right operand, respectively
    # ("firstName", OP_GT, "hahaha")
    def scan(self, table_name, query):
        # check argument
        if not type(query) == tuple:
            raise TypeError
        if not len(query) == 3:
            raise ValueError
        if not type(query[1]) == int:
            raise TypeError
        if not query[1] in range(1, 5):
            raise ValueError

        tb_idx = self.table_index(table_name)
        col_idx = self.column_index(table_name, query[0])
        col_type_code = self.column_type(table_name, query[0])
        check_col_type(col_type_code, query[2])
        # check if op is supported for current type
        if query[1] not in supported_op_dict[col_type_code]:
            raise ValueError
        # all ok
        offset = self.pack_request_to_sendbuf(CMD_SCAN, tb_idx, 0)
        struct.pack_into("!ii", self.send_buf, offset, col_idx, query[1])
        offset += struct.calcsize("!ii")
        offset = pack_value(self.send_buf, offset, col_type_code, query[2])
        self.send_request(offset)
        res_body = self.recv_check_response()
        offset = 0
        cnt = struct.unpack_from("!i", res_body, offset)[0]
        pks = []
        offset += struct.calcsize("!i")
        id_fmt = "!q"
        id_bytes_cnt = struct.calcsize(id_fmt)
        for i in range(cnt):
            pk = struct.unpack_from(id_fmt, res_body, offset)[0]
            offset += id_bytes_cnt
            pks.append(pk)
        return pks

