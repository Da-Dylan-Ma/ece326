/*
 * database.rs
 *
 * Implementation of EasyDB database internals
 *
 * University of Toronto
 * 2019
 */

use packet::{Command, Request, Response, Value};
use schema::Table as STable;
use std::collections::HashMap;


/* OP codes for the query command */
pub const OP_AL: i32 = 0;
pub const OP_EQ: i32 = 1;
pub const OP_NE: i32 = 2;
pub const OP_LT: i32 = 3;
pub const OP_GT: i32 = 4;
pub const OP_LE: i32 = 5;
pub const OP_GE: i32 = 6;


pub struct Database {
    pub tables: HashMap<i32, Table>,
}

pub struct Table {
    pub info: STable,
    pub data: HashMap<i64, Row>,
    pub count: i64,
}

pub struct Row {
    pub version: i64,
    pub values: Vec<Value>
}

impl Database {
    pub fn new(schema_tables: Vec<STable>) -> Database {
        let mut construct = HashMap::new();
        let mut counter: i32 = 1;
        for entry in schema_tables {
            construct.insert(counter, Table {
                info: entry,
                data: HashMap::new(),
                count: 0,
            });
            counter += 1;
        }
        Database {
            tables: construct,
        }
    }
}

/* Receive the request packet from client and send a response back */
pub fn handle_request(request: Request, db: & mut Database)
    -> Response
{
    /* Handle a valid request */
    let result = match request.command {
        Command::Insert(values) =>
            handle_insert(db, request.table_id, values),
        Command::Update(id, version, values) =>
             handle_update(db, request.table_id, id, version, values),
        Command::Drop(id) => handle_drop(db, request.table_id, id),
        Command::Get(id) => handle_get(db, request.table_id, id),
        Command::Query(column_id, operator, value) =>
            handle_query(db, request.table_id, column_id, operator, value),
        /* should never get here */
        Command::Exit => Err(Response::UNIMPLEMENTED),
    };

    /* Send back a response */
    match result {
        Ok(response) => response,
        Err(code) => Response::Error(code),
    }
}

/*
 * TODO: Implment these EasyDB functions
 */

fn handle_insert(db: & mut Database, table_id: i32, values: Vec<Value>)
    -> Result<Response, i32>
{
    let table = match db.tables.get(&table_id) { // borrow as immutable first
        Some(table) => table,
        None => return Err(Response::BAD_TABLE),
    };
    let table_cols = &table.info.t_cols;

    // Type checking
    for i in 0..values.len() {
        match table_cols.get(i) {
            Some(column) => {
                let column_type = column.c_type;
                let request_type = match values.get(i).unwrap() {
                    Value::Null => Value::NULL,
                    Value::Integer(_) => Value::INTEGER,
                    Value::Float(_) => Value::FLOAT,
                    Value::Text(_) => Value::STRING,
                    Value::Foreign(v) => {
                        let target_table = db.tables.get(&column.c_ref).unwrap();
                        match target_table.data.get(v) {
                            Some(_) => Value::FOREIGN,
                            None => return Err(Response::BAD_FOREIGN)
                        }
                    }
                };
                if request_type != column_type {
                    return Err(Response::BAD_VALUE)
                }
            },
            None => return Err(Response::BAD_ROW)
        }
    }

    // Process data
    let mut table = db.tables.get_mut(&table_id).unwrap(); // borrow as mutable
    table.count += 1;
    table.data.insert(table.count, Row {
        version: 1,
        values: values,
    });

    let r = Response::Insert(table.count, 1);
    // println!("{:#?}", r);
    Ok(r) // vary id and version
}

fn handle_update(db: & mut Database, table_id: i32, object_id: i64,
    version: i64, values: Vec<Value>) -> Result<Response, i32>
{
    let table = match db.tables.get(&table_id) { // borrow as immutable first
        Some(table) => table,
        None => return Err(Response::BAD_TABLE),
    };
    let table_cols = &table.info.t_cols;

    // Type checking
    for i in 0..values.len() {
        match table_cols.get(i) {
            Some(column) => {
                let column_type = column.c_type;
                let request_type = match values.get(i).unwrap() {
                    Value::Null => Value::NULL,
                    Value::Integer(_) => Value::INTEGER,
                    Value::Float(_) => Value::FLOAT,
                    Value::Text(_) => Value::STRING,
                    Value::Foreign(v) => {
                        let target_table = db.tables.get(&column.c_ref).unwrap();
                        match target_table.data.get(v) {
                            Some(_) => Value::FOREIGN,
                            None => return Err(Response::BAD_FOREIGN)
                        }
                    }
                };
                if request_type != column_type {
                    return Err(Response::BAD_VALUE)
                }
            },
            None => return Err(Response::BAD_ROW)
        }
    }

    let row = match table.data.get(&object_id) {
        Some(row) => row,
        None => return Err(Response::NOT_FOUND),
    };

    if version != 0 {
        if row.version != version {
            return Err(Response::TXN_ABORT)
        }
    }
    let new_version = row.version + 1;

    // Process data
    let mut table = db.tables.get_mut(&table_id).unwrap(); // borrow as mutable
    table.data.remove(&version);
    table.data.insert(table.count, Row {
        version: new_version,
        values: values,
    });

    let r = Response::Update(new_version);
    // println!("{:#?}", r);
    Ok(r) // vary id and version
}

fn handle_drop(db: & mut Database, table_id: i32, object_id: i64)
    -> Result<Response, i32>
{
    Err(Response::UNIMPLEMENTED)
}

fn handle_get(db: & Database, table_id: i32, object_id: i64)
    -> Result<Response, i32>
{
    let table = match db.tables.get(&table_id) { // borrow as immutable first
        Some(table) => table,
        None => return Err(Response::BAD_TABLE),
    };

    let row = match table.data.get(&object_id) {
        Some(row) => row,
        None => return Err(Response::NOT_FOUND),
    };
    let version = row.version;
    let values = &row.values;
    let r = Response::Get(version, &values);

    // println!("{:#?}", r);
    Ok(r)
}

fn handle_query(db: & Database, table_id: i32, column_id: i32,
    operator: i32, other: Value)
    -> Result<Response, i32>
{
    Err(Response::UNIMPLEMENTED)
}
