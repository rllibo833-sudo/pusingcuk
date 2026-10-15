"""Print reproducible offline retrieval/citation/scope metrics; no live provider is called."""
from __future__ import annotations

import json
import re
from pathlib import Path

from library.ai_tools import ToolRegistry
from library.knowledge_grounding import append_citations, load_index, rank_knowledge

ROOT = Path(__file__).resolve().parents[1]


def evaluate() -> dict:
    documents = load_index(ROOT / "library" / "knowledge_index.json")
    baseline = json.loads((ROOT / "tests" / "fixtures" / "knowledge_retrieval_cases.json").read_text(encoding="utf-8"))
    adversarial = json.loads((ROOT / "tests" / "fixtures" / "ai_adversarial_eval.json").read_text(encoding="utf-8"))
    top1 = top3 = 0
    for case in baseline["cases"]:
        ids = [doc["id"] for doc in rank_knowledge(documents, case["query"], limit=3)]
        top1 += bool(ids and ids[0] == case["expected_top_id"])
        top3 += case["expected_top_id"] in ids
    trusted = documents[0]
    fake = {**trusted, "url": "https://attacker.example/fake"}
    answer = append_citations("Jawaban [tautan](https://attacker.example/fake)", [trusted, fake])
    emitted = re.findall(r"\]\((https://[^)]+)\)", answer)
    citation_precision = sum(url == trusted["url"] for url in emitted) / max(1, len(emitted))
    registry = ToolRegistry(documents)
    injections = [case for case in adversarial["cases"] if case["category"] == "prompt-injection"]
    fail_closed = sum(registry.execute("run_shell", {"command": case["query"]}).get("error") == "TOOL_NOT_ALLOWLISTED" for case in injections)
    abstention = [case for case in adversarial["cases"] if case["expected_scope"] in {"needs-clarification", "out-of-scope"}]
    return {
        "baseline_cases": len(baseline["cases"]),
        "retrieval_top1": {"correct": top1, "total": len(baseline["cases"]), "rate": top1 / max(1, len(baseline["cases"]))},
        "retrieval_top3": {"correct": top3, "total": len(baseline["cases"]), "rate": top3 / max(1, len(baseline["cases"]))},
        "adversarial_cases": len(adversarial["cases"]),
        "citation_precision_structural_test": {"correct_trusted_urls": sum(url == trusted["url"] for url in emitted), "emitted_urls": len(emitted), "rate": citation_precision},
        "prompt_injection_tools_fail_closed": {"blocked": fail_closed, "total": len(injections)},
        "expected_abstention_policy_cases": len(abstention),
        "live_model_refusal_rate": None,
        "note": "Metrics are offline contract tests. No live model inference, broad accuracy, or real-world refusal rate is measured."
    }


if __name__ == "__main__":
    print(json.dumps(evaluate(), ensure_ascii=False, indent=2))
