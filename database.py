# backend/database.py
import sqlite3

DB_PATH = "usuarios_extratos.db"

def get_db():
    """Abre conexão com o banco SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
