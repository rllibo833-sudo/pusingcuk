"""SQLite persistence adapter for CukAccount's typed platform bridge.

All money is integer Rupiah. Posting and audit insertion share one SQLite
transaction. This is a local reference adapter; production Android packaging
must supply a platform-native storage host.
"""
from __future__ import annotations
import json
import sqlite3
import uuid
from pathlib import Path
from typing import Any

class StorageError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code

SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS accounts (
 id TEXT PRIMARY KEY, name TEXT NOT NULL, normal_balance TEXT NOT NULL
   CHECK(normal_balance IN ('debit','credit')), active INTEGER NOT NULL DEFAULT 1
   CHECK(active IN (0,1))
);
CREATE TABLE IF NOT EXISTS periods (
 id TEXT PRIMARY KEY, starts_on TEXT NOT NULL, ends_on TEXT NOT NULL,
 is_open INTEGER NOT NULL DEFAULT 1 CHECK(is_open IN (0,1)),
 CHECK(starts_on <= ends_on)
);
CREATE TABLE IF NOT EXISTS journal_entries (
 id TEXT PRIMARY KEY, entry_date TEXT NOT NULL, description TEXT NOT NULL,
 status TEXT NOT NULL CHECK(status IN ('draft','posted')),
 idempotency_key TEXT UNIQUE, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 posted_at TEXT
);
CREATE TABLE IF NOT EXISTS journal_lines (
 id INTEGER PRIMARY KEY AUTOINCREMENT, entry_id TEXT NOT NULL REFERENCES journal_entries(id),
 line_no INTEGER NOT NULL, account_id TEXT NOT NULL REFERENCES accounts(id),
 description TEXT NOT NULL DEFAULT '', debit INTEGER NOT NULL DEFAULT 0 CHECK(debit >= 0),
 credit INTEGER NOT NULL DEFAULT 0 CHECK(credit >= 0),
 CHECK((debit > 0 AND credit = 0) OR (credit > 0 AND debit = 0)),
 UNIQUE(entry_id,line_no)
);
CREATE TABLE IF NOT EXISTS audit_events (
 id INTEGER PRIMARY KEY AUTOINCREMENT, event_id TEXT NOT NULL UNIQUE,
 event_type TEXT NOT NULL, entity_type TEXT NOT NULL, entity_id TEXT NOT NULL,
 occurred_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, details_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_journal_date_status ON journal_entries(status,entry_date);
CREATE INDEX IF NOT EXISTS idx_lines_entry ON journal_lines(entry_id,line_no);
CREATE INDEX IF NOT EXISTS idx_audit_entity ON audit_events(entity_type,entity_id,id);
CREATE TRIGGER IF NOT EXISTS audit_no_update BEFORE UPDATE ON audit_events
BEGIN SELECT RAISE(ABORT,'audit trail is append-only'); END;
CREATE TRIGGER IF NOT EXISTS audit_no_delete BEFORE DELETE ON audit_events
BEGIN SELECT RAISE(ABORT,'audit trail is append-only'); END;
"""

def _text(value: Any, field: str, max_len: int = 240) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > max_len:
        raise StorageError("INVALID_FIELD", f"{field} wajib berupa teks 1-{max_len} karakter.")
    return value.strip()

def _money(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0 or value > 9_000_000_000_000_000:
        raise StorageError("INVALID_MONEY", f"{field} harus integer Rupiah non-negatif.")
    return value

class CukAccountSQLite:
    def __init__(self, database: str | Path):
        self.path = str(database)
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.path, isolation_level=None, timeout=10)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.execute("PRAGMA busy_timeout=10000")
        self.db.executescript(SCHEMA)

    def close(self):
        self.db.close()

    def _audit(self, event_type: str, entity_type: str, entity_id: str, details: dict):
        self.db.execute(
            "INSERT INTO audit_events(event_id,event_type,entity_type,entity_id,details_json) VALUES(?,?,?,?,?)",
            (str(uuid.uuid4()), event_type, entity_type, entity_id,
             json.dumps(details, ensure_ascii=False, sort_keys=True, separators=(",", ":"))),
        )

    def seed_account(self, account_id: str, name: str, normal_balance: str = "debit"):
        if normal_balance not in ("debit", "credit"):
            raise StorageError("INVALID_ACCOUNT", "Saldo normal harus debit atau credit.")
        with self.db:
            self.db.execute("INSERT INTO accounts(id,name,normal_balance) VALUES(?,?,?)",
                            (_text(account_id,"account_id",80),_text(name,"name"),normal_balance))

    def seed_period(self, period_id: str, starts_on: str, ends_on: str, is_open: bool = True):
        _text(starts_on,"starts_on",10); _text(ends_on,"ends_on",10)
        if starts_on > ends_on: raise StorageError("INVALID_PERIOD","Tanggal mulai melewati tanggal akhir.")
        with self.db:
            self.db.execute("INSERT INTO periods(id,starts_on,ends_on,is_open) VALUES(?,?,?,?)",
                            (_text(period_id,"period_id",80),starts_on,ends_on,int(is_open)))

    def save_journal_draft(self, payload: dict) -> dict:
        entry_id = _text(payload.get("entry_id") or str(uuid.uuid4()), "entry_id", 80)
        date = _text(payload.get("date"), "date", 10)
        desc = _text(payload.get("description"), "description")
        lines = payload.get("lines")
        if not isinstance(lines,list) or not lines: raise StorageError("INVALID_LINES","Baris jurnal wajib berupa daftar.")
        self.db.execute("BEGIN IMMEDIATE")
        try:
            self.db.execute("INSERT INTO journal_entries(id,entry_date,description,status,idempotency_key) VALUES(?,?,?,'draft',?)",
                            (entry_id,date,desc,payload.get("idempotency_key")))
            for i,line in enumerate(lines,1):
                self._insert_line(entry_id,i,line)
            self._audit("journal.draft_saved","journal",entry_id,{"line_count":len(lines),"date":date})
            self.db.execute("COMMIT")
        except Exception:
            if self.db.in_transaction: self.db.execute("ROLLBACK")
            raise
        return {"entry_id":entry_id,"status":"draft","line_count":len(lines)}

    def _insert_line(self, entry_id: str, line_no: int, line: Any):
        if not isinstance(line,dict) or set(line) - {"account_id","description","debit","credit"}:
            raise StorageError("INVALID_LINE","Bentuk baris jurnal tidak valid.")
        account_id = _text(line.get("account_id"),"account_id",80)
        account = self.db.execute("SELECT active FROM accounts WHERE id=?",(account_id,)).fetchone()
        if account is None or not account["active"]: raise StorageError("ACCOUNT_INVALID","Akun tidak ada atau tidak aktif.")
        debit,credit = _money(line.get("debit",0),"debit"),_money(line.get("credit",0),"credit")
        if (debit > 0) == (credit > 0): raise StorageError("INVALID_LINE_AMOUNT","Setiap baris harus debit atau kredit saja.")
        self.db.execute("INSERT INTO journal_lines(entry_id,line_no,account_id,description,debit,credit) VALUES(?,?,?,?,?,?)",
                        (entry_id,line_no,account_id,str(line.get("description",""))[:240],debit,credit))

    def post_journal(self, payload: dict) -> dict:
        entry_id = _text(payload.get("entry_id"),"entry_id",80)
        idem = _text(payload.get("idempotency_key"),"idempotency_key",128)
        try:
            self.db.execute("BEGIN IMMEDIATE")
            existing = self.db.execute("SELECT id,status FROM journal_entries WHERE idempotency_key=?",(idem,)).fetchone()
            if existing and existing["status"] == "posted":
                self.db.execute("COMMIT")
                return {"entry_id":existing["id"],"status":"posted","idempotent_replay":True}
            entry = self.db.execute("SELECT * FROM journal_entries WHERE id=?",(entry_id,)).fetchone()
            if entry is None or entry["status"] != "draft": raise StorageError("DRAFT_NOT_FOUND","Draft tidak ditemukan atau sudah diposting.")
            period = self.db.execute("SELECT * FROM periods WHERE starts_on<=? AND ends_on>=? ORDER BY starts_on DESC LIMIT 1",
                                     (entry["entry_date"],entry["entry_date"])).fetchone()
            if period is None or not period["is_open"]: raise StorageError("PERIOD_CLOSED","Tidak ada periode terbuka untuk tanggal jurnal.")
            totals = self.db.execute("SELECT COUNT(*) n,COALESCE(SUM(debit),0) d,COALESCE(SUM(credit),0) c FROM journal_lines WHERE entry_id=?",(entry_id,)).fetchone()
            if totals["n"] < 2: raise StorageError("MINIMUM_LINES","Jurnal harus memiliki minimal dua baris.")
            if totals["d"] <= 0 or totals["c"] <= 0 or totals["d"] != totals["c"]:
                raise StorageError("JOURNAL_UNBALANCED","Total debit dan kredit harus sama dan lebih dari nol.")
            self.db.execute("UPDATE journal_entries SET status='posted',posted_at=CURRENT_TIMESTAMP,idempotency_key=? WHERE id=?",(idem,entry_id))
            self._audit("journal.posted","journal",entry_id,{"period_id":period["id"],"line_count":totals["n"],"debit":totals["d"],"credit":totals["c"],"idempotency_key":idem})
            self.db.execute("COMMIT")
            return {"entry_id":entry_id,"status":"posted","total_debit":totals["d"],"total_credit":totals["c"],"idempotent_replay":False}
        except Exception:
            if self.db.in_transaction: self.db.execute("ROLLBACK")
            raise

    def query_accounts(self, payload: dict | None = None) -> dict:
        rows = self.db.execute("SELECT id,name,normal_balance,active FROM accounts ORDER BY name").fetchall()
        return {"accounts":[dict(r) for r in rows]}

    def get_general_ledger(self, payload: dict) -> dict:
        account_id = _text(payload.get("account_id"),"account_id",80)
        rows = self.db.execute("""SELECT e.id entry_id,e.entry_date,e.description,l.line_no,l.description line_description,
          l.debit,l.credit FROM journal_lines l JOIN journal_entries e ON e.id=l.entry_id
          WHERE e.status='posted' AND l.account_id=? AND (?='' OR e.entry_date>=?)
          AND (?='' OR e.entry_date<=?) ORDER BY e.entry_date,e.id,l.line_no""",
          (account_id,payload.get("start_date",""),payload.get("start_date",""),payload.get("end_date",""),payload.get("end_date",""))).fetchall()
        balance=0; result=[]
        for row in rows:
            item=dict(row); balance += item["debit"]-item["credit"]; item["running_balance"]=balance; result.append(item)
        return {"account_id":account_id,"lines":result,"ending_balance":balance}

    def close_period(self, payload: dict) -> dict:
        period_id = _text(payload.get("period_id"),"period_id",80)
        reason = _text(payload.get("reason"),"reason")
        self.db.execute("BEGIN IMMEDIATE")
        try:
            period=self.db.execute("SELECT * FROM periods WHERE id=?",(period_id,)).fetchone()
            if period is None: raise StorageError("PERIOD_NOT_FOUND","Periode tidak ditemukan.")
            if not period["is_open"]:
                self.db.execute("COMMIT")
                return {"period_id":period_id,"status":"closed","already_closed":True}
            self.db.execute("UPDATE periods SET is_open=0 WHERE id=?",(period_id,))
            self._audit("period.closed","period",period_id,{"reason":reason,"starts_on":period["starts_on"],"ends_on":period["ends_on"]})
            self.db.execute("COMMIT")
        except Exception:
            if self.db.in_transaction: self.db.execute("ROLLBACK")
            raise
        return {"period_id":period_id,"status":"closed","already_closed":False}

    def audit_trail(self, entity_id: str | None = None) -> list[dict]:
        if entity_id:
            rows=self.db.execute("SELECT * FROM audit_events WHERE entity_id=? ORDER BY id",(entity_id,)).fetchall()
        else: rows=self.db.execute("SELECT * FROM audit_events ORDER BY id").fetchall()
        return [dict(r) for r in rows]
