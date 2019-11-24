import struct

MAX_INT = 2147483647
MAX_LONG = 2**63 - 1 # easydb crashes...
MAX_LONG = MAX_INT
ERROR_MSGS = [None, "OK", "NOT_FOUND", "BAD_TABLE", "BAD_QUERY",
                  "TXN_ABORT", "BAD_VALUE", "BAD_ROW", "BAD_REQUEST",
                  "BAD_FOREIGN", "UNIMPLEMENTED"]

def is_foreign(column_type):
    return type(column_type) is str

##################
##  PRIMITIVES  ##
##################

# Singletons

def read_int(bstrm):
    assert len(bstrm) == 4
    return struct.unpack(">i", bstrm)[0]

def read_long(bstrm):
    assert len(bstrm) == 8
    return struct.unpack(">q", bstrm)[0]

def read_str(bstrm):
    return bstrm.decode("utf-8").rstrip("\x00")

def read_float(bstrm):
    assert len(bstrm) == 4
    return struct.unpack(">f", bstrm)[0]

def read_double(bstrm):
    assert len(bstrm) == 8
    return struct.unpack(">d", bstrm)[0]

read_foreign = read_long

# Streams

def next_int(bstrm):
    return read_int(bstrm[:4]), bstrm[4:]

def next_long(bstrm):
    return read_long(bstrm[:8]), bstrm[8:]

def next_str(bstrm, str_len):
    return read_str(bstrm[:str_len]), bstrm[str_len]

def next_float(bstrm):
    return read_float(bstrm[:4]), bstrm[4:]

def next_double(bstrm):
    return read_double(bstrm[:8]), bstrm[8:]

next_foreign = next_long

# Generators

def make_int(value):
    assert type(value) is int
    return struct.pack(">i", value)

def make_long(value):
    assert type(value) is int
    return struct.pack(">q", value)

def make_str(value):
    assert type(value) is str
    buffer_size = 4*((len(value)-1)//4 + 1) # align to 4 bytes
    # automatic padding using \x00
    return struct.pack(">{}s".format(buffer_size), value.encode("utf-8"))

def make_float(value):
    assert type(value) in (int, float)
    return struct.pack(">f", float(value))

def make_double(value):
    assert type(value) in (int, float)
    return struct.pack(">d", float(value))

make_foreign = make_long


######################
##  EASYDB READERS  ##
######################

READERS = [None, read_long, read_double, read_str, read_foreign]

def assert_consumed(f):
    def helper(*args, **kwargs):
        result, bstrm = f(*args, **kwargs)
        assert len(bstrm) == 0, "{} -> {}".format(bstrm, len(bstrm)) # bstrm should have been exhausted
        return result
    return helper

def next_response(bstrm):
    error_code, bstrm = next_int(bstrm)
    return ERROR_MSGS[error_code], bstrm

def next_key(bstrm):
    pk, bstrm = next_pk(bstrm)
    ver, bstrm = next_version(bstrm)
    return (pk, ver), bstrm

next_pk = next_long
next_version = next_long

def next_value(bstrm):
    val_enum, bstrm = next_int(bstrm)
    size, bstrm = next_int(bstrm)
    value, bstrm = READERS[val_enum](bstrm[:size]), bstrm[size:]
    return value, bstrm

def next_row(bstrm):
    count, bstrm = next_int(bstrm)
    values = []
    for i in range(count):
        value, bstrm = next_value(bstrm)
        values.append(value)
    return tuple(values), bstrm

def next_ids(bstrm):
    count, bstrm = next_int(bstrm)
    ids = []
    for i in range(count):
        row_id, bstrm = next_long(bstrm)
        ids.append(row_id)
    return list(ids), bstrm

read_response = assert_consumed(next_response)
read_key = assert_consumed(next_key)
read_pk = assert_consumed(next_pk)
read_version = assert_consumed(next_version)
read_value = assert_consumed(next_value)
read_row = assert_consumed(next_row)
read_ids = assert_consumed(next_ids)


#########################
##  EASYDB STRUCTURES  ##
#########################

MAKERS = [None, make_long, make_double, make_str, make_foreign]

def REQUEST(cmd, table_num):
    cmds = [None, "INSERT", "UPDATE", "DROP", "GET", "SCAN", "EXIT"]
    assert type(table_num) is int
    #assert 1 <= table_num <= MAX_INT # not exposed to user
    assert cmd in cmds[1:]
    return make_int(cmds.index(cmd)) + make_int(table_num)

def VALUE(value, expct_type=None):
    # Type checking
    if expct_type is not None: # ignore type checking otherwise
        if is_foreign(expct_type): # foreign, str is name to Table
            if type(value) is not int:
                raise ValueError("`{}` is not a valid foreign key reference.".format(value))
            #assert 1 <= value <= MAX_LONG # not exposed to user
        elif expct_type is float:
            if type(value) not in (int, float):
                raise ValueError("`{}` is not a valid float.".format(value))
            value = float(value) # cast int to float
        elif type(value) is not expct_type: # str, int
            raise ValueError("`{}` is not a valid {}".format(value, expct_type))

    # Determine enumeration value
    val_enum = 4 if is_foreign(expct_type) else [None, int, float, str].index(type(value))
    size = 8 if val_enum != 3 else 4*((len(value)-1)//4 + 1) # 4-byte aligned strings
    return make_int(val_enum) + make_int(size) + MAKERS[val_enum](value)

def ROW(values, expct_types=None):
    bstrm = make_int(len(values))
    for i, value in enumerate(values):
        bstrm += VALUE(value, expct_types[i] if expct_types is not None else None)
    return bstrm

def KEY(pk, ver):
    return ID(pk) + VERSION(ver)

ID = make_long
VERSION = make_long
COLUMN = make_int
OPERATOR = make_int
