# CS50-Final-Project
My final CS50 project

command to acticate virtual enviroment: 
    source "/Users/miguellopes/Documents/Software Enginiring/FraughtCow/.venv/bin/activate"

comand to run flask
    flask --app app run --debug

New DB designe: 

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
    username TEXT NOT NULL UNIQUE, 
    hash TEXT NOT NULL
);

CREATE TABLE accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
    user_id INTEGER NOT NULL,
    account_name TEXT NOT NULL,
    balance_cents INTEGER NOT NULL DEFAULT 0,
    UNIQUE (user_id, account_name),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    created_by_user_id INTEGER,
    account_id INTEGER NOT NULL,
    trans_type TEXT NOT NULL CHECK (trans_type IN ('income','expense','transfer_in', 'transfer_out')),
    category TEXT NOT NULL,
    amount_cents INTEGER NOT NULL CHECK (amount_cents > 0),
    trans_date TEXT NOT NULL DEFAULT CURRENT_DATE,
    date_created TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    FOREIGN KEY (created_by_user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
);

CREATE TABLE account_permissions (
    user_id INTEGER NOT NULL,
    account_id INTEGER NOT NULL,
    perm_type INTEGER NOT NULL CHECK (perm_type IN (0,1,2)),
    PRIMARY KEY (user_id, account_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
);

CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    UNIQUE(user_id, name),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
