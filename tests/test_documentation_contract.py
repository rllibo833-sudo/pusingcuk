"""Prevent documentation version and built-in-count drift."""
import json
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DocumentationContractTests(unittest.TestCase):
    def test_public_docs_match_language_and_package_contract(self):
        package = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        contract = json.loads((ROOT / "library/builtin_contract.json").read_text(encoding="utf-8"))
        language = package["tool"]["pusingcuk"]["language-version"]
        package_version = package["project"]["version"]
        total = len(contract["builtins"])
        native = sum(item.get("backends", {}).get("native_c", {}).get("status") == "supported"
                     for item in contract["builtins"])
        self.assertEqual(contract["language_version"], language)
        self.assertEqual(contract["contract_version"], language)
        self.assertEqual((language, package_version, total, native),
                         ("0.6-dev", "0.8.0.dev0", 25, 17))
        expectations = {
            "docs/COMPATIBILITY.md": [f"`{language}`", f"{total} built-in", f"{native} built-in"],
            "docs/VISION.md": [f"`{language}`", f"`{package_version}`"],
            "docs/NATIVE_RUNTIME.md": [f"`{language}`", f"`{package_version}`"],
            "docs/language/BUILTINS.md": [f"`{language}`", f"## {total} Built-in Terkontrak"],
            "docs/PEMULA.md": [f"`{language}`", f"`{package_version}`", f"{total} built-in", f"{native} di antaranya"],
        }
        for relative, phrases in expectations.items():
            content = (ROOT / relative).read_text(encoding="utf-8")
            for phrase in phrases:
                self.assertIn(phrase, content, f"{relative} missing {phrase!r}")
            self.assertNotIn("0.4-dev", content, f"{relative} has stale language version")
            self.assertNotIn("## 19 Built-in Terkontrak", content)



    def test_ai_engine_docs_match_local_service_and_migration_boundaries(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        readiness = (ROOT / "docs/AI_ENGINE_READINESS.md").read_text(encoding="utf-8")
        grounding = (ROOT / "docs/AI_KNOWLEDGE_GROUNDING.md").read_text(encoding="utf-8")
        service = (ROOT / "docs/AI_LOCAL_SERVICE.md").read_text(encoding="utf-8")
        ledger = (ROOT / "docs/AI_ENGINE_MIGRATION_LEDGER.md").read_text(encoding="utf-8")

        self.assertIn("pusingcuk-ai-service", readme)
        self.assertIn("docs/AI_LOCAL_SERVICE.md", readme)
        self.assertIn("loopback-only", readiness)
        self.assertNotIn("It is not yet a multi-user HTTP service", readiness)
        self.assertIn("GET /healthz", service)
        self.assertIn("not a public hosted service", service)
        self.assertIn("AI_ENGINE_MIGRATION_LEDGER.md", grounding)
        self.assertIn("No Proof, No Claim", ledger)
        self.assertIn("Founder-OS", ledger)
        self.assertIn("kawasan-masjid-core", ledger)
        self.assertIn("not a general-purpose security sandbox", ledger)
        self.assertIn("/blob/d9a41ae35dcc08628c7ac1fc38b3ac52fb982792/", ledger)
        self.assertIn("/blob/2e11dd3d8974a8a8390636a55a286057db99db05/", ledger)
        self.assertNotIn("/blob/main/", ledger)


    def test_ai_index_benchmark_and_conformance_counts_stay_in_sync(self):
        root = Path(__file__).resolve().parents[1]
        index = json.loads((root / "library/knowledge_index.json").read_text(encoding="utf-8"))
        benchmark = json.loads((root / "tests/fixtures/knowledge_retrieval_cases.json").read_text(encoding="utf-8"))
        manifest = json.loads((root / "tests/conformance/manifest.json").read_text(encoding="utf-8"))
        documents = index["documents"]
        source_ids = {item["id"] for item in documents}
        self.assertEqual(len(documents), 22)
        self.assertEqual(len(source_ids), 22)
        self.assertTrue(all(item["source_repository"] == "rllibo833-sudo/pusingcuk" for item in documents))
        self.assertTrue(all(item["visibility"] == "public-safe" for item in documents))
        self.assertTrue(all(len(item["source_commit"]) == 40 for item in documents))
        self.assertEqual(len(benchmark["cases"]), 22)
        self.assertTrue(all(case["expected_top_id"] in source_ids for case in benchmark["cases"]))

        counts = {"reference:required": 0, "native:required": 0, "native:unsupported": 0}
        for fixture in manifest["fixtures"]:
            for runtime, status in fixture["runtimes"].items():
                key = f"{runtime}:{status}"
                counts[key] = counts.get(key, 0) + 1
        self.assertEqual(len(manifest["fixtures"]), 70)
        self.assertEqual(counts["reference:required"], 69)
        self.assertEqual(counts["native:required"], 67)
        self.assertEqual(counts["native:unsupported"], 3)

        readiness = (root / "docs/AI_ENGINE_READINESS.md").read_text(encoding="utf-8")
        ledger = (root / "docs/AI_ENGINE_MIGRATION_LEDGER.md").read_text(encoding="utf-8")
        status = (root / "docs/PROJECT_STATUS_AND_ROADMAP.md").read_text(encoding="utf-8")
        self.assertIn("22-case baseline currently yields top-1", readiness)
        self.assertIn("22 curated source records", readiness)
        self.assertNotIn("16-case exact-top-1 retrieval benchmark", readiness)
        self.assertNotIn("16 source records", ledger)
        self.assertIn("22 dokumen sumber terkurasi", status)
        self.assertIn("22 kasus baseline menghasilkan top-1", status)
        self.assertIn("5/8 (62,5%)", status)
        self.assertIn("6/8 (75%)", status)
        self.assertIn("70 fixture", status)

    def test_supabase_notes_migration_has_owner_only_rls_and_no_client_secret(self):
        root = Path(__file__).resolve().parents[1]
        migration = (root / "supabase/migrations/20261015002334_pusingcuk_project_notes_v1.sql").read_text(encoding="utf-8").lower()
        smoke = (root / "supabase/tests/20261015002334_pusingcuk_project_notes_smoke.sql").read_text(encoding="utf-8").lower()
        access_fix = (root / "supabase/migrations/20261015002509_restrict_public_rls_auto_enable_execution.sql").read_text(encoding="utf-8").lower()
        status = (root / "docs/integrations/SUPABASE_PROJECTS.md").read_text(encoding="utf-8").lower()
        self.assertIn("references auth.users(id) on delete cascade", migration)
        self.assertIn("enable row level security", migration)
        self.assertIn("force row level security", migration)
        for operation in ("select", "insert", "update", "delete"):
            self.assertIn(f"pusingcuk_notes_{operation}_own", migration)
        self.assertIn("auth.uid()", migration)
        self.assertIn("revoke all on table", migration)
        self.assertIn("to authenticated", migration)
        self.assertIn("rls_cross_user_read_leak", smoke)
        self.assertIn("rls_cross_user_insert_allowed", smoke)
        self.assertIn("rls_cross_user_update_allowed", smoke)
        self.assertIn("rls_cross_user_delete_allowed", smoke)
        self.assertIn("not a rest api or application-runtime integration test", status)
        self.assertNotIn("service_role key is required", status)
        self.assertIn("revoke all on function public.rls_auto_enable()", access_fix)

    def test_release_claims_remain_proportional_to_evidence(self):
        root = Path(__file__).resolve().parents[1]
        readme = (root / "README.md").read_text(encoding="utf-8").lower()
        readiness = (root / "docs/AI_ENGINE_READINESS.md").read_text(encoding="utf-8").lower()
        status = (root / "docs/PROJECT_STATUS_AND_ROADMAP.md").read_text(encoding="utf-8").lower()
        supabase = (root / "docs/integrations/SUPABASE_PROJECTS.md").read_text(encoding="utf-8").lower()
        package = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))

        self.assertIn("experimental", readme)
        self.assertIn("not a foundation model trained by pusingcuk", readiness)
        self.assertIn("not a claim that a production service is deployed", readiness)
        self.assertIn("audit ini tidak menyatakan bahasa stabil atau ai akurat secara umum", status)
        self.assertIn("application status:** still not connected", supabase)
        self.assertEqual(package["project"]["classifiers"][0], "Development Status :: 3 - Alpha")
        self.assertNotIn("supabase sync active", status)
        self.assertNotIn("apk has been tested on physical android devices", status)

if __name__ == "__main__":
    unittest.main()
