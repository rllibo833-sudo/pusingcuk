import importlib.util, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("cuk_sqlite_store",ROOT/"apps/accounting/sqlite_store.py")
STORE=importlib.util.module_from_spec(SPEC); sys.modules[SPEC.name]=STORE; SPEC.loader.exec_module(STORE)

class SQLiteStoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.store=STORE.CukAccountSQLite(Path(self.tmp.name)/"books.sqlite")
        self.store.seed_account("cash","Kas","debit")
        self.store.seed_account("capital","Modal","credit")
        self.store.seed_period("2026-01","2026-01-01","2026-12-31",True)
    def tearDown(self):
        self.store.close(); self.tmp.cleanup()
    def draft(self, debit=100, credit=100, date="2026-10-17"):
        return self.store.save_journal_draft({"entry_id":"j1","date":date,"description":"Setoran modal","lines":[
          {"account_id":"cash","debit":debit,"credit":0},{"account_id":"capital","debit":0,"credit":credit}]})
    def test_posting_is_atomic_and_audited(self):
        self.draft()
        result=self.store.post_journal({"entry_id":"j1","idempotency_key":"post-j1"})
        self.assertEqual(result["status"],"posted")
        self.assertEqual(result["total_debit"],100)
        self.assertEqual([e["event_type"] for e in self.store.audit_trail("j1")],["journal.draft_saved","journal.posted"])
    def test_unbalanced_posting_keeps_draft_and_no_post_audit(self):
        self.draft(100,99)
        with self.assertRaises(STORE.StorageError): self.store.post_journal({"entry_id":"j1","idempotency_key":"post-j1"})
        self.assertEqual(self.store.db.execute("SELECT status FROM journal_entries WHERE id='j1'").fetchone()[0],"draft")
        self.assertEqual(len(self.store.audit_trail("j1")),1)
    def test_closed_period_rejects_posting_atomically(self):
        self.draft()
        self.store.close_period({"period_id":"2026-01","reason":"tutup"})
        with self.assertRaises(STORE.StorageError) as caught: self.store.post_journal({"entry_id":"j1","idempotency_key":"post-j1"})
        self.assertEqual(caught.exception.code,"PERIOD_CLOSED")
        self.assertEqual(self.store.db.execute("SELECT status FROM journal_entries WHERE id='j1'").fetchone()[0],"draft")
    def test_idempotent_retry_does_not_duplicate_audit(self):
        self.draft(); self.store.post_journal({"entry_id":"j1","idempotency_key":"post-j1"})
        again=self.store.post_journal({"entry_id":"j1","idempotency_key":"post-j1"})
        self.assertTrue(again["idempotent_replay"])
        self.assertEqual(len(self.store.audit_trail("j1")),2)
    def test_integer_only_money_and_inactive_or_unknown_accounts_rejected(self):
        with self.assertRaises(STORE.StorageError): self.draft(True,100)
        with self.assertRaises(STORE.StorageError):
            self.store.save_journal_draft({"entry_id":"j2","date":"2026-10-17","description":"bad","lines":[
             {"account_id":"missing","debit":1,"credit":0}]})
    def test_ledger_only_includes_posted_lines_and_running_balance(self):
        self.draft(); self.store.post_journal({"entry_id":"j1","idempotency_key":"post-j1"})
        result=self.store.get_general_ledger({"account_id":"cash"})
        self.assertEqual(result["ending_balance"],100)
        self.assertEqual(result["lines"][0]["running_balance"],100)
    def test_audit_trail_is_append_only(self):
        self.draft()
        with self.assertRaises(Exception):
            self.store.db.execute("UPDATE audit_events SET details_json='{}' WHERE entity_id='j1'")
        with self.assertRaises(Exception):
            self.store.db.execute("DELETE FROM audit_events WHERE entity_id='j1'")
    def test_failed_draft_insert_rolls_back_entry_and_partial_lines(self):
        with self.assertRaises(STORE.StorageError):
            self.store.save_journal_draft({"entry_id":"bad","date":"2026-10-17","description":"bad","lines":[
             {"account_id":"cash","debit":1,"credit":0},{"account_id":"missing","debit":0,"credit":1}]})
        self.assertIsNone(self.store.db.execute("SELECT id FROM journal_entries WHERE id='bad'").fetchone())
        self.assertEqual(self.store.audit_trail("bad"),[])

if __name__=="__main__": unittest.main()
