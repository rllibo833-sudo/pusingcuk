import importlib.util, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("diagnostic_repair_loop",ROOT/"tools/diagnostic_repair_loop.py")
DIAG=importlib.util.module_from_spec(SPEC); sys.modules[SPEC.name]=DIAG; SPEC.loader.exec_module(DIAG)
class DiagnosticRepairLoopTests(unittest.TestCase):
 def test_compiler_runtime_fixture_and_hash_are_reproducible(self):
  source=ROOT/"apps/accounting/cukaccount_backend.cuk"
  expected=(ROOT/"apps/accounting/cukaccount_backend.expected.txt").read_text(encoding="utf-8").splitlines()
  result=DIAG.run_case(source,expected)
  self.assertEqual(result["status"],"passed",result)
  self.assertEqual(len(result["source_sha256"]),64)
 def test_output_mismatch_produces_manual_only_repair_hint(self):
  result=DIAG.run_case(ROOT/"apps/accounting/cukaccount_backend.cuk",["wrong"])
  self.assertEqual(result["code"],"OUTPUT_MISMATCH")
  self.assertFalse(result["repair"]["automatic_apply"])
  self.assertEqual(result["repair"]["risk"],"manual_review")
 def test_syntax_error_does_not_apply_patch(self):
  import tempfile
  with tempfile.TemporaryDirectory(dir=ROOT) as d:
   p=Path(d)/"broken.cuk"; p.write_text("jancuk\nthis is invalid\nselesai jancuk\n",encoding="utf-8")
   result=DIAG.run_case(p)
   self.assertEqual(result["code"],"SYNTAX")
   self.assertFalse(result["repair"]["automatic_apply"])
 def test_outside_repository_and_non_cuk_sources_rejected(self):
  import tempfile
  with tempfile.TemporaryDirectory() as d:
   result=DIAG.run_case(Path(d)/"x.cuk")
   self.assertEqual(result["code"],"SOURCE_OUTSIDE_REPOSITORY")
 def test_fixture_manifest_schema_is_checked(self):
  result=DIAG.evaluate_fixtures([{"id":"bad","source":"apps/accounting/cukaccount_backend.cuk","expected":["ok"],"apply_patch":True}])
  self.assertEqual(result["failed"],1)
  self.assertEqual(result["results"][0]["code"],"INVALID_FIXTURE_SCHEMA")
if __name__=="__main__": unittest.main()
