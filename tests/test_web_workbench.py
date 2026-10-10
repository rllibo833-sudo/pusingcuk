import shutil
import tempfile
import unittest
from pathlib import Path

from tools.web_workbench import MAX_SOURCE_BYTES, build_native, run_program, validate_payload

class WorkbenchValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (shutil.which("cc") or shutil.which("clang") or shutil.which("gcc")):
            raise unittest.SkipTest("compiler C tidak tersedia")
        cls.tempdir = tempfile.TemporaryDirectory(prefix="pusingcuk-workbench-test-")
        cls.addClassCleanup(cls.tempdir.cleanup)
        cls.binary = build_native(cls.tempdir.name)

    def test_accepts_program_and_stdin(self):
        source, stdin = validate_payload({"source": "jancuk\nselesai jancuk", "stdin": "Budi\n"})
        self.assertEqual(source, "jancuk\nselesai jancuk")
        self.assertEqual(stdin, "Budi\n")

    def test_rejects_non_object(self):
        with self.assertRaises(ValueError): validate_payload("jancuk")
    def test_rejects_empty_source(self):
        with self.assertRaises(ValueError): validate_payload({"source": "  "})
    def test_rejects_nul(self):
        with self.assertRaises(ValueError): validate_payload({"source": "jancuk\x00"})
    def test_rejects_oversized_source(self):
        with self.assertRaises(ValueError): validate_payload({"source": "x" * (MAX_SOURCE_BYTES + 1)})
    def test_rejects_non_text_stdin(self):
        with self.assertRaises(ValueError): validate_payload({"source": "jancuk", "stdin": ["not", "text"]})
    def test_executes_native_runtime(self):
        result = run_program(self.binary, "jancuk\nhedeh 40 + 2\nselesai jancuk")
        self.assertTrue(result["ok"], result["stderr"])
        self.assertEqual(result["stdout"], "42\n")
    def test_passes_stdin_to_native_runtime(self):
        source = 'jancuk\ntanya nama = "Nama? "\nhedeh nama\nselesai jancuk'
        result = run_program(self.binary, source, "Budi\n")
        self.assertTrue(result["ok"], result["stderr"])
        self.assertEqual(result["stdout"], "Nama? Budi\n")

if __name__ == "__main__":
    unittest.main()
