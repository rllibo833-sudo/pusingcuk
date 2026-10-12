"""Confined SQLite adapter for local, offline-first development."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from threading import RLock


class DatabaseAdapterError(RuntimeError):
    """Database access or policy failure."""


class LocalDatabase:
    """SQLite file confined to a chosen workspace; no network or extension loading."""

    MAX_SQL_BYTES = 65_536

    def __init__(self, workspace: str | Path, filename: str = "pusingcuk.sqlite3"):
        self.workspace = Path(workspace).resolve()
        if not filename or Path(filename).is_absolute() or Path(filename).name != filename:
            raise DatabaseAdapterError("nama database harus berupa nama file lokal")
        if filename in (".", ".."):
            raise DatabaseAdapterError("nama database tidak valid")
        self.path = (self.workspace / filename).resolve()
        if self.path.parent != self.workspace:
            raise DatabaseAdapterError("database harus berada di dalam workspace")
        self._connection = None
        self._lock = RLock()
        self._transaction = False

    @staticmethod
    def _authorize(action, arg1, arg2, database, trigger):
        denied = {
            getattr(sqlite3, "SQLITE_ATTACH", -1),
            getattr(sqlite3, "SQLITE_DETACH", -2),
            getattr(sqlite3, "SQLITE_PRAGMA", -3),
            getattr(sqlite3, "SQLITE_CREATE_VTABLE", -4),
            getattr(sqlite3, "SQLITE_DROP_VTABLE", -5),
        }
        if action in denied:
            return sqlite3.SQLITE_DENY
        if action == getattr(sqlite3, "SQLITE_FUNCTION", -6):
            function = (arg2 or arg1 or "").lower()
            if function in {"load_extension", "readfile", "writefile"}:
                return sqlite3.SQLITE_DENY
        return sqlite3.SQLITE_OK

    def _connect(self):
        if self._connection is None:
            self.workspace.mkdir(parents=True, exist_ok=True)
            resolved = self.path.resolve()
            if resolved.parent != self.workspace:
                raise DatabaseAdapterError("jalur database keluar dari workspace")
            try:
                connection = sqlite3.connect(
                    str(resolved), timeout=2.0, isolation_level=None,
                    check_same_thread=False,
                )
                # Set trusted connection defaults before installing the restrictive authorizer.
                connection.execute("PRAGMA foreign_keys = ON")
                connection.set_authorizer(self._authorize)
            except (sqlite3.Error, OSError) as exc:
                raise DatabaseAdapterError(f"gagal membuka database lokal: {exc}") from exc
            self._connection = connection
        return self._connection

    def execute(self, sql: str, params=()):
        if not isinstance(sql, str) or not sql.strip():
            raise DatabaseAdapterError("SQL harus berupa teks yang tidak kosong")
        if len(sql.encode("utf-8")) > self.MAX_SQL_BYTES:
            raise DatabaseAdapterError("SQL melewati batas ukuran")
        if not isinstance(params, (tuple, list)):
            raise DatabaseAdapterError("parameter SQL harus berupa tuple atau list")
        with self._lock:
            try:
                return self._connect().execute(sql, tuple(params))
            except (sqlite3.Error, UnicodeError) as exc:
                raise DatabaseAdapterError(f"query database ditolak/gagal: {exc}") from exc

    def query(self, sql: str, params=()):
        cursor = self.execute(sql, params)
        return cursor.fetchall()

    def transaction(self):
        return _Transaction(self)

    def close(self):
        with self._lock:
            if self._connection is not None:
                self._connection.close()
                self._connection = None
                self._transaction = False

    def __enter__(self):
        self._connect()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()


class _Transaction:
    def __init__(self, database: LocalDatabase):
        self.database = database

    def __enter__(self):
        db = self.database
        db._lock.acquire()
        try:
            connection = db._connect()
            if db._transaction:
                raise DatabaseAdapterError("nested transaction belum didukung")
            connection.execute("BEGIN")
            db._transaction = True
            return db
        except Exception:
            db._lock.release()
            raise

    def __exit__(self, exc_type, exc, tb):
        db = self.database
        try:
            if db._connection is not None and db._transaction:
                db._connection.execute("ROLLBACK" if exc_type else "COMMIT")
                db._transaction = False
        finally:
            db._lock.release()
        return False
