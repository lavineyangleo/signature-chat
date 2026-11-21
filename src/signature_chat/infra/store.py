import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path


class Store:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.database = self.root / 'studio.sqlite3'
        with self.connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS turns (id TEXT PRIMARY KEY, session TEXT NOT NULL, message TEXT NOT NULL, status TEXT NOT NULL, created TEXT NOT NULL, metadata TEXT NOT NULL, error TEXT NOT NULL)')
            db.execute("UPDATE turns SET status='interrupted', error='服务曾中断，结果未知；未自动重试。' WHERE status='running'")

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.database, timeout=10)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    def rows(self, session=None):
        with self.connect() as db:
            result = db.execute('SELECT * FROM turns' + (' WHERE session=?' if session else '') + ' ORDER BY rowid', (session,) if session else ()).fetchall()
        return [{**dict(row), 'metadata': json.loads(row['metadata'])} for row in result]

    def add(self, key, session, message):
        with self.connect() as db:
            db.execute('INSERT INTO turns VALUES (?,?,?,?,?,?,?)',
                       (key, session, message, 'running', datetime.now(timezone.utc).isoformat(), '{}', ''))

    def finish(self, key, status, metadata=None, error=''):
        with self.connect() as db:
            db.execute('UPDATE turns SET status=?,metadata=?,error=? WHERE id=?',
                       (status, json.dumps(metadata or {}), error, key))
