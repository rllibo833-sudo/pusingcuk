#!/usr/bin/env python3
"""Compile a deterministic subset and compare Python/C bytecode VM output."""
import io, json, subprocess, tempfile
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from compiler.bytecode import compile_source
from compiler.vm import VirtualMachine
FIXTURES=[
 ("declare-print", 'jancuk\nlah angka = 40 + 2\nhedeh angka\nselesai jancuk\n', "42\n"),
 ("branch", 'jancuk\nlah x = 3\nnjir x > 2\n    hedeh "yes"\nkampret\n    hedeh "no"\nselesai njir\nselesai jancuk\n', "yes\n"),
 ("loop", 'jancuk\nlah x = 0\nmumet x < 3\n    hedeh x\n    x = x + 1\nselesai mumet\nselesai jancuk\n', "0\n1\n2\n"),
 ("logic", 'jancuk\nlah x = bukan salah\nhedeh x\nselesai jancuk\n', "okelah\n"),
 ("list-index", 'jancuk\nlah data = [10, 20, 30]\nhedeh data[1]\nselesai jancuk\n', "20\n"),
]
def main():
 with tempfile.TemporaryDirectory() as td:
  path=Path(td)/"case.json"
  for name,source,expected in FIXTURES:
   bc=compile_source(source,name+".cuk")
   pyout=io.StringIO();VirtualMachine(bc,output_stream=pyout).run()
   assert pyout.getvalue()==expected,(name,"Python VM",repr(pyout.getvalue()),repr(expected))
   path.write_text(json.dumps(bc,ensure_ascii=False),encoding="utf-8")
   c=subprocess.run([str(ROOT/"native"/"cuk-bytecode-vm"),str(path)],capture_output=True,text=True)
   assert c.returncode==0,(name,c.stderr)
   assert c.stdout==pyout.getvalue(),(name,"C VM",repr(c.stdout),repr(pyout.getvalue()))
   print("PASS",name)
  invalid_cases = [
   ("malformed-json", "{"),
   ("unknown-opcode", json.dumps({"format":"pusingcuk-bytecode","bytecode_version":1,"language_version":"0.6-dev","source_name":"bad.cuk","functions":{},"code":[["NOT_REAL",None,1]]})),
   ("bad-jump", json.dumps({"format":"pusingcuk-bytecode","bytecode_version":1,"language_version":"0.6-dev","source_name":"bad.cuk","functions":{},"code":[["JUMP",999,1]]})),
   ("step-limit", json.dumps({"format":"pusingcuk-bytecode","bytecode_version":1,"language_version":"0.6-dev","source_name":"loop.cuk","functions":{},"code":[["JUMP",0,1]]})),
  ]
  for name,payload in invalid_cases:
   path.write_text(payload,encoding="utf-8")
   c=subprocess.run([str(ROOT/"native"/"cuk-bytecode-vm"),str(path)],capture_output=True,text=True)
   assert c.returncode != 0,(name,"invalid bytecode unexpectedly accepted")
   print("PASS reject",name)
 print(f"Python/C VM fixtures: {len(FIXTURES)}/{len(FIXTURES)}; invalid-input checks: {len(invalid_cases)}")
if __name__=="__main__":main()
