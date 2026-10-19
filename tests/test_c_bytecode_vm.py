#!/usr/bin/env python3
"""Compile a deterministic subset and compare Python/C bytecode VM output."""
import io, json, subprocess, tempfile
from pathlib import Path
from compiler.bytecode import compile_source
from compiler.vm import VirtualMachine
ROOT=Path(__file__).resolve().parents[1]
FIXTURES=[
 ("declare-print", 'bikin angka = 40 + 2\nspill(angka)\n', "42\n"),
 ("branch", 'bikin x = 3\nkalo x > 2:\n    spill("yes")\nkalau:\n    spill("no")\n', "yes\n"),
 ("loop", 'bikin x = 0\nselama x < 3:\n    spill(x)\n    x = x + 1\n', "0\n1\n2\n"),
 ("logic", 'bikin x = bukan salah\nspill(x)\n', "okelah\n"),
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
 print(f"Python/C VM fixtures: {len(FIXTURES)}/{len(FIXTURES)}")
if __name__=="__main__":main()
