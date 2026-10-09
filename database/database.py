import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

try:
    DATABASE_URL = str(
        st.secrets.get("DATABASE_URL", "")
    ).strip()
except Exception:
    DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
IS_POSTGRES = DATABASE_URL.startswith(("postgresql://", "postgres://"))

if IS_POSTGRES:
    import psycopg
    from psycopg.rows import dict_row
else:
    DB_PATH = Path(os.getenv("SQLITE_PATH", "data/expenses.db"))
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def _pg_dsn():
    return DATABASE_URL.replace("postgres://", "postgresql://", 1)

@contextmanager
def get_conn():
    if IS_POSTGRES:
        conn = psycopg.connect(_pg_dsn(), row_factory=dict_row)
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

def execute(sql, params=(), fetch=False, many=False):
    # Keep SQL parameterized. Convert common PostgreSQL placeholders.
    if IS_POSTGRES:
        sql = sql.replace("?", "%s")
    with get_conn() as conn:
        cur = conn.cursor()
        if many:
            cur.executemany(sql, params)
        else:
            cur.execute(sql, params)
        if fetch:
            return cur.fetchall()
        return cur.lastrowid if not IS_POSTGRES else None

def init_db():
    with get_conn() as conn:
        cur = conn.cursor()
        statements = [
        """CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            name TEXT NOT NULL, email TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL,
            college TEXT, phone TEXT, monthly_budget REAL DEFAULT 0,
            monthly_savings_goal REAL DEFAULT 0, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_admin INTEGER DEFAULT 0
        )""",
        """CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            user_id INTEGER NOT NULL, type TEXT NOT NULL CHECK(type IN ('income','expense')),
            amount REAL NOT NULL CHECK(amount > 0), category TEXT, subcategory TEXT,
            date TEXT NOT NULL, payment_method TEXT, description TEXT, location TEXT,
            notes TEXT, trip_id INTEGER, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )""",
        """CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            user_id INTEGER NOT NULL, name TEXT NOT NULL, parent TEXT,
            UNIQUE(user_id, name), FOREIGN KEY(user_id) REFERENCES users(id)
        )""",
        """CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            user_id INTEGER NOT NULL, category TEXT NOT NULL, amount REAL NOT NULL,
            month TEXT NOT NULL, UNIQUE(user_id, category, month),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )""",
        """CREATE TABLE IF NOT EXISTS savings_goals (
            id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            user_id INTEGER NOT NULL, name TEXT NOT NULL, target_amount REAL NOT NULL,
            current_amount REAL DEFAULT 0, target_date TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )""",
        """CREATE TABLE IF NOT EXISTS recurring_expenses (
            id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            user_id INTEGER NOT NULL, name TEXT NOT NULL, amount REAL NOT NULL,
            frequency TEXT NOT NULL, next_payment_date TEXT NOT NULL, category TEXT,
            active INTEGER DEFAULT 1, FOREIGN KEY(user_id) REFERENCES users(id)
        )""",
        """CREATE TABLE IF NOT EXISTS trips (
            id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            user_id INTEGER NOT NULL, name TEXT NOT NULL, start_date TEXT, end_date TEXT,
            budget REAL DEFAULT 0, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )""",
        """CREATE TABLE IF NOT EXISTS trip_expenses (
            id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            user_id INTEGER NOT NULL, trip_id INTEGER NOT NULL, category TEXT,
            amount REAL NOT NULL, date TEXT NOT NULL, description TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id), FOREIGN KEY(trip_id) REFERENCES trips(id)
        )""",
        """CREATE TABLE IF NOT EXISTS ai_insights (
            id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            user_id INTEGER NOT NULL, insight TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )"""
        ]
        for s in statements:
            if not IS_POSTGRES:
                s = s.replace("INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY", "INTEGER PRIMARY KEY AUTOINCREMENT")
            cur.execute(s)

def insert_and_get_id(sql, params=()):
    if IS_POSTGRES:
        sql = sql.replace("?", "%s")
        if "RETURNING" not in sql.upper():
            sql += " RETURNING id"
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute(sql, params)
            return cur.fetchone()["id"]
    return execute(sql, params)

def query(sql, params=()):
    return execute(sql, params, fetch=True)
