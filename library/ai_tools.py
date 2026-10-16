"""Internal allowlisted tool registry for PusingCuk's local AI assistant."""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

from library.knowledge_grounding import rank_knowledge
from compiler.ir import LANGUAGE_VERSION, from_source
from compiler.js_backend import generate
from library.builtin_contract import BUILTIN_CONTRACT
from lexer import KEYWORD_ALIASES

_MAX_CUK_SOURCE_BYTES = 16 * 1024


def _cuk_diagnostic_location(message: str) -> dict[str, int] | None:
    """Extract a location only when it matches the compiler's explicit diagnostic format."""
    match = re.search(r"(?:\] )?Baris (\d+), kolom (\d+):", message)
    if not match:
        return None
    return {"line": int(match.group(1)), "column": int(match.group(2))}


def _cuk_language_identity(source: str) -> dict[str, Any]:
    """Describe official aliases recognized as tokens, not words in comments/strings."""
    from lexer import lex

    line_offsets = [0]
    line_offsets.extend(index + 1 for index, char in enumerate(source) if char == "\n")
    aliases_used = []
    seen = set()
    for token in lex(source):
        if token.kind != "KEYWORD":
            continue
        offset = line_offsets[token.line - 1] + token.column - 1
        match = re.match(r"[^\W\d]\w*", source[offset:], flags=re.UNICODE)
        if not match:
            continue
        word = match.group(0)
        if word in KEYWORD_ALIASES and word not in seen:
            seen.add(word)
            aliases_used.append({"word": word, "canonical": KEYWORD_ALIASES[word]})
    return {
        "opening_form": "jancuk",
        "closing_form": "selesai jancuk",
        "aliases_used": aliases_used,
    }


def _cuk_semantic_review(
    features: list[str],
    *,
    compile_ok: bool,
    diagnostic_type: str | None = None,
    diagnostic_location: dict[str, int] | None = None,
) -> dict[str, Any]:
    """Return a conservative, contract-grounded review summary for the AI."""
    if not compile_ok:
        return {
            "status": "compiler_rejected",
            "evidence": ["front_end_or_backend_rejected_source"],
            "diagnostic_type": diagnostic_type,
            "diagnostic_location": diagnostic_location,
            "next_step": (
                "Periksa diagnostik dan lokasi sumber; jangan menyimpulkan masalah "
                "runtime atau mengubah semantik sebelum penyebabnya terkonfirmasi."
            ),
        }
    return {
        "status": "compile_only",
        "evidence": ["parser_ir_validation", "javascript_generation"],
        "features_detected": sorted(set(features)),
        "not_verified": [
            "runtime_output",
            "cross_runtime_semantic_parity",
            "native_c_behavior",
            "pvm_behavior",
            "type_correctness_beyond_front_end_checks",
        ],
        "next_step": (
            "Gunakan docs/SEMANTIC_CONTRACT.md dan fixture yang sudah ada untuk "
            "memeriksa klaim semantik terkait fitur; jangan menyebutnya terbukti "
            "hanya karena kompilasi berhasil."
        ),
    }


_MAX_RULE_INPUT = 1_000_000_000_000
_MAX_RULE_INPUT_BYTES = 128
_MAX_RULE_OUTPUT_BYTES = 1024
_RULE_TIMEOUT_SECONDS = 3.0

# Rule source is package data owned by PusingCuk. The registry accepts inputs,
# never source code or caller-selected paths. This is a trusted fixed-artifact
# runner, not an OS sandbox; never register model-generated or untrusted source.
_REGISTERED_RULES: dict[str, dict[str, Any]] = {
    "budget.threshold.v1": {
        "source_file": "budget_threshold.cuk",
        "source_sha256": "0320f50b48489251d4a784ce3c1781a1a014ca2aecc5dfd1b8317f8a6b9fb911",
        "entrypoint": "status_anggaran",
        "language_version": "0.6-dev",
        "input_fields": ("nominal", "batas"),
        "properties": {
            "nominal": {"type": "integer", "minimum": 0, "maximum": _MAX_RULE_INPUT},
            "batas": {"type": "integer", "minimum": 0, "maximum": _MAX_RULE_INPUT},
        },
        "required": ("nominal", "batas"),
        "allowed_outputs": ("DALAM_BATAS", "PERLU_PERSETUJUAN", "INPUT_TIDAK_VALID"),
        "capabilities": (),
        "description": (
            "Jalankan aturan anggaran .cuk tetap yang terdaftar pada PusingCuk. "
            "Tidak menerima source dari model dan tidak memerlukan server/runner HTTP. "
            "Runtime referensi lokal bukan sandbox OS."
        ),
    },
    "journal.balance.v1": {
        "source_file": "journal_balance_check.cuk",
        "source_sha256": "ce519f68d20c0db3a5c611a30a7355e1dd1170a3450ab93d1f048e1945bd4f2c",
        "entrypoint": "cek_keseimbangan_jurnal",
        "language_version": "0.6-dev",
        "input_fields": ("debit_total", "kredit_total"),
        "properties": {
            "debit_total": {"type": "integer", "minimum": 0, "maximum": _MAX_RULE_INPUT},
            "kredit_total": {"type": "integer", "minimum": 0, "maximum": _MAX_RULE_INPUT},
        },
        "required": ("debit_total", "kredit_total"),
        "allowed_outputs": ("JURNAL_SEIMBANG", "JURNAL_TIDAK_SEIMBANG", "INPUT_TIDAK_VALID"),
        "capabilities": (),
        "description": (
            "Periksa dua total debit/kredit dengan aturan .cuk tetap. Ini hanya pemeriksaan "
            "sekunder atas total yang diberikan, bukan pembukuan, posting jurnal, atau "
            "pengganti mesin akuntansi deterministik CukAccount."
        ),
    },
    "accounting.equation.v1": {
        "source_file": "accounting_equation_check.cuk",
        "source_sha256": "aa2f46e3fb3ac65adc763de5f4818ccda251e2f316a6a91e16e41095890b35bc",
        "entrypoint": "cek_persamaan_akuntansi",
        "language_version": "0.6-dev",
        "input_fields": ("aset", "liabilitas", "ekuitas"),
        "properties": {
            "aset": {"type": "integer", "minimum": 0, "maximum": _MAX_RULE_INPUT},
            "liabilitas": {"type": "integer", "minimum": 0, "maximum": _MAX_RULE_INPUT},
            "ekuitas": {"type": "integer", "minimum": 0, "maximum": _MAX_RULE_INPUT},
        },
        "required": ("aset", "liabilitas", "ekuitas"),
        "allowed_outputs": ("PERSAMAAN_SEIMBANG", "PERSAMAAN_TIDAK_SEIMBANG", "INPUT_TIDAK_VALID"),
        "capabilities": (),
        "description": (
            "Periksa persamaan aset = liabilitas + ekuitas memakai artefak .cuk "
            "tetap. Pemeriksaan pendamping; bukan pengganti buku besar CukAccount."
        ),
    },
    "period.close.plan.v1": {
        "source_file": "period_close_plan.cuk",
        "source_sha256": "7625849ce41d1c5149b49a8d2f16f0df8834318c4cd2200fa647032b99a7eb7e",
        "entrypoint": "status_penutupan_periode",
        "language_version": "0.6-dev",
        "input_fields": ("income_total", "expense_total"),
        "properties": {
            "income_total": {"type": "integer", "minimum": 0, "maximum": _MAX_RULE_INPUT},
            "expense_total": {"type": "integer", "minimum": 0, "maximum": _MAX_RULE_INPUT},
        },
        "required": ("income_total", "expense_total"),
        "allowed_outputs": ("PENUTUPAN_LABA", "PENUTUPAN_RUGI", "PENUTUPAN_NOL", "INPUT_TIDAK_VALID"),
        "capabilities": (),
        "description": (
            "Rencanakan baris penutupan periode dari total pendapatan dan beban sintetis "
            "menggunakan aturan .cuk terdaftar. Menghasilkan rencana peran-akun untuk "
            "dibandingkan dengan CukAccount; tidak mem-posting jurnal."
        ),
    },
    "report.classification.v1": {
        "source_file": "report_classification_check.cuk",
        "source_sha256": "6f1882ee8d68d0bbe1feb279ce438a592b458ef3f267fc7a5607a224ec423c1d",
        "entrypoint": "cek_klasifikasi_laporan",
        "language_version": "0.6-dev",
        "input_fields": ("jumlah_kas", "kas_tanpa_kategori", "jumlah_ekuitas", "ekuitas_tanpa_kategori"),
        "properties": {
            "jumlah_kas": {"type": "integer", "minimum": 0, "maximum": _MAX_RULE_INPUT},
            "kas_tanpa_kategori": {"type": "integer", "minimum": 0, "maximum": _MAX_RULE_INPUT},
            "jumlah_ekuitas": {"type": "integer", "minimum": 0, "maximum": _MAX_RULE_INPUT},
            "ekuitas_tanpa_kategori": {"type": "integer", "minimum": 0, "maximum": _MAX_RULE_INPUT},
        },
        "required": ("jumlah_kas", "kas_tanpa_kategori", "jumlah_ekuitas", "ekuitas_tanpa_kategori"),
        "allowed_outputs": ("KLASIFIKASI_LAPORAN_BELUM_LENGKAP", "KLASIFIKASI_LAPORAN_LENGKAP", "INPUT_TIDAK_VALID"),
        "capabilities": (),
        "description": (
            "Diagnosis CukAccount: periksa jumlah baris kas/ekuitas dan jumlah yang belum "
            "diklasifikasikan sebelum laporan dihitung. Gunakan ketika arus kas atau perubahan "
            "ekuitas gagal karena kategori hilang. Input hanya hitungan agregat sintetis; "
            "rule tidak membaca atau mengubah buku pengguna. Setelah diagnosis, periksa program "
            ".cuk melalui cuk_compile_check dan sarankan klasifikasi eksplisit pada jurnal."
        ),
    },
}

# Model-facing tool names map only to internal registered rule IDs.
_TOOL_RULE_BINDINGS = {
    "budget_threshold": "budget.threshold.v1",
    "journal_balance_check": "journal.balance.v1",
    "accounting_equation_check": "accounting.equation.v1",
    "period_close_plan": "period.close.plan.v1",
    "report_classification_check": "report.classification.v1",
}


def _load_rule_source(rule: dict[str, Any]) -> bytes:
    """Load the bundled artifact; callers cannot choose its path."""
    return (Path(__file__).resolve().parent / rule["source_file"]).read_bytes()


def _rule_subprocess_environment() -> dict[str, str]:
    """Avoid inheriting API keys, runner tokens, and other ambient secrets."""
    allowed = ("PATH", "SYSTEMROOT", "WINDIR", "TEMP", "TMP")
    env = {key: os.environ[key] for key in allowed if os.environ.get(key)}
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


class ToolRegistry:
    """Expose only explicitly registered, schema-validated operations."""

    def __init__(self, documents: list[dict[str, Any]]):
        self.documents = documents
        self.by_id = {doc["id"]: doc for doc in documents}
        self.definitions = [
            {
                "type": "function",
                "function": {
                    "name": "knowledge_search",
                    "description": (
                        "Cari dokumen primer terkurasi milik PusingCuk serta ledger "
                        "migrasi konsep terpilih. Klaim historis CORE/Founder hanya "
                        "dapat diverifikasi sejauh dirangkum di ledger, bukan sebagai "
                        "indeks penuh kedua repositori."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "minLength": 1, "maxLength": 300},
                            "limit": {"type": "integer", "minimum": 1, "maximum": 3},
                        },
                        "required": ["query"],
                        "additionalProperties": False,
                    },
                },
            }
        ]
        self.definitions.append({
            "type": "function",
            "function": {
                "name": "cuk_compile_check",
                "description": (
                    "Validasi dan kompilasi source .cuk dengan front-end/compiler PusingCuk, "
                    "lalu kembalikan diagnostik atau artefak JavaScript beserta hash. Tidak "
                    "menjalankan source atau artefak; keberhasilan kompilasi bukan bukti hasil "
                    "runtime dan bukan sandbox OS."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "source": {"type": "string", "minLength": 1, "maxLength": 16000}
                    },
                    "required": ["source"],
                    "additionalProperties": False,
                },
            },        })
        self.definitions.append({
            "type": "function",
            "function": {
                "name": "cuk_compiler_context",
                "description": (
                    "Baca konteks compiler .cuk dari kontrak semantik kanonis: built-in, "
                    "status target, fixture konformansi, dan batas dukungan. Gunakan sebelum "
                    "menyarankan perubahan bahasa; data ini bukan bukti runtime lulus."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string", "enum": ["general", "builtins", "js", "native", "formats", "fixtures", "semantics", "development", "independence"]}
                    },
                    "required": [],
                    "additionalProperties": False,
                },
            },
        })

        for tool_name, rule_id in _TOOL_RULE_BINDINGS.items():
            rule = _REGISTERED_RULES[rule_id]
            self.definitions.append({
                "type": "function",
                "function": {
                    "name": tool_name,
                    "description": rule["description"],
                    "parameters": {
                        "type": "object",
                        "properties": rule["properties"],
                        "required": list(rule["required"]),
                        "additionalProperties": False,
                    },
                },
            })

    def execute(self, name: str, arguments: Any) -> dict[str, Any]:
        if not isinstance(arguments, dict):
            return {"ok": False, "error": "TOOL_ARGUMENTS_INVALID"}
        if name == "knowledge_search":
            if set(arguments) - {"query", "limit"}:
                return {"ok": False, "error": "TOOL_ARGUMENTS_INVALID"}
            query = arguments.get("query")
            limit = arguments.get("limit", 3)
            if not isinstance(query, str) or not query.strip() or len(query) > 300:
                return {"ok": False, "error": "KNOWLEDGE_QUERY_INVALID"}
            if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 3:
                return {"ok": False, "error": "KNOWLEDGE_LIMIT_INVALID"}
            ranked = rank_knowledge(self.documents, query, limit=limit)
            results = [{
                "id": item["id"],
                "title": item["title"],
                "summary": item["summary"][:300],
                "source_path": item["source_path"],
                "source_url": item["source_url"],
                "source_repository": item["source_repository"],
                "source_commit": item["source_commit"],
                "authority": item["authority"],
                "claim_status": item["claim_status"],
            } for item in ranked]
            return {"ok": True, "result_count": len(results), "results": results}

        if name == "cuk_compiler_context":
            if set(arguments) - {"topic"}:
                return {"ok": False, "error": "TOOL_ARGUMENTS_INVALID"}
            topic = arguments.get("topic", "general")
            allowed_topics = {
                "general", "builtins", "js", "native", "formats",
                "fixtures", "semantics", "development", "independence",
            }
            if not isinstance(topic, str) or topic not in allowed_topics:
                return {"ok": False, "error": "COMPILER_CONTEXT_TOPIC_INVALID"}
            entries = BUILTIN_CONTRACT["builtins"]
            try:
                manifest_path = Path(__file__).resolve().parent.parent / "tests" / "conformance" / "manifest.json"
                fixtures = json.loads(manifest_path.read_text(encoding="utf-8")).get("fixtures", [])
            except (OSError, json.JSONDecodeError):
                return {"ok": False, "error": "COMPILER_CONTEXT_FIXTURES_UNAVAILABLE"}
            summarize = lambda entry: {
                "name": entry["name"], "min_args": entry["min_args"], "max_args": entry["max_args"],
                "description": entry["description"], "implementation": entry["implementation"],
                "targets": {target: entry["backends"][target]["status"] for target in BUILTIN_CONTRACT["targets"]},
            }
            if topic == "builtins":
                result = {"builtins": [summarize(entry) for entry in entries]}
            elif topic == "js":
                result = {
                    "supported_builtins": [entry["name"] for entry in entries if entry["backends"]["js"]["status"] == "supported"],
                    "unsupported_builtins": [entry["name"] for entry in entries if entry["backends"]["js"]["status"] != "supported"],
                    "backend_nodes": ["Program", "Declare", "Assign", "Input", "Print", "If", "While", "For", "Function", "Return", "Literal", "Variable", "Unary", "Binary", "Try", "List", "Dict", "Index", "IndexAssign", "Call"],
                }
            elif topic == "native":
                native_fixtures = [
                    fixture for fixture in fixtures
                    if isinstance(fixture, dict)
                    and isinstance(fixture.get("runtimes"), dict)
                    and fixture["runtimes"].get("native") in {"required", "unsupported"}
                ]
                result = {
                    "baseline_role": "Native C is the second runtime for the explicitly supported subset; reference-only features must not be presented as native parity.",
                    "supported_builtins": [entry["name"] for entry in entries if entry["backends"].get("native_c", {}).get("status") == "supported"],
                    "unsupported_builtins": [entry["name"] for entry in entries if entry["backends"].get("native_c", {}).get("status") != "supported"],
                    "fixture_count": len(native_fixtures),
                    "required_fixture_ids": [fixture["id"] for fixture in native_fixtures if fixture["runtimes"].get("native") == "required"],
                    "shared_required_fixture_ids": [
                        fixture["id"] for fixture in native_fixtures
                        if fixture["runtimes"].get("reference") == "required"
                        and fixture["runtimes"].get("native") == "required"
                    ],
                    "reference_only_fixture_ids": [
                        fixture["id"] for fixture in native_fixtures
                        if fixture["runtimes"].get("reference") == "required"
                        and fixture["runtimes"].get("native") == "unsupported"
                    ],
                    "unsupported_fixture_ids": [fixture["id"] for fixture in native_fixtures if fixture["runtimes"].get("native") == "unsupported"],
                    "parity_rule": "Only shared_required_fixture_ids establish the Python/native parity baseline; unsupported is not a pass and reference-only features are not native parity.",
                }
            elif topic == "independence":
                native_required = [
                    fixture for fixture in fixtures
                    if isinstance(fixture, dict)
                    and isinstance(fixture.get("runtimes"), dict)
                    and fixture["runtimes"].get("native") == "required"
                ]
                native_unsupported = [
                    fixture for fixture in fixtures
                    if isinstance(fixture, dict)
                    and isinstance(fixture.get("runtimes"), dict)
                    and fixture["runtimes"].get("native") == "unsupported"
                ]
                reference_only = [
                    fixture for fixture in native_unsupported
                    if fixture["runtimes"].get("reference") == "required"
                ]
                native_gaps = [
                    {"name": entry["name"], "status": entry["backends"].get("native_c", {}).get("status", "missing")}
                    for entry in entries
                    if entry["backends"].get("native_c", {}).get("status") != "supported"
                ]
                result = {
                    "goal": "Make .cuk useful without requiring the Python interpreter at program execution time, while keeping PusingCuk AI as a helper for language development.",
                    "current_boundary": {
                        "native_execution": "native/pusingcuk.c parses and executes .cuk without importing Python; building it requires a C compiler and libm.",
                        "python_still_used_for": ["modular reference interpreter", "compiler and AI tooling", "conformance/test harness"],
                        "important_distinction": "Native execution independence is not the same as removing Python from all developer tooling."
                    },
                    "evidence": {
                        "native_required_fixture_count": len(native_required),
                        "native_required_fixture_ids": [fixture["id"] for fixture in native_required],
                        "native_unsupported_fixture_count": len(native_unsupported),
                        "native_unsupported_fixture_ids": [fixture["id"] for fixture in native_unsupported],
                        "reference_required_but_native_unsupported_ids": [fixture["id"] for fixture in reference_only],
                        "builtins_not_claimed_supported_by_native": native_gaps
                    },
                    "next_actions": [
                        "Choose one existing reference-required/native-unsupported fixture and inspect the contract before implementing its native C behavior.",
                        "Prefer closing a small native C semantic gap in core language semantics (types, operators, collections, built-ins, diagnostics) over expanding experimental transpiler backends.",
                        "Do not propose JSON, HTML, or CSV implementation or support expansion as part of native-runtime independence work.",
                        "Keep each change bounded and reuse existing conformance infrastructure; do not add a new document, issue, or CI workflow for a single gap.",
                        "After implementation, run only the focused native fixture and the existing conformance command before claiming parity."
                    ],
                    "safety_note": "AI-generated code is a proposal, not proof. Do not change a fixture to hide a mismatch or mark a target supported before its behavior is implemented."
                }
            elif topic == "formats":
                names = {"json_teks", "json_baca", "html_aman", "csv_baris"}
                result = {"builtins": [summarize(entry) for entry in entries if entry["name"] in names],
                          "contract": {"json": "strict JSON; string keys; finite numbers; safe integers", "html": "escape &, <, >, double quote, apostrophe", "csv": "one row; quote fields containing comma, quote, CR, or LF"}}
            elif topic == "fixtures":
                result = {"count": len(fixtures), "ids": [fixture.get("id") for fixture in fixtures],
                          "last_fixture_ids": [fixture.get("id") for fixture in fixtures[-12:]]}
            elif topic == "semantics":
                result = {
                    "source_of_truth": ["SPEC.md", "docs/SEMANTIC_CONTRACT.md", "library/builtin_contract.json", "tests/conformance/manifest.json"],
                    "rules": ["boolean is not numeric", "short-circuit and/or", "floor division follows mathematical floor", "modulo follows a-floor(a/b)*b", "finite numeric values only for math builtins", "safe integer range is +/-9007199254740991", "compile success does not prove runtime parity"],
                    "review_order": ["reproduce behavior with a fixture", "check reference interpreter", "check target backend", "update metadata only after implementation exists", "run focused conformance"],
                }
            elif topic == "development":
                shared = [
                    fixture for fixture in fixtures
                    if isinstance(fixture, dict)
                    and isinstance(fixture.get("runtimes"), dict)
                    and fixture["runtimes"].get("reference") == "required"
                    and fixture["runtimes"].get("native") == "required"
                ]
                reference_only = [
                    fixture for fixture in fixtures
                    if isinstance(fixture, dict)
                    and isinstance(fixture.get("runtimes"), dict)
                    and fixture["runtimes"].get("reference") == "required"
                    and fixture["runtimes"].get("native") == "unsupported"
                ]
                # Turn semantic priorities into repository-grounded coverage hints.
                # A missing shared fixture is a coverage gap to investigate, not
                # proof that an implementation is broken or unsupported.
                priority_requirements = [
                    "numeric-types", "numeric-range", "safe-integer-range",
                    "ordered-accumulation", "collection-types", "runtime-diagnostics",
                    "short-circuit", "floor-division", "modulo",
                ]
                shared_by_requirement = {
                    requirement: [
                        fixture["id"] for fixture in shared
                        if requirement in fixture.get("requires", [])
                    ]
                    for requirement in priority_requirements
                }
                result = {
                    "purpose": "Use PusingCuk AI to improve .cuk semantics from repository evidence, not from guesses or compile-only success.",
                    "source_of_truth": ["SPEC.md", "docs/SEMANTIC_CONTRACT.md", "library/builtin_contract.json", "tests/conformance/manifest.json"],
                    "baseline": "Python reference behavior is authoritative; native C is the second runtime only for the shared required subset.",
                    "shared_required_fixture_count": len(shared),
                    "shared_required_fixture_ids": [fixture["id"] for fixture in shared],
                    "priority_requirement_coverage": {
                        requirement: {
                            "shared_fixture_count": len(fixture_ids),
                            "shared_fixture_ids": fixture_ids,
                            "coverage_status": "fixture-backed" if fixture_ids else "no-shared-fixture-found",
                        }
                        for requirement, fixture_ids in shared_by_requirement.items()
                    },
                    "coverage_warning": "No shared fixture means investigate the contract and both implementations before editing; absence of coverage alone does not prove a runtime bug.",
                    "reference_only_fixture_count": len(reference_only),
                    "reference_only_fixture_ids": [fixture["id"] for fixture in reference_only],
                    "next_actions": [
                        "Find one concrete behavior gap in an existing required fixture or semantic contract.",
                        "Reproduce the smallest failing case on the Python reference and native C before changing behavior.",
                        "Make the implementation agree with the documented contract; do not weaken a fixture to hide a mismatch.",
                        "Add or update only the focused fixture that proves the behavior and its relevant error boundary.",
                        "Update builtin/runtime metadata only after implementation and fixture evidence agree.",
                        "Report the exact changed behavior and which runtime evidence exists; never infer APK readiness from compiler success."
                    ],
                    "priority_semantics": [
                        "jumlah: empty list, negative values, cancellation, fractions, invalid types, safe-integer intermediate and final bounds",
                        "collections: empty/malformed collections, indexing and mutation consistency",
                        "operators and types: boolean-versus-number, floor division, modulo, short-circuit behavior",
                        "diagnostics: syntax/runtime class, exit code, source line and no partial output on failure"
                    ],
                    "deferred_targets": ["JavaScript/PVM as experimental", "Android/APK until language semantics and a runnable target are independently proven"],
                    "guardrails": ["Unsupported is not a pass", "compile success is not runtime proof", "no broad test runs for every edit; use the narrowest relevant conformance case"]
                }
            else:
                result = {
                    "language_version": BUILTIN_CONTRACT["language_version"],
                    "contract_version": BUILTIN_CONTRACT["contract_version"],
                    "builtin_count": len(entries),
                    "supported_builtin_counts": {target: sum(1 for entry in entries if entry["backends"][target]["status"] == "supported") for target in BUILTIN_CONTRACT["targets"]},
                    "fixture_count": len(fixtures),
                    "compiler_pipeline": ["lexer", "parser", "IR validation", "target backend generation"],
                    "known_limits": ["compile_check does not execute generated code", "cross-runtime parity requires fixtures", "native C, JavaScript transpiler, and VM support remain separately declared", "JavaScript transpiler, PVM, and Android Studio APK work are experimental or deferred, not the supported baseline"],
                    "baseline_targets": ["Python reference interpreter", "native C runtime"],
                    "next_priority": "Prioritaskan kesenjangan semantik Python/C yang terbukti: operator, tipe, koleksi, built-in, diagnostik, dan fixture konformansi bersama. Untuk jumlah dan statistik, kunci perilaku daftar kosong, nilai negatif, pembatalan, pecahan, tipe tidak valid, serta batas integer aman. Jangan mengutamakan JS/PVM/APK sebelum baseline Python/C dan fixture terkait konsisten.",
                }
            return {"ok": True, "operation": "compiler_context", "topic": topic, "context": result}

        if name == "cuk_compile_check":
            if set(arguments) != {"source"}:
                return {"ok": False, "error": "TOOL_ARGUMENTS_INVALID"}
            source = arguments.get("source")
            if not isinstance(source, str) or not source.strip():
                return {"ok": False, "error": "CUK_SOURCE_INVALID", "evidence_status": "SOURCE_INPUT_TIDAK_VALID"}
            if "\x00" in source:
                return {
                    "ok": False,
                    "error": "CUK_SOURCE_INVALID",
                    "evidence_status": "SOURCE_INPUT_TIDAK_VALID",
                }
            # Character count is a cheap lower bound for UTF-8 byte length.
            # Reject obviously oversized text before allocating an encoded copy.
            if len(source) > _MAX_CUK_SOURCE_BYTES:
                return {"ok": False, "error": "CUK_SOURCE_TOO_LARGE", "evidence_status": "SOURCE_MELEBIHI_BATAS"}
            try:
                source_bytes = source.encode("utf-8")
            except UnicodeEncodeError:
                return {
                    "ok": False,
                    "error": "CUK_SOURCE_INVALID",
                    "evidence_status": "SOURCE_INPUT_TIDAK_VALID",
                }
            if len(source_bytes) > _MAX_CUK_SOURCE_BYTES:
                return {"ok": False, "error": "CUK_SOURCE_TOO_LARGE", "evidence_status": "SOURCE_MELEBIHI_BATAS"}
            language_identity = {
                "opening_form": "jancuk",
                "closing_form": "selesai jancuk",
                "aliases_used": [],
            }
            try:
                language_identity = _cuk_language_identity(source)
                document = from_source(source, "ai_input.cuk")
                generated = generate(document)
            except (SyntaxError, ValueError, TypeError, UnicodeError, ArithmeticError) as exc:
                return {
                    "ok": False,
                    "error": "CUK_COMPILE_FAILED",
                    "evidence_status": "SOURCE_DITOLAK_COMPILER",
                    "diagnostic": str(exc)[:500],
                    "diagnostic_type": type(exc).__name__,
                    "diagnostic_location": _cuk_diagnostic_location(str(exc)),
                    "semantic_review": _cuk_semantic_review(
                        [],
                        compile_ok=False,
                        diagnostic_type=type(exc).__name__,
                        diagnostic_location=_cuk_diagnostic_location(str(exc)),
                    ),
                    "target": "javascript",
                    "language_version": LANGUAGE_VERSION,
                    "language_identity": language_identity,
                    "executed": False,
                }
            except Exception as exc:
                # Unexpected compiler failures are not evidence that user source is invalid.
                # Keep the AI tool response usable without exposing internal exception details.
                return {
                    "ok": False,
                    "error": "CUK_COMPILER_INTERNAL_ERROR",
                    "evidence_status": "STATUS_KOMPILASI_TIDAK_VALID",
                    "diagnostic": (
                        "Terjadi kesalahan internal saat memvalidasi atau menghasilkan "
                        "artefak .cuk; sumber belum dapat dinilai."
                    ),
                    "diagnostic_type": type(exc).__name__,
                    "diagnostic_location": None,
                    "semantic_review": {
                        "status": "compiler_internal_error",
                        "evidence": ["unexpected_compiler_exception"],
                        "diagnostic_type": type(exc).__name__,
                        "next_step": (
                            "Periksa kesalahan internal compiler/tool terlebih dahulu; "
                            "jangan menyimpulkan source .cuk salah atau mengubah kontrak semantik."
                        ),
                    },
                    "target": "javascript",
                    "language_version": LANGUAGE_VERSION,
                    "language_identity": language_identity,
                    "executed": False,
                }
            artifact_bytes = generated.encode("utf-8")
            return {
                "ok": True,
                "operation": "compile_check",
                "evidence_status": "KOMPILASI_LOLOS_RUNTIME_BELUM_DIUJI",
                "target": "javascript",
                "language_version": LANGUAGE_VERSION,
                "language_identity": language_identity,
                "features": document.get("features", []),
                "semantic_review": _cuk_semantic_review(
                    document.get("features", []),
                    compile_ok=True,
                ),
                "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
                "artifact_sha256": hashlib.sha256(artifact_bytes).hexdigest(),
                "artifact_bytes": len(artifact_bytes),
                "artifact": generated,
                "executed": False,
                "artifact_saved": False,
            }

        rule_id = _TOOL_RULE_BINDINGS.get(name)
        if rule_id is not None:
            rule = _REGISTERED_RULES.get(rule_id)
            if rule is None:
                return {"ok": False, "error": "RULE_NOT_REGISTERED"}
            if set(arguments) != set(rule["input_fields"]):
                return {"ok": False, "error": "TOOL_ARGUMENTS_INVALID"}
            for field, schema in rule["properties"].items():
                value = arguments[field]
                if (
                    schema["type"] == "integer"
                    and (
                        isinstance(value, bool)
                        or not isinstance(value, int)
                        or not schema["minimum"] <= value <= schema["maximum"]
                    )
                ):
                    return {"ok": False, "error": "RULE_INPUT_INVALID"}
            result = self._run_registered_rule(rule_id, arguments)
            if result.get("ok") and rule_id == "period.close.plan.v1":
                values = result.pop("period_close_values", None)
                if not isinstance(values, list) or len(values) != 7:
                    return {"ok": False, "error": "RULE_EXECUTION_FAILED"}
                (
                    net_result, income_debit, income_credit,
                    expense_debit, expense_credit, retained_debit, retained_credit,
                ) = values
                # Treat the .cuk rule as the planner, then independently verify
                # its accounting semantics before exposing the plan to the model.
                income_total = arguments["income_total"]
                expense_total = arguments["expense_total"]
                expected_result = income_total - expense_total
                expected_status = (
                    "PENUTUPAN_LABA" if expected_result > 0 else
                    "PENUTUPAN_RUGI" if expected_result < 0 else
                    "PENUTUPAN_NOL"
                )
                if (
                    result.get("result") != expected_status
                    or net_result != expected_result
                    or income_debit != income_total
                    or income_credit != 0
                    or expense_debit != 0
                    or expense_credit != expense_total
                    or retained_debit != max(-expected_result, 0)
                    or retained_credit != max(expected_result, 0)
                ):
                    return {"ok": False, "error": "RULE_SEMANTIC_MISMATCH"}
                closing_lines = []
                for role, debit, credit in (
                    ("income", income_debit, income_credit),
                    ("expense", expense_debit, expense_credit),
                    ("retained_earnings", retained_debit, retained_credit),
                ):
                    if debit or credit:
                        closing_lines.append({
                            "role": role,
                            "debit_minor_units": debit,
                            "credit_minor_units": credit,
                        })
                debit_total = sum(line["debit_minor_units"] for line in closing_lines)
                credit_total = sum(line["credit_minor_units"] for line in closing_lines)
                if debit_total != credit_total:
                    return {"ok": False, "error": "RULE_EXECUTION_FAILED"}
                result["net_result_minor_units"] = net_result
                result["closing_lines"] = closing_lines
                result["debit_total"] = debit_total
                result["credit_total"] = credit_total
            return result

        return {"ok": False, "error": "TOOL_NOT_ALLOWLISTED"}

    @staticmethod
    def _run_registered_rule(rule_id: str, arguments: dict[str, int]) -> dict[str, Any]:
        """Execute one hash-pinned .cuk artifact without a local HTTP runner."""
        rule = _REGISTERED_RULES.get(rule_id)
        if rule is None:
            return {"ok": False, "error": "RULE_NOT_REGISTERED"}
        if rule["capabilities"]:
            return {"ok": False, "error": "RULE_CAPABILITY_DENIED"}
        if set(arguments) != set(rule["input_fields"]):
            return {"ok": False, "error": "TOOL_ARGUMENTS_INVALID"}
        for field, schema in rule["properties"].items():
            value = arguments[field]
            if (
                isinstance(value, bool)
                or not isinstance(value, int)
                or not schema["minimum"] <= value <= schema["maximum"]
            ):
                return {"ok": False, "error": "RULE_INPUT_INVALID"}

        try:
            source = _load_rule_source(rule)
        except OSError:
            return {"ok": False, "error": "RULE_ARTIFACT_UNAVAILABLE"}
        if hashlib.sha256(source).hexdigest() != rule["source_sha256"]:
            return {"ok": False, "error": "RULE_ARTIFACT_HASH_MISMATCH"}

        cli_path = Path(__file__).resolve().parent.parent / "pusingcuk_new.py"
        if not cli_path.is_file():
            return {"ok": False, "error": "RULE_RUNTIME_UNAVAILABLE"}

        stdin_text = "".join(f"{arguments[field]}\n" for field in rule["input_fields"])
        if len(stdin_text.encode("utf-8")) > _MAX_RULE_INPUT_BYTES:
            return {"ok": False, "error": "RULE_INPUT_TOO_LARGE"}

        started = time.monotonic()
        try:
            with tempfile.TemporaryDirectory(prefix="pusingcuk-rule-") as workdir:
                program_path = Path(workdir) / "registered_rule.cuk"
                program_path.write_bytes(source)
                completed = subprocess.run(
                    [sys.executable, str(cli_path), str(program_path)],
                    cwd=workdir,
                    env=_rule_subprocess_environment(),
                    input=stdin_text,
                    text=True,
                    encoding="utf-8",
                    capture_output=True,
                    timeout=_RULE_TIMEOUT_SECONDS,
                    check=False,
                )
        except subprocess.TimeoutExpired:
            return {"ok": False, "error": "RULE_EXECUTION_TIMEOUT"}
        except OSError:
            return {"ok": False, "error": "RULE_RUNTIME_UNAVAILABLE"}

        elapsed_ms = int((time.monotonic() - started) * 1000)
        stdout = completed.stdout
        if (
            completed.returncode != 0
            or completed.stderr
            or not isinstance(stdout, str)
            or len(stdout.encode("utf-8")) > _MAX_RULE_OUTPUT_BYTES
        ):
            return {"ok": False, "error": "RULE_EXECUTION_FAILED"}

        if rule_id == "period.close.plan.v1":
            lines = stdout.splitlines()
            if len(lines) != 8 or lines[0] not in rule["allowed_outputs"]:
                return {"ok": False, "error": "RULE_EXECUTION_FAILED"}
            if any(not re.fullmatch(r"-?\d+", value) for value in lines[1:]):                return {"ok": False, "error": "RULE_EXECUTION_FAILED"}
            values = [int(value) for value in lines[1:]]
            if any(abs(value) > _MAX_RULE_INPUT for value in values):
                return {"ok": False, "error": "RULE_EXECUTION_FAILED"}
            return {
                "ok": True,
                "program_id": rule_id,
                "program_sha256": rule["source_sha256"],
                "language_version": rule["language_version"],
                "entrypoint": rule["entrypoint"],
                "capabilities": [],
                "execution_boundary": "fixed-hash-local-rule-not-os-sandbox",
                "result": lines[0],
                "period_close_values": values,
                "elapsed_ms": elapsed_ms,
            }

        if stdout not in {f"{value}\n" for value in rule["allowed_outputs"]}:
            return {"ok": False, "error": "RULE_EXECUTION_FAILED"}
        return {
            "ok": True,
            "program_id": rule_id,
            "program_sha256": rule["source_sha256"],
            "language_version": rule["language_version"],
            "entrypoint": rule["entrypoint"],
            "capabilities": [],
            "execution_boundary": "fixed-hash-local-rule-not-os-sandbox",
            "result": stdout[:-1],
            "elapsed_ms": elapsed_ms,
        }