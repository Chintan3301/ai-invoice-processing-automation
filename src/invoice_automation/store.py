from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

SCHEMA = """
CREATE TABLE IF NOT EXISTS invoices (
    id TEXT PRIMARY KEY, source_filename TEXT NOT NULL, invoice_number TEXT, supplier_name TEXT,
    purchase_order TEXT, invoice_total TEXT, tax TEXT, currency TEXT NOT NULL,
    confidence_invoice_number REAL NOT NULL, confidence_supplier_name REAL NOT NULL,
    confidence_invoice_total REAL NOT NULL, duplicate_key TEXT NOT NULL, status TEXT NOT NULL,
    route TEXT NOT NULL, approval_stage TEXT, reason TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_invoices_duplicate_key ON invoices(duplicate_key);
CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(status);
"""

class InvoiceStore:
    def __init__(self, path: str | Path = "invoice-demo.db") -> None:
        self.path = str(path); self._init_db()
    def _connect(self):
        conn = sqlite3.connect(self.path); conn.row_factory = sqlite3.Row; return conn
    def _init_db(self):
        with self._connect() as conn: conn.executescript(SCHEMA)
    def duplicate_keys(self):
        with self._connect() as conn: rows = conn.execute("SELECT duplicate_key FROM invoices WHERE status <> 'Duplicate'").fetchall()
        return [row["duplicate_key"] for row in rows]
    def insert(self, record: dict[str, Any]):
        columns = ", ".join(record.keys()); placeholders = ", ".join("?" for _ in record)
        with self._connect() as conn: conn.execute(f"INSERT INTO invoices ({columns}) VALUES ({placeholders})", tuple(record.values()))
    def get(self, record_id: str):
        with self._connect() as conn: row = conn.execute("SELECT * FROM invoices WHERE id = ?", (record_id,)).fetchone()
        return dict(row) if row else None
    def list(self, status: str | None = None):
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM invoices WHERE status = ? ORDER BY created_at DESC", (status,)).fetchall() if status else conn.execute("SELECT * FROM invoices ORDER BY created_at DESC").fetchall()
        return [dict(row) for row in rows]
    def update(self, record_id: str, changes: dict[str, Any]):
        if not changes: return
        assignments = ", ".join(f"{column} = ?" for column in changes); values = [*changes.values(), record_id]
        with self._connect() as conn: conn.execute(f"UPDATE invoices SET {assignments} WHERE id = ?", values)
