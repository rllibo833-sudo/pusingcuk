"""Compile and execute the explicitly supported C++17 conformance subset."""
import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from compiler.cpp_backend import CppBackendError, generate
from compiler.ir import from_source

ROOT = Path(__file__).resolve().parents[1]
CONF = ROOT / "tests" / "conformance"
CORPUS = json.loads((CONF / "manifest.json").read_text(encoding="utf-8"))
SELECTED = json.loads((CONF / "cpp_manifest.json").read_text(encoding="utf-8"))
BY_ID = {item["id"]: item for item in CORPUS["fixtures"]}


def classify(stderr):
    first = (stderr or "").lstrip().splitlines()[:1]
    if not first:
        return None
    if "Kesalahan runtime:" in first[0]:
        return "runtime_error"
    if "Kesalahan sintaks:" in first[0]:
        return "syntax_error"
    return "error"


def source_line(stderr):
    match = re.search(r"\bBaris\s+(\d+)\b", stderr or "", re.IGNORECASE)
    if not match:
        match = re.search(r"\bbaris\s+(\d+)\b", stderr or "", re.IGNORECASE)
    return int(match.group(1)) if match else None


class CppBackendConformanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.compiler = shutil.which("g++") or shutil.which("c++")
        if not cls.compiler:
            raise RuntimeError("C++ backend conformance requires a C++17 compiler (g++ or c++)")
        if SELECTED.get("schema_version") != 1:
            raise AssertionError("C++ manifest schema_version must be 1")
        if len(SELECTED.get("fixtures", [])) < 40:
            raise AssertionError("C++ backend must declare at least 40 explicit conformance fixtures")
        if len(set(SELECTED["fixtures"])) != len(SELECTED["fixtures"]):
            raise AssertionError("C++ manifest contains duplicate fixture IDs")
        for fixture_id in SELECTED["fixtures"]:
            if fixture_id not in BY_ID:
                raise AssertionError("C++ manifest references unknown fixture: " + fixture_id)

    def test_cpp_backend_matches_pinned_fixture_contract(self):
        with tempfile.TemporaryDirectory(prefix="pusingcuk-cpp-") as temp_name:
            temp = Path(temp_name)
            for fixture_id in SELECTED["fixtures"]:
                with self.subTest(fixture=fixture_id):
                    fixture = BY_ID[fixture_id]
                    source_path = (CONF / fixture["source"]).resolve()
                    self.assertTrue(source_path.is_relative_to(CONF.resolve()), fixture_id)
                    source = source_path.read_text(encoding="utf-8")
                    generated = generate(from_source(source, source_path.name))
                    cpp_path = temp / (fixture_id.replace(".", "_").replace("-", "_") + ".cpp")
                    executable = cpp_path.with_suffix("")
                    cpp_path.write_text(generated, encoding="utf-8")
                    build = subprocess.run(
                        [self.compiler, "-std=c++17", "-O0", str(cpp_path), "-o", str(executable)],
                        cwd=ROOT, text=True, capture_output=True, timeout=20,
                    )
                    self.assertEqual(build.returncode, 0, fixture_id + " C++ compilation failed:\n" + build.stderr)
                    result = subprocess.run(
                        [str(executable)], cwd=ROOT, text=True, capture_output=True, timeout=5,
                        input=fixture["expected"].get("stdin", ""),
                    )
                    expected = fixture["expected"]
                    self.assertEqual(result.returncode, expected["exit_code"], fixture_id + " exit code:\n" + result.stderr)
                    self.assertEqual(result.stdout, expected["stdout"], fixture_id + " stdout mismatch")
                    self.assertEqual(classify(result.stderr), expected.get("stderr_class"), fixture_id + " error class:\n" + result.stderr)
                    self.assertEqual(source_line(result.stderr), expected.get("source_line"), fixture_id + " source line:\n" + result.stderr)


if __name__ == "__main__":
    unittest.main()
