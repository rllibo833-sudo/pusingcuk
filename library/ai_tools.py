"""Internal allowlisted tool registry for PusingCuk's local AI assistant."""
from __future__ import annotations

import hashlib
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

_MAX_CUK_SOURCE_BYTES = 16 * 1024

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
        "language_version": "0.5-dev",
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
        "language_version": "0.5-dev",
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
        "language_version": "0.5-dev",
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
        "source_sha256": "5c8dd8fdf4524ed71ca6b46dbc7ea4b59278210747796db6dd8fe49a8f6bc252",
        "entrypoint": "status_penutupan_periode",
        "language_version": "0.5-dev",
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
        "language_version": "0.5-dev",
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
                    "Kompilasi source .cuk menjadi artefak JavaScript mandiri yang dapat diuji dengan Node.js. "
                    "Mengembalikan source JavaScript dan hash artefak. Tidak menjalankan source "
                    "dan tidak menyimpan artefak di server."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "source": {"type": "string", "minLength": 1, "maxLength": 16000}
                    },
                    "required": ["source"],
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

        if name == "cuk_compile_check":
            if set(arguments) != {"source"}:
                return {"ok": False, "error": "TOOL_ARGUMENTS_INVALID"}
            source = arguments.get("source")
            if not isinstance(source, str) or not source.strip():
                return {"ok": False, "error": "CUK_SOURCE_INVALID"}
            if "\x00" in source:
                return {"ok": False, "error": "CUK_SOURCE_INVALID"}
            try:
                source_bytes = source.encode("utf-8")
            except UnicodeEncodeError:
                return {"ok": False, "error": "CUK_SOURCE_INVALID"}
            if len(source_bytes) > _MAX_CUK_SOURCE_BYTES:
                return {"ok": False, "error": "CUK_SOURCE_TOO_LARGE"}
            try:
                generated = generate(from_source(source, "ai_input.cuk"))
            except (SyntaxError, ValueError, TypeError, UnicodeError) as exc:
                return {
                    "ok": False,
                    "error": "CUK_COMPILE_FAILED",
                    "diagnostic": str(exc)[:500],
                    "target": "javascript",
                }
            return {
                "ok": True,
                "operation": "compile_check",
                "target": "javascript",
                "language_version": LANGUAGE_VERSION,
                "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
                "artifact_sha256": hashlib.sha256(generated.encode("utf-8")).hexdigest(),
                "artifact_bytes": len(generated.encode("utf-8")),
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
            if any(not re.fullmatch(r"-?\d+", value) for value in lines[1:]):
                return {"ok": False, "error": "RULE_EXECUTION_FAILED"}
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
