"""Integration checks for the native source-to-IR compiler."""
import json, os, shutil, subprocess, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CC=os.environ.get("CC") or shutil.which("cc") or shutil.which("gcc") or shutil.which("clang")
@unittest.skipUnless(CC,"C compiler unavailable")
class NativeBootstrapTests(unittest.TestCase):
 def build(self,binary):
  return subprocess.run([CC,"-std=c11","-O2","-Wall","-Wextra","-Werror","-Wno-misleading-indentation","native/pusingcuk_bootstrap.c","native/cuk_lexer.c","native/cuk_parser.c","native/cuk_ir.c","-o",str(binary)],cwd=ROOT,text=True,capture_output=True,timeout=30)
 def test_native_compiler_emits_canonical_ir(self):
  with tempfile.TemporaryDirectory() as d:
   d=Path(d);b=d/"cukc";built=self.build(b);self.assertEqual(built.returncode,0,built.stderr)
   src=d/"hello.cuk";src.write_text('jancuk\nlah nama = "Dunia"\nhedeh "Halo, " + nama\nselesai jancuk\n',encoding="utf-8")
   out=subprocess.run([str(b),str(src)],capture_output=True,text=True,timeout=5);self.assertEqual(out.returncode,0,out.stderr)
   doc=json.loads(out.stdout);from compiler.ir import validate,from_source
   validate(doc);canonical=from_source(src.read_text(encoding="utf-8"),"hello.cuk")
   self.assertEqual(doc["program"],canonical["program"]);self.assertEqual(doc["source_map"],canonical["source_map"]);self.assertEqual(doc["features"],canonical["features"])
 def test_operator_precedence_and_parentheses(self):
  with tempfile.TemporaryDirectory() as d:
   d=Path(d);b=d/"cukc";built=self.build(b);self.assertEqual(built.returncode,0,built.stderr)
   src=d/"math.cuk";src.write_text("jancuk\nhedeh (2 + 3) * 4 - 6 / 2\nselesai jancuk\n",encoding="utf-8")
   out=subprocess.run([str(b),str(src)],capture_output=True,text=True,timeout=5);self.assertEqual(out.returncode,0,out.stderr)
   doc=json.loads(out.stdout);from compiler.ir import validate;validate(doc)
   self.assertEqual(doc["program"]["fields"]["body"][0]["fields"]["value"]["fields"]["op"],"-")
 def test_unsupported_syntax_fails_closed(self):
  with tempfile.TemporaryDirectory() as d:
   d=Path(d);b=d/"cukc";built=self.build(b);self.assertEqual(built.returncode,0,built.stderr)
   src=d/"bad.cuk";src.write_text("jancuk\nfungsi sapa()\nselesai jancuk\n",encoding="utf-8")
   out=subprocess.run([str(b),str(src)],capture_output=True,text=True,timeout=5);self.assertNotEqual(out.returncode,0);self.assertEqual(out.stdout,"")
if __name__=="__main__":unittest.main()
