# Assignment 3

## Assignment requirements

1. `easydb.py`: Implement Database class for communication
2. `table.py`: Implement Table class and associated metaclass
3. `fields.py`: Implement types supported by ORM layer
4. `__init__.py`: Implement `setup` and `export` functions

See the section on [Solution requirements](http://fs.csl.toronto.edu/~sunk/asst3.html#specification) for detailed writeup. Summary of details below.

### Notes

+ Python `struct` library [documentation](https://docs.python.org/3.6/library/struct.html)
+ Python `socket` library [documentation](https://docs.python.org/3.6/library/socket.html?highlight=socket#module-socket)
+ Geographic coordinates [instructions](https://en.wikipedia.org/wiki/Geographic_coordinate_system)
+ Release to be tagged as `Asst3-end`
---

## ORM API specification

### 1. `orm/easydb.py`

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

### 2. `orm/table.py`

```python
import orm

##############
##  TASK 5  ##
##############

# Implement orm.Table from which tables inherit
# Column names start with letters, cannot use underscores
# Each column presented with an instance of either:
# - String / Integer / Float / Foreign
#
# Note: Schema from `schema.py`

class User(orm.Table):
    firstName = orm.String(blank=True)
    lastName = orm.String(blank=True)
    height = orm.Float(blank=True)
    age = orm.Integer(blank=True)

    def __repr__(self):
        return "<User: %s %s>"%(self.firstName, self.lastName)

class Account(orm.Table):   
    user = orm.Foreign(User)
    type = orm.String(choices=["Savings", "Chequing",], default="Chequing")
    balance = orm.Float(blank=True)

    def __repr__(self):
        return "<Account: %s's %s>"%(self.user.firstName, self.type)
```

### 3. `orm/fields.py`

```python
##############
##  TASK 6  ##
##############

# Implement __init__ for each of the primitive types (fields.py)
# - blank=False: Allows fields to be unspecified when creating objects
#   - Raise attribute error if False and field not specified during object creation
#   - Default value of type will be automatically used for missing fields
# - default: Change default value for type
# - choices: List of allowed values for field
#   - Raise ValueError if field does not have value in choices during insert/update
# - table: Class of referenced table

Integer.__init__(self, blank=False, default=0, choices=())
Float.__init__(self, blank=False, default=0., choices=())
String.__init__(self, blank=False, default="", choices=())
Foreign.__init__(self, table, blank=False) # default missing is None
```

### 4. `orm/__init__.py`

```python
# Implement the interface with the underlying database client

##############
##  TASK 7  ##
##############

# Setup: Return initialized but unconnected database object
# - database_name: name of underlying database, currently only "easydb"
# - module: module name containing the schema (initialization)
orm.setup(database_name, module)

import schema
db = orm.setup("easydb", schema)
db.connect("127.0.0.1", 8080)


##############
##  TASK 8  ##
##############

# Export: Return string that can be read by underlying database
# Note that all fields are ignored since they're only enforced
# in the ORM layer
orm.export(database_name, module)

# schema2.py
class Course(orm.Table):
    instructor = orm.Foreign(Person)
    name = orm.String()
    difficulty = orm.Float(default=5.0)
    numEnrolled = orm.Integer(blank=True)

import schema2
fmt = orm.export("easydb", schema2)
"""
Course {
    instructor : Person;
    name : string;
    difficulty : float;
    numEnrolled : integer;
}
"""
```

### 5. `orm/table.py`

```python
import orm

##############
##  TASK 9  ##
##############

# Implement the object interface, i.e. Table instance methods
# When setting field value, do implict type conversion, and
# if not available, throw TypeError
object = Table(db, ...)
joe = User(db, firstName="Joe", lastName="Harris", age=32)

# SAVE: Saves object to database
# - New objects will call insert
# - Existing objects will call update
# - `atomic=True` default param
joe.save(atomic=False)

# DELETE: Deletes object, i.e. drop
joe.delete()

# PK: Object id
# Has value None before it is in the database
joe.pk

# VERSION: Object version
# Has value None before it is in the database
joe.version

# GET: Return existing object from table if exists
# Note that pk and version should already be set
object = Table.get(db, pk)

# FILTER: Return list of objects matching query
# Query arguments are in format `columnname__op=value`
# Supported operators are `ne`, `gt` and `lt`
# Foreign key field can be either object itself or its id
[object...] = Table.filter(db, ...)
results = User.filter(db, age__gt=33)
results = User.filter(db, firstName="Joe") # not needed for equality
results = Account.filter(db, user=joe)
results = Account.filter(db, user=2)

# COUNT: Returns number of matches to given query
# Note that only equality and inequality supported
# Used to check if object exists without fetching entire object
if Table.count(db, pk=2) == 1: pass


## Some hints
# Example usage
joe.pk is None    # True
joe.height == 0.  # True
joe.lastName = "Smith"
joe.save()
joe.pk            # 2 (the id of the object)
joe.version       # 1 (the version of the object)
joe.age = 33
joe.save(atomic=False)    # disable atomic update for this call to easydb.update
joe.version               # 2 (new version of the object)
joe.age = 34
joe.save()                # this will call easydb.update, which may raise TransactionAbort
joe.delete()              # deletes the row from the database
joe.pk is None            # True
joe.save()                #
joe.pk                    # 4 (the new id of the object)

# Foreign key references are converted automatically to their
# objects, either lazily or eagerly.
# Raise InvalidReference if not existing, i.e. server returns BAD_FOREIGN
account = Account.get(db, pk=2)
account.user  # <User: Joe Smith>

# Note that cascaded save is performed, and in reverse order
greg = User(db, firstName="Greg", lastName="Russell", age=27)
account = Account(db, user=greg, type="Chequing", balance=100.0)
account.save()  # will save 'greg' first before saving 'account'
saving = Account(db, user=greg, type="Saving", balance=200.0)
saving.save()   # will not save 'greg' first since it already exists in database

# Type checking is performed during the set attribute, so can use descriptors,
# __getattr__, __getattribute__, or property to implement type checking
account.user = greg             # OK
account.user = 3                # NO - cannot use object id
account.user = User.get(db, 3)  # OK
account.user = None             # NO - blank is not specified for this field
account.user = account2         # NO - incorrect object type (only instance of User accepted)
```

### 6. `orm/fields.py`

```python
###############
##  TASK 10  ##
###############

# Datetime field
# To convert to and from database storage type and
# perform as required type safety checks
# Default value must support calling a function if default is assigned
# a function
# Ignore time zone related settings
# Can use datetime.timestamp() for POSIX timestamp
class Lecture(orm.Table):
    location = orm.String()
    start = orm.DateTime(default=datetime.now)
    end = orm.DateTime()

# main.py
ece326 = Lecture(db, location="BA1190", end=datetime(2019, 10, 15, 13))
ece326.start = datetime(2019, 10, 15, 12)
ece326.save()


###############
##  TASK 11  ##
###############

# Coordinate field
# Coordinates are represented in Python as 2-tuple, and must be
# valid geographic coordinates in latitude and longitude.
# Raise ValueError if invalid coordinate when save or update attempted
# Only need to support equality and inequality operations when queried
# Can store as two native EasyDB fields and use underscore character to avoid conflicts with user-defined column names
class Capital(orm.Table):
    name = orm.String()
    location = orm.Coordinate()

# main.py
ottawa = Capital.filter(db, name="Ottawa")[0]
ottawa.location  # (45.4215, 75.6972)

# Possible implementation
Capital {
    name : string;
    location_lat : float;
    location_lon : float;
}
```

---

## EasyDB API specification

Object-relational mapping is used to abstract database accesses.

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

#### Atomic updates

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

## Testing code

To test the database client, the server needs to be run. A server can be started by running `easydb -g PORT` on one terminal and running the client on a different terminal (`-g` prints everything the database is doing). Loads `default.txt` by default.

A custom script can be written that imports `schema.py` for unit testing, or the program can alternatively be run in interactive mode.

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
