# Assignment 4

## Assignment requirements

1. `database.rs`: Implement request handlers
2. `server.rs`: Enable concurrency

See the section on [Solution requirements](http://fs.csl.toronto.edu/~sunk/asst4.html#specification) for detailed writeup. Summary of details below.

## Program overview

### database.rs
Defines database structure and implements response handlers.

```rust
pub struct Database { }
pub fn handle_request(request: Request, db: & mut Database)
```

Matches to `handle_insert`, `handle_update`, `handle_drop`, `handle_get`, `handle_query`. To be implemented.

### packet.rs
Includes definitions for `Value`, `Command`, `Request`, `Response`. Fully implemented.

```rust
pub enum Value
pub enum Command
pub enum Response<'a>

pub struct Request {
    pub table_id : i32,
    pub command : Command,
}

impl Value             // const: NULL, INTEGER
impl Request           // const: INSERT, UPDATE, ...
impl Response<'_>      // const: OK, NOT_FOUND, ...

struct ByteArray {
    buffer: Vec<u8>,
    pointer: usize,
    strlen: usize,
}

impl ByteArray {
    const MAX_PACKET_SIZE : usize = 16384;

    pub fn new() -> Self
    fn read_size(& mut self) -> io::Result<i32>
    fn read_fixed(& mut self) -> io::Result<i32> // 8 bytes
    fn read_zero(& mut self) -> io::Result<i32>
    fn read_value(&mut self) -> io::Result<Value> { // size then value

    fn underfull(& self, size: usize) -> bool
    fn from(buf: & [u8; ByteArray::MAX_PACKET_SIZE]) -> Self

    fn write(&mut self, value: &i32)
    fn write(&mut self, value: &i64)
    fn write(&mut self, value: &u64)
    fn write(&mut self, value: &f64)
    fn write(&mut self, value: &[u8])
    fn write(&mut self, value: &str)
    fn write(&mut self, value: &String)

    fn from_raw(&mut self) -> i32
    fn from_raw(&mut self) -> i64
    fn from_raw(&mut self) -> f64
    fn from_raw(&mut self) -> String

    fn size(&self) -> usize
    fn size(&self) -> usize
    fn size(&self) -> usize
    fn size(& self) -> usize
}

pub trait Network : io::Write + io::Read {
    fn receive(&mut self) -> io::Result<Request>
    fn respond(&mut self, resp: &Response) -> io::Result<usize>
}
```

### schema.rs
Provides column and table structures, as well as other parsers, to read schema from file. Already fully implemented.

```rust
pub struct Column {
    pub c_name: String, /* column name */
    pub c_id: i32,      /* column id */
    pub c_type: i32,    /* one of 4 native types */
    pub c_ref: i32,     /* table id */
}

pub struct Table {
    pub t_name: String,
    pub t_id: i32,
    pub t_cols: Vec<Column>,
}

impl Column {
    fn type_as_str(& self) -> String
}
```

### server.rs
Implements event handlers and runs database on server.

```rust
fn single_threaded(listener: TcpListener, table_schema: Vec<Table>, verbose: bool)
fn multi_threaded(listener: TcpListener, table_schema: Vec<Table>, verbose: bool)
```

Calls `mut db = Database { }` and loops `handle_connection(stream, &mut db)`.

```rust
pub fn run_server(table_schema: Vec<Table>, ip_address: String, verbose: bool) // Wrapper to `single_threaded`
fn handle_connection(mut stream: TcpStream, db: & mut Database)
    -> io::Result<()> // receive and reply
```

Calls `stream.respond(database::handle_request(request, db))?` in normal loop. Terminates if `let Command::Exit = request.command`.

### main.rs
Same database as in assignment 3. Triggers `server::run_server`.
