"""Native compiler integration: assignments survive IR serialization."""
import json, os, shutil, subprocess, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CC=os.environ.get("CC") or shutil.which("cc") or shutil.which("gcc") or shutil.which("clang")
@unittest.skipUnless(CC,"C compiler unavailable")
class NativeAssignmentTests(unittest.TestCase):
 def test_assignment_emits_canonical_assign_node(self):
  with tempfile.TemporaryDirectory() as d:
   d=Path(d);b=d/"cukc";cmd=[CC,"-std=c11","-O2","-Wall","-Wextra","-Werror","-Wno-misleading-indentation","native/pusingcuk_bootstrap.c","native/cuk_lexer.c","native/cuk_parser.c","native/cuk_ir.c","-o",str(b)]
   built=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,timeout=30);self.assertEqual(built.returncode,0,built.stderr)
   src=d/"assign.cuk";src.write_text("jancuk\nlah angka = 1\nangka = angka + 2\nhedeh angka\nselesai jancuk\n",encoding="utf-8")
   run=subprocess.run([str(b),str(src)],cwd=ROOT,text=True,capture_output=True,timeout=5);self.assertEqual(run.returncode,0,run.stderr)
   doc=json.loads(run.stdout);from compiler.ir import from_source,validate
   validate(doc);canonical=from_source(src.read_text(encoding="utf-8"),"assign.cuk")
   self.assertEqual(doc["program"],canonical["program"]);self.assertEqual(doc["source_map"],canonical["source_map"]);self.assertEqual(doc["features"],canonical["features"])
