# Assignment 3

## Assignment requirements

1. `easydb.py`: Implement Database class for communication
2. `table.py`: Implement Table class and associated metaclass
3. `fields.py`: Implement types supported by ORM layer
4. `__init__.py`: Implement `setup` and `export` functions

See the section on (Solution requirements)[http://fs.csl.toronto.edu/~sunk/asst3.html#specification] for detailed writeup.

### Notes

+ Python `struct` library [documentation](https://docs.python.org/3.6/library/struct.html)
+ Python `socket` library [documentation](https://docs.python.org/3.6/library/socket.html?highlight=socket#module-socket)

---

### API specification

#### Schema: `easydb.py`
Creates a Database object. If there is an issue with the provided schema, throw the following errors:
+ `TypeError`: Table name or column not a string
+ `ValueError`: type not one of `str`, `float`, `int` or string referencing another table name
+ `orm.IntegrityError`: Cyclic/Non-existent foreign key reference

```python
import easydb

##############
##  TASK 1  ##
##############

# Initialization: creates a Database object.
# Throw following errors if issues with provided schema:
# - TypeError: Table name or column not a string
# - ValueError: Type not one of `str`, `float`, `int` or string table name
# - orm.IntegrityError: Cyclic/Non-existent foreign key reference
tb = (
    ("User", (                  # table_name
        ("firstName", str),     # (column_name, type)
        ("lastName", str),
        ("height", float),
        ("age", int),
    )),

    ("Account", (
        ("user", "User"),       # (column_name, table_reference)
        ("type", str),
        ("balance", float),
    ))
)
db = easydb.Database(tb)

##############
##  TASK 2  ##
##############

# Connect method
# Accepts hostname and port number, use socket library
# No exception handling in method
db.connect("127.0.0.1", 8080)

##############
##  TASK 3  ##
##############

# Close method: disconnect from server
# Send EXIT command and close socket
db.close()

##############
##  TASK 4  ##
##############

# Implement EasyDB commands
# Throw corresponding error classes:
# - NOT_FOUND -> orm.ObjectDoesNotExist
# - BAD_FOREIGN -> orm.InvalidReference
# - TXN_ABORT -> orm.TransactionAbort
# - BAD_TABLE, BAD_VALUE, BAD_ROW -> orm.PacketError

# INSERT
db.insert(table_name, values)
pk, version = db.insert("User", ["Jay", "Sung", 5.5, 31])

# UPDATE
# Atomic update if version not None
db.update(table_name, pk, values, version=None)
version = db.update("User", 1, ["Jay", "Sung", 5.5, 31])

# DROP
# No return value
db.drop(table_name, pk)
db.drop("User", 1)

# GET
db.get(table_name, pk)
values, version = db.get("User", 1)
print(values) # ['Jay', 'Sung', 5.5, 31]

# SCAN
# Query is 3-tuple
db.scan(table_name, query)
results = db.scan("Account", ("balance", orm.easydb.OP_GT, 10000))
print(results) # [1, 3, 7]
```

#### Model
None

---

## Writeup

Object-relational mapping is used to abstract database accesses, e.g. converting from the first to second form,

```python
# Minimal abstraction - Record object
rec = db.execute("GET 2 FROM User")
if rec.valid(): name = rec["firstName"]

# ORM abstraction - User object
try:
    user = User.get(db, id=2)
    name = user.firstName
except ObjectDoesNotExist:
    pass
```

### Database schema

The database schema (list of table definitions) for EasyDB is as follows, with the value either a type or a table-specifier,
```
table-name {
    column-name-1: type | table-specifier;
    column-name-2: type | table-specifier;
    ...
}
```

Each column in the table can be one of four types: `integer`, `float`, `string`, or foreign key (i.e. pointer to record in another table) which is a 64-bit integer. Since `id` and `pk` are used as object id references in the ORM layer, those cannot be used for column names. EasyDB disallows cyclical references in foreign keys.

### Access protocol

An EasyDB server is accessed via its hostname and port number, and communicates in binary format. The common structures for the EasyDB network packets are defined below using C syntax, 4-bytes aligned, with 32-bit `int` and 64-bit `long` [big-endian](https://en.wikipedia.org/wiki/Endianness#Big-endian) numbers. The table number is in order of definition in the schema, starting from 1.

```cpp
// Requests to server
enum Command {
    INSERT = 1,
    UPDATE = 2,
    DROP = 3,
    GET = 4,
    SCAN = 5,
    EXIT = 6,
};

struct request {
    int command;
    int table;           // table number
};

// Responses from server
enum Code {
    OK = 1,
    NOT_FOUND = 2,       // id not found
    BAD_TABLE = 3,       // table not found
    BAD_QUERY = 4,       // error during scan
    TXN_ABORT = 5,       // update aborted
    BAD_VALUE = 6,       // column value type mismatch
    BAD_ROW = 7,         // number of values is incorrect
    BAD_REQUEST = 8,     // malformed packet
    BAD_FOREIGN = 9,     // foreign key not found
    UNIMPLEMENTED = 10,  // ignore; to be used in asst4
};

struct response {
    int code;
};

enum Type {
    INTEGER = 1,
    FLOAT = 2,
    STRING = 3,
    FOREIGN = 4,
};

struct value {
    int type;
    int size;       // buffer size, 8 bytes (except strings as 4 byte multiples)
    char buf[];     // data
};

struct row {
    int count;      // length of values array
    struct value values[];
};
```

### Atomic updates

Atomic updates provide support for concurrent updates, by matching version numbers of updates and the database row, and modifying the version number after each update.
The atomic update should be put in a loop to retry if `TXN_ABORT` occurs.

```cpp
struct key {
    long id;        // row id
    long version;   // row version
};
```

### Commands

The format of each EasyDB query is stated in the respective header for each command in the format:
`<param1> <param2> ... -> <return1> <return2> ...`

#### INSERT: `request row -> response key`

Used to insert row into table.
The `struct key` only appears if response is `OK`.
+ `BAD_FOREIGN`: Reference to foreign key not found

#### UPDATE: `request key row -> response key.version`

Used to update existing row.
If not using atomic update feature, set `key.version = 0`.
Note that only `key.version` is returned, rather than `key`.
+ `NOT_FOUND`: Row not found
+ `TXN_ABORT`: Atomic update faileds
+ `BAD_FOREIGN`: Reference to foreign key not found

#### DROP: `request key.id -> response`

Used to delete a row in table.
EasyDB performs cascade delete, i.e. rows of other tables referencing the deleted row will also be deleted, to prevent dangling pointers.
+ `NOT_FOUND`: Row not found

#### GET: `request key.id -> request key.version row`

Retrieves a row from table, specified by `key.id`.
+ `NOT_FOUND`: Row not found

#### SCAN: `request column operator value -> response count key.ids[]`

Returns the id of all rows whose column number matches `column` and value matches `value`.
On success, the `int count` is returned along with `long ids[]`.
Column numbers start from 1, with the internal `id` field referenced by 0 with the type `FOREIGN`.
+ `BAD_QUERY`: Either (1) column type and value type mismatch, or (2) operator not supported for given type.

The operator field specifies how the column value is compared against `value`; the enumeration is specified below.
`FOREIGN` fields only support `OP_EQ` and `OP_NE`.
Strings are lexicographically ordered.

```cpp
enum Operator {
    OP_EQ = 1,  // equal
    OP_NE = 2,  // not equal
    OP_LT = 3,  // less than
    OP_GT = 4,  // greater than
};
```

#### EXIT: `request -> NULL`

Graceful shut down of server; no server response.
The preferred value for `request.table` is 1.

---

## Program overview

### schema.py
Includes user-defined tables. Change this to help with testing of ORM layer.

### main.py
Contains the `main` function which allows you to run in interactive mode for testing purposes, or export the currently loaded schema.

### orm/\_\_init\_\_.py
Implement `setup` and `export` functions

### orm/easydb.py
Includes a database client needed to communicate with an EasyDB server. To implement Database class to send and receive packets to and from the server.

### orm/table.py
Definition for database table. To implement the Table class and its associated metaclass

### orm/fields.py
Implement all the fields supported by the ORM layer, including custom fields not natively supported by the underlying database

### orm/exceptions.py
Contains all the exception classes used by the database implementation or the ORM layer. No need to change this file.
