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
    if !db.tables.contains_key(&table_id) {
        return Err(Response::BAD_TABLE);
    }
    let table = db.tables.get(&table_id).unwrap(); // borrow as immutable first

    let table_cols = &table.info.t_cols;
    if table_cols.len() != values.len() {
        return Err(Response::BAD_ROW);
    }

    // Type checking
    for (i, col) in table_cols.iter().enumerate() {
        let column = &table_cols[i];
        let value_type = match values.get(i).unwrap() {
            Value::Null => Value::NULL,
            Value::Integer(_) => Value::INTEGER,
            Value::Float(_) => Value::FLOAT,
            Value::Text(_) => Value::STRING,
            Value::Foreign(v) => {
                if !db.tables.contains_key(&column.c_ref) {
                    return Err(Response::BAD_FOREIGN);
                }
                let target_table = db.tables.get(&column.c_ref).unwrap();

                if !target_table.data.contains_key(&v) {
                    return Err(Response::BAD_FOREIGN);
                }
                Value::FOREIGN
            }
        };
        if value_type != Value::NULL {
            if value_type != column.c_type {
                return Err(Response::BAD_VALUE);
            }
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
    if !db.tables.contains_key(&table_id) {
        return Err(Response::BAD_TABLE);
    }
    let table = db.tables.get(&table_id).unwrap(); // borrow as immutable first

    let table_cols = &table.info.t_cols;
    if table_cols.len() != values.len() {
        return Err(Response::BAD_ROW);
    }

    // Type checking
    for (i, col) in table_cols.iter().enumerate() {
        let column = &table_cols[i];
        let value_type = match values.get(i).unwrap() {
            Value::Null => Value::NULL,
            Value::Integer(_) => Value::INTEGER,
            Value::Float(_) => Value::FLOAT,
            Value::Text(_) => Value::STRING,
            Value::Foreign(v) => {
                if !db.tables.contains_key(&column.c_ref) {
                    return Err(Response::BAD_FOREIGN);
                }
                let target_table = db.tables.get(&column.c_ref).unwrap();

                if !target_table.data.contains_key(&v) {
                    return Err(Response::BAD_FOREIGN);
                }
                Value::FOREIGN
            }
        };
        if value_type != Value::NULL {
            if value_type != column.c_type {
                return Err(Response::BAD_VALUE);
            }
        }
    }

    if !table.data.contains_key(&object_id) {
        return Err(Response::NOT_FOUND);
    }
    let row = table.data.get(&object_id).unwrap();

    if version != 0 {
        if row.version != version {
            return Err(Response::TXN_ABORT);
        }
    }
    let new_version = row.version + 1;

    // Process data
    let mut table = db.tables.get_mut(&table_id).unwrap(); // borrow as mutable
    table.data.remove(&object_id);
    table.data.insert(object_id, Row {
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
    if !db.tables.contains_key(&table_id) {
        return Err(Response::BAD_TABLE);
    }
    let table = db.tables.get(&table_id).unwrap(); // borrow as immutable first


    if !table.data.contains_key(&object_id) {
        return Err(Response::NOT_FOUND);
    }
    let row = table.data.get(&object_id).unwrap();

    // Cascade drop!
    let mut collect_ref = vec![];
    let mut collect_pk = vec![];
    for (next_table_id, next_table) in &db.tables {
        let table_cols = &next_table.info.t_cols;
        for (next_row_id, next_row) in &next_table.data {
            for i in 0..table_cols.len() {
                let pk = match next_row.values[i] {
                    Value::Foreign(pk) => pk,
                    _ => -1
                };
                let ref_id = table_cols[i].c_ref;
                if (ref_id == table_id) & (pk == object_id) {
                    collect_ref.push(*next_table_id);
                    collect_pk.push(*next_row_id);
                }
            }
        }
    }
    for i in 0..collect_ref.len() {
        handle_drop(db, collect_ref[i], collect_pk[i]);
    }


    let mut table = db.tables.get_mut(&table_id).unwrap(); // borrow as mutable
    table.data.remove(&object_id);


    let r = Response::Drop;
    Ok(r)
}

fn handle_get(db: & Database, table_id: i32, object_id: i64)
    -> Result<Response, i32>
{
    if !db.tables.contains_key(&table_id) {
        return Err(Response::BAD_TABLE);
    }
    let table = db.tables.get(&table_id).unwrap(); // borrow as immutable first

    if !table.data.contains_key(&object_id) {
        return Err(Response::NOT_FOUND);
    }
    let row = table.data.get(&object_id).unwrap();

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
