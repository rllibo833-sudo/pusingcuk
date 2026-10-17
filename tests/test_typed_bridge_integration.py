import importlib.util, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,ROOT/path); mod=importlib.util.module_from_spec(spec); sys.modules[name]=mod; spec.loader.exec_module(mod); return mod
BRIDGE=load("typed_cuk_bridge","apps/accounting/platform_bridge.py")
class TypedBridgeIntegrationTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory()
  self.bridge,self.store=BRIDGE.create_sqlite_bridge(Path(self.tmp.name)/"db.sqlite")
  self.store.seed_account("cash","Kas")
  self.store.seed_account("capital","Modal","credit")
  self.store.seed_period("p1","2026-01-01","2026-12-31")
 def tearDown(self): self.store.close(); self.tmp.cleanup()
 def req(self,op,payload):
  return {"contract_version":BRIDGE.CONTRACT_VERSION,"request_id":"evt-1","operation":op,"input":payload}
 def test_frontend_style_typed_event_saves_then_posts_atomic_journal(self):
  saved=self.bridge.dispatch(self.req("db.save_journal_draft",{"entry_id":"e1","date":"2026-10-17","description":"Setoran","lines":[
   {"account_id":"cash","debit":2500,"credit":0},{"account_id":"capital","debit":0,"credit":2500}]}))
  self.assertEqual(saved["status"],"succeeded")
  posted=self.bridge.dispatch(self.req("db.post_journal",{"entry_id":"e1","idempotency_key":"evt-post-1"}))
  self.assertEqual(posted["status"],"succeeded"); self.assertEqual(posted["result"]["total_credit"],2500)
  self.assertEqual([e["event_type"] for e in self.store.audit_trail("e1")],["journal.draft_saved","journal.posted"])
 def test_typed_contract_rejects_extra_and_missing_payload_fields(self):
  bad=self.bridge.dispatch(self.req("db.post_journal",{"entry_id":"e1","idempotency_key":"k","sql":"drop"}))
  self.assertEqual(bad["diagnostic"]["code"],"INVALID_INPUT_FIELDS")
  bad=self.bridge.dispatch(self.req("db.post_journal",{"entry_id":"e1"}))
  self.assertEqual(bad["diagnostic"]["code"],"MISSING_INPUT_FIELDS")
 def test_post_event_rejects_unbalanced_without_mutating_status(self):
  self.bridge.dispatch(self.req("db.save_journal_draft",{"entry_id":"e2","date":"2026-10-17","description":"Tidak seimbang","lines":[
   {"account_id":"cash","debit":100,"credit":0},{"account_id":"capital","debit":0,"credit":99}]}))
  result=self.bridge.dispatch(self.req("db.post_journal",{"entry_id":"e2","idempotency_key":"k2"}))
  self.assertEqual(result["status"],"rejected")
  self.assertEqual(self.store.db.execute("SELECT status FROM journal_entries WHERE id='e2'").fetchone()[0],"draft")
if __name__=="__main__": unittest.main()
