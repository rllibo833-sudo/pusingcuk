import unittest

from compiler.bootstrap import BootstrapError, build


class BootstrapEvidenceTests(unittest.TestCase):
    def test_two_stage_build_emits_identical_artifacts(self):
        source = 'jancuk\nlah nama = "Dunia"\nhedeh "Halo, " + nama\nselesai jancuk\n'
        evidence = build(source, "hello.cuk")
        self.assertEqual(evidence["schema"], "pusingcuk-bootstrap-evidence")
        self.assertEqual(evidence["status"], "reproducible-subset")
        self.assertFalse(evidence["full_self_hosting"])
        self.assertEqual(evidence["comparison"], "identical")
        self.assertEqual(evidence["stages"][0]["ir_sha256"], evidence["stages"][1]["ir_sha256"])
        self.assertEqual(evidence["stages"][0]["bytecode_sha256"], evidence["stages"][1]["bytecode_sha256"])
        self.assertEqual(evidence["stages"][0]["stdout"], "Halo, Dunia\n")

    def test_bootstrap_rejects_unsupported_compiler_source_instead_of_claiming_success(self):
        source = 'jancuk\nfungsi tambah(a, b)\n    balek a + b\nselesai fungsi\nselesai jancuk\n'
        with self.assertRaises(BootstrapError):
            build(source, "compiler.cuk")


if __name__ == "__main__":
    unittest.main()
