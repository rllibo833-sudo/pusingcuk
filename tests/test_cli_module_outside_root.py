import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CliModuleOutsideRootTests(unittest.TestCase):
    def test_cli_resolves_mutually_importing_cuk_files_in_temp_project(self):
        with tempfile.TemporaryDirectory(prefix="warung_test_", dir="/tmp") as directory:
            project = Path(directory)
            main_file = project / "main.cuk"
            helper_file = project / "helper.cuk"
            main_file.write_text(
                "jancuk\n"
                'lah helper = angkut("helper.cuk")\n'
                "njir helper == salah\n"
                '    hedeh "cycle-safe"\n'
                "kampret\n"
                '    hedeh helper["nilai"]\n'
                "selesai njir\n"
                "selesai jancuk\n",
                encoding="utf-8",
            )
            helper_file.write_text(
                "jancuk\n"
                'lah utama = angkut("main.cuk")\n'
                "lah nilai = 42\n"
                "selesai jancuk\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(ROOT / "pusingcuk_new.py"), str(main_file)],
                cwd=ROOT, capture_output=True, text=True, check=False, timeout=10,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, "cycle-safe\n42\n")
            self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
