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
 def test_functions_calls_and_returns_emit_canonical_ir(self):
  with tempfile.TemporaryDirectory() as d:
   d=Path(d);b=d/"cukc";built=self.build(b);self.assertEqual(built.returncode,0,built.stderr)
   source='jancuk\nfungsi tambah(a, b)\n    balek a + b\nselesai fungsi\nhedeh tambah(20, 22)\nselesai jancuk\n'
   src=d/"function.cuk";src.write_text(source,encoding="utf-8")
   out=subprocess.run([str(b),str(src)],capture_output=True,text=True,timeout=5);self.assertEqual(out.returncode,0,out.stderr)
   doc=json.loads(out.stdout)
   from compiler.ir import validate,from_source
   validate(doc);canonical=from_source(source,"function.cuk")
   self.assertEqual(doc["program"],canonical["program"])
   self.assertEqual(doc["source_map"],canonical["source_map"])
   self.assertEqual(doc["features"],canonical["features"])
 def test_if_else_and_nested_if_emit_canonical_ir(self):
  with tempfile.TemporaryDirectory() as d:
   d=Path(d);b=d/"cukc";built=self.build(b);self.assertEqual(built.returncode,0,built.stderr)
   source=("jancuk\n"
           "njir 1 < 2\n"
           "    hedeh 7\n"
           "kampret\n"
           "    njir 2 < 3\n"
           "        hedeh 8\n"
           "    selesai njir\n"
           "selesai njir\n"
           "selesai jancuk\n")
   src=d/"conditional.cuk";src.write_text(source,encoding="utf-8")
   out=subprocess.run([str(b),str(src)],capture_output=True,text=True,timeout=5)
   self.assertEqual(out.returncode,0,out.stderr)
   doc=json.loads(out.stdout)
   from compiler.ir import validate,from_source
   validate(doc);canonical=from_source(source,"conditional.cuk")
   self.assertEqual(doc["program"],canonical["program"])
   self.assertEqual(doc["source_map"],canonical["source_map"])
   self.assertEqual(doc["features"],canonical["features"])
   self.assertIn("control-flow",doc["features"])
 def test_checked_in_cuk_frontend_runs_on_native_c_runtime(self):
  with tempfile.TemporaryDirectory() as d:
   d=Path(d);binary=d/"pusingcuk-native"
   built=subprocess.run([CC,"-std=c11","-O2","-Wall","-Wextra","-Wno-misleading-indentation","native/pusingcuk.c","-lm","-o",str(binary)],cwd=ROOT,text=True,capture_output=True,timeout=60)
   self.assertEqual(built.returncode,0,built.stderr)
   compiler=d/"compiler_combined.cuk"
   compiler_source=(ROOT/"examples/self_hosting/compiler.cuk").read_text(encoding="utf-8").rsplit("selesai jancuk",1)[0]
   driver_source=(ROOT/"examples/self_hosting/compiler_driver.cuk").read_text(encoding="utf-8")
   compiler.write_text(compiler_source+driver_source+"selesai jancuk\\n",encoding="utf-8")
   source=("jancuk\n"
           "lah data = [1, 2, 3]\n"
           "data[1] = 7\n"
           "lah mapping = {\"value\": data[1]}\n"
           "fungsi pilih(a)\n"
           "    njir a > 0\n"
           "        balek mapping[\"value\"]\n"
           "    kampret\n"
           "        balek 0\n"
           "    selesai njir\n"
           "selesai fungsi\n"
           "hedeh pilih(1)\n"
           "selesai jancuk\n")
   payload=json.dumps({"source_name":"native-selfhost-probe.cuk","source":source},ensure_ascii=False,separators=(",",":"))+"\n"
   out=subprocess.run([str(binary),str(compiler)],input=payload,capture_output=True,text=True,timeout=60)
   self.assertEqual(out.returncode,0,out.stderr)
   lines=out.stdout.splitlines()
   self.assertTrue(lines, "native .cuk frontend emitted no IR")
   doc=json.loads(lines[-1])
   from compiler.ir import validate,from_source
   validate(doc)
   canonical=from_source(source,"native-selfhost-probe.cuk")
   self.assertEqual(doc["program"],canonical["program"])
   self.assertEqual(doc["source_map"],canonical["source_map"])
   self.assertEqual(doc["features"],canonical["features"])
 def test_unsupported_syntax_fails_closed(self):
  with tempfile.TemporaryDirectory() as d:
   d=Path(d);b=d/"cukc";built=self.build(b);self.assertEqual(built.returncode,0,built.stderr)
   src=d/"bad.cuk";src.write_text("jancuk\nuntuk i dalam [1]\n    hedeh 1\nselesai untuk\nselesai jancuk\n",encoding="utf-8")
   out=subprocess.run([str(b),str(src)],capture_output=True,text=True,timeout=5);self.assertNotEqual(out.returncode,0);self.assertEqual(out.stdout,"")
if __name__=="__main__":unittest.main()
