"""CLI regression tests for executable .cuk examples."""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "pusingcuk_new.py"
EXAMPLES = ROOT / "examples"


class CukExampleCliTests(unittest.TestCase):
    def test_halo_dunia_accepts_interactive_name(self):
        with tempfile.TemporaryDirectory(prefix="pusingcuk-example-") as temporary:
            project = Path(temporary)
            script = project / "halo_dunia.cuk"
            shutil.copyfile(EXAMPLES / script.name, script)
            result = subprocess.run(
                [sys.executable, str(CLI), str(script)], cwd=project,
                input="Ayu\n", capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Halo, Ayu!", result.stdout)

    def test_keuangan_example_runs_and_writes_within_project(self):
        with tempfile.TemporaryDirectory(prefix="pusingcuk-finance-") as temporary:
            project = Path(temporary)
            script = project / "keuangan_sederhana.cuk"
            shutil.copyfile(EXAMPLES / script.name, script)
            result = subprocess.run(
                [sys.executable, str(CLI), str(script)], cwd=project,
                input="Ayu\n3000000\n1250000\nya\n",
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Pemasukan: 3000000", result.stdout)
            self.assertIn("Pengeluaran: 1250000", result.stdout)
            self.assertIn("Sisa: 1750000", result.stdout)
            self.assertIn("Hitung catatan ke-1", result.stdout)
            self.assertIn("Hitung catatan ke-2", result.stdout)
            self.assertIn("Status: anggaran aman", result.stdout)
            self.assertIn("Catatan tersimpan: keuangan_sederhana.txt", result.stdout)
            note = (project / "keuangan_sederhana.txt").read_text(encoding="utf-8")
            self.assertIn("Nama: Ayu", note)
            self.assertIn("Sisa: 1750000", note)
            self.assertTrue((project / "keuangan_sederhana.txt").resolve().is_relative_to(project))


if __name__ == "__main__":
    unittest.main()
