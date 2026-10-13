"""Konformansi dasar antara interpreter modular dan runtime C native."""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SHARED_FIXTURES = (
    "tests/native/functions.pusingcuk",
    "tests/native/dictionary_key_types.pusingcuk",
    "tests/native/for_range.pusingcuk",
    "tests/native/slang_aliases.pusingcuk",
    "examples/native/rekap_anggaran.pusingcuk",
    "examples/rekap_anggaran.cuk",
    "examples/warung.cuk",
)


class RuntimeConformanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not shutil.which("cc"):
            raise unittest.SkipTest("compiler C tidak tersedia; tes konformansi native dilewati")
        cls.tempdir = tempfile.TemporaryDirectory(prefix="pusingcuk-conformance-")
        cls.addClassCleanup(cls.tempdir.cleanup)
        cls.native_binary = Path(cls.tempdir.name) / "pusingcuk-native"
        build = subprocess.run(
            ["make", "native", f"NATIVE_BIN={cls.native_binary}"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if build.returncode != 0:
            raise RuntimeError(
                "Build runtime native gagal sebelum tes konformansi:\n"
                + build.stdout + build.stderr
            )

    def test_shared_fixtures_match(self):
        for fixture in SHARED_FIXTURES:
            path = ROOT / fixture
            with self.subTest(fixture=fixture):
                modular = subprocess.run(
                    [sys.executable, str(ROOT / "pusingcuk_new.py"), str(path)],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                native = subprocess.run(
                    [str(self.native_binary), str(path)],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(
                    modular.returncode, 0,
                    f"Interpreter modular gagal untuk {fixture}: {modular.stderr}",
                )
                self.assertEqual(
                    native.returncode, 0,
                    f"Runtime native gagal untuk {fixture}: {native.stderr}",
                )
                self.assertEqual(
                    modular.stdout, native.stdout,
                    f"Output runtime berbeda untuk {fixture}",
                )
