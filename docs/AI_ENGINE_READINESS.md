# PusingCuk AI Engine: readiness and knowledge migration

**Status:** roadmap and acceptance contract; not a claim that a production service is deployed.

## Current boundary

The maintained AI entry point is an experimental local-first CLI. It delegates inference to a selected provider (local Ollama by default, Gemini only by explicit opt-in), performs deterministic lexical retrieval over a small curated index, appends citations from validated source records, keeps active chat history in process memory, and offers a small allowlisted tool registry. Explicit project notes can be saved to the user's local memory store.

This is an application/orchestrator, not a foundation model trained by PusingCuk. An authenticated loopback-only HTTP adapter now serves local clients, but there is no externally hosted production API or per-user identity/authorization yet. The language runtimes are not OS security sandboxes. Passing CI is evidence for tested contracts only; it is not proof of production availability, general answer quality, or safe execution of arbitrary programs.

The current runtime index (`library/knowledge_index.json`) contains **26 curated source records**, and the Indonesian retrieval regression contains **22 cases**. This small benchmark is regression evidence, not a broad accuracy score.

## Local integration service now available

`library/ai_service.py` provides a bounded authenticated HTTP adapter for local clients. It has loopback-only binding, bearer-token protection, duplicate-key rejection, bounded JSON input, per-session in-memory contexts, session/concurrency caps, generic provider errors and a liveness endpoint. Contract tests use a fake provider, so CI does not require a running model. This is a local integration surface, **not** an externally hosted production service; see [AI_LOCAL_SERVICE.md](AI_LOCAL_SERVICE.md).

## .cuk AI authoring contract (v1)

PusingCuk already has a maintained language pipeline: `lexer.py` → `parser.py` → `ast_nodes.py` → `evaluator.py`, plus the separately tested `native/pusingcuk.c` runtime. Do not create a second parser or introduce new reserved words just to describe AI behavior. Version 1 uses existing `.cuk` statements and data types as a small authoring convention:

- **Prompt/context:** a pure `fungsi` receives explicit context and question values and returns bounded text. Templates must not silently read memory, environment variables, or network resources.
- **Language-first implementation:** when asked to build application behavior, business rules, examples, or new solutions, PusingCuk AI should author the primary implementation in `.cuk`. Python/C/JavaScript are reserved for actual language-engine, compiler/backend, host-adapter, test-harness, or CI work. If `.cuk` lacks a required capability, identify the gap and extend the language/runtime with conformance fixtures instead of silently substituting a host-language implementation.
- **Deterministic rule:** a pure `fungsi` validates inputs and returns a stable enumerated result. The host validates input types/ranges before calling it. Rules do not get ambient capabilities.
- **Evidence status in `.cuk` AI checks:** `examples/ai/engine_contract.cuk` defines `status_bukti_kode` for compiler rejection, compile-only, runtime-tested success, runtime failure, and invalid host-supplied statuses. `library/ai_tools.py` exposes the stable `evidence_status` field from `cuk_compile_check`: successful compilation is `KOMPILASI_LOLOS_RUNTIME_BELUM_DIUJI`, invalid or empty input is `SOURCE_INPUT_TIDAK_VALID`, oversized input is `SOURCE_MELEBIHI_BATAS`, source rejected by the compiler is `SOURCE_DITOLAK_COMPILER`, and unexpected compiler failures are `STATUS_KOMPILASI_TIDAK_VALID`. Tests cover those host responses and the `.cuk` classification example. The field reports evidence available to the host; compile-check still does not execute or sandbox generated code.
- **Tool binding:** a `lah` dictionary records a stable tool ID, host handler ID, input fields, and declared capabilities. This is metadata, not automatic authority: only the existing host `ToolRegistry` may execute an explicitly allowlisted handler after schema validation.
- **Provider choice:** remains in the existing Python provider adapters; model selection is not encoded as an executable `.cuk` tool. Never place API keys or service credentials in source, context, or manifests.

Runnable example: [`examples/ai/engine_contract.cuk`](../examples/ai/engine_contract.cuk). It uses existing grammar only; it demonstrates a prompt builder, a pure output-review rule, and a declarative local knowledge-tool binding. The tool declaration does not itself invoke the host tool. First-class declarations such as `prompt ...`, `rule ...`, or `tool ...` should be considered only if the convention proves insufficient; any such grammar change must update the existing lexer/parser/AST/evaluator and required runtime conformance fixtures together.

## Existing project structure to extend, not duplicate

- Language frontend and Python runtime: `lexer.py`, `parser.py`, `ast_nodes.py`, `evaluator.py`, `pusingcuk_new.py`.
- Native runtime and cross-runtime evidence: `native/pusingcuk.c`, `tests/conformance/`, `tests/native/`, `tools/conformance.py`.
- AI orchestration and tools: `library/assistant.py`, `library/ai_tools.py`, `library/knowledge_grounding.py`, `library/local_memory.py`.
- Existing provider adapters: `library/local_ai_provider.py` (Ollama) and `library/gemini_ai_provider.py` (Gemini opt-in).
- Local service: `library/ai_service.py`; its current contract is loopback-only and experimental.
- User-facing executable contract example: `examples/ai/engine_contract.cuk`; its CLI test belongs in the existing `tests/test_examples_cuk.py`.

Do not create a second `pusingcuk_ai/`, parser, knowledge index, provider framework, or migration ledger. Split provider adapters into a subpackage only when a real implementation need justifies it. `budget_threshold` now maps through the internal `ToolRegistry` to the packaged, SHA-256-pinned `library/budget_threshold.cuk`; it no longer calls a localhost HTTP runner or needs a runner token, Node service, or Docker daemon. The legacy `tools/core-rule-runner.mjs` remains a separately tested compatibility/integration harness, not a runtime dependency of the local assistant. The Python-reference execution boundary is **not an OS sandbox** and may run only registered, fixed, reviewed artifacts—not model-generated source.

## Release gates

A release must not skip gates or turn a prototype into a production claim just because the code builds.

### Gate 0 — source and contract integrity

- All AI citations come only from validated immutable GitHub source envelopes.
- The curated runtime index contains reviewed PusingCuk-owned source paths only, has unique IDs, and pins each source URL to its exact path and commit.
- The index never crawls repositories, imports another repository at runtime, or treats retrieved text as instructions.
- The regression suite covers Indonesian retrieval, unrelated queries, source commit/path mismatch, invalid URLs, duplicate IDs, visibility, limits, and citation sanitization.
- Language-specific behavior remains owned by `SPEC.md`, `docs/SEMANTIC_CONTRACT.md`, builtin contracts, and executable conformance fixtures.

### Gate 1 — measurable answer quality and reliability

- The 22-case baseline currently yields top-1 21/21 and top-3 21/21 on its curated expected-source queries. On the 8 answerable adversarial cases, lexical retrieval yields top-1 5/8 and top-3 6/8. These small fixture metrics do not measure general answer quality or live-model behavior. `python tools/evaluate_live_ai.py --provider ollama` runs the same 12-case suite against an actual local model and prints heuristic clarification/refusal and structural citation metrics; `--provider gemini` requires `GEMINI_API_KEY`. The live script is opt-in and was not run as part of CI.
- Record expected source IDs and whether a question is answerable. The offline evaluator also tests structural citation precision (1/1 in its deliberately small link-injection test) and registry fail-closed response (2/2 prompt-injection tool requests blocked). Four adversarial cases are labeled as needing clarification/off-topic; actual live-model refusal remains unmeasured. Do not present these fixture metrics as broad accuracy.
- Add regressions for prompt injection inside retrieved documents, fabricated URLs, malformed/oversized provider responses, timeouts, quota/rate-limit responses, and repeated/invalid tool calls.
- Model output is not proof that a requested tool ran. Tool outcomes must come from validated tool responses and their citations must retain the trusted source envelope.

### Gate 2 — local service contract and hosted-service gate

The local adapter is implemented and tested for a versioned `POST /v1/chat` schema, bearer authentication, request IDs, 4 KiB request bound, bounded session/concurrency counts, duplicate-key rejection, generic errors, loopback-only binding, and ephemeral in-memory session context. `GET /healthz` reports process liveness only—not provider readiness. Details and limitations are in [AI_LOCAL_SERVICE.md](AI_LOCAL_SERVICE.md).

Not implemented as production guarantees: per-user identities/authorization and quotas, application-level abuse/rate controls, end-to-end cancellation/deadlines, streaming, graceful orchestration under SIGTERM, production metrics/alerts, TLS termination, backup/restore of durable service state, rollout/rollback automation, and an incident process. These must be designed and tested before public deployment. Keep provider-specific behavior behind an interface and do not blindly retry non-idempotent tool operations.

Never expose the local model adapter or registered-rule runner directly to the public internet. Gemini is explicit opt-in and sends prompt/context data to a third party. Provider adapters normalize timeout, 429/rate-limit, authentication, missing-model and malformed-response failures to stable non-sensitive error codes. See tests in `tests/test_local_ai_provider.py` and `tests/test_gemini_ai_provider.py`.

### Gate 3 — safe deterministic rule execution

- AI may select only a named, versioned registered rule and schema-valid input. It must not submit source code, shell commands, paths, environment variables, or arbitrary capabilities for execution.
- Each rule manifest pins an immutable program identifier, language version, SHA-256, entry point, allowed capabilities, input/output schema, and resource limits.
- Determinism means the same normalized input and rule version produce the same result on each runtime claimed as supported. Cover boundary, invalid, overflow, and error cases with shared fixtures.
- Portability is claimed only for runtimes that pass the same required fixtures. Keep a truthful capability matrix; never equate Python reference, native C, transpilers, and PVM without conformance evidence.
- Before any untrusted-code feature is considered, require OS-level isolation, network denial, a read-only filesystem, least privilege, CPU/memory/process/output/time limits, and adversarial testing. The current project runtime is not a general sandbox.

### Gate 3A — deterministic rule test evidence

The pure example `examples/core/priority_triage.cuk` now defines a bounded operations triage decision using urgency/impact integers from 1 to 5. Its fixture pins source SHA-256 and covers all four outputs plus invalid lower/upper bounds. It is exercised by the Python reference test and native C test target. This proves only this example's tested behavior on those two runtimes; it is not a registered hosted tool, and it is not an isolation boundary.

### Gate 4 — small opt-in pilot

Start with a narrow, non-sensitive workflow and explicit human review. Define success, failure, latency, cost/quota, and rollback thresholds before collecting results. No customer, uptime, security, or production-readiness claims without observed evidence. Expand scope only after the previous gate is green.

## Gradually absorbing Founder OS and CORE knowledge

Founder OS and CORE are **reference sources for reviewed decisions and patterns**, not runtime dependencies. See the [AI Engine knowledge migration ledger](AI_ENGINE_MIGRATION_LEDGER.md) for rewritten principles, immutable source pins, and remaining evidence gates. Their repositories must never be crawled wholesale. A migration entry should be added only after a maintainer has checked the primary document, determined that the information is relevant and safe to publish, and rewritten the transferable insight in PusingCuk's own words.

| Source area | Transferable subject | PusingCuk-owned destination | Acceptance evidence |
| --- | --- | --- | --- |
| Founder OS — durable decisions and boundaries | Decision status, explicit assumptions, ownership, provenance, and "No Proof, No Claim" discipline | AI policy/readiness docs and answer-grounding fixtures | Tests reject unsupported project claims and cite reviewed evidence |
| Founder OS — governance and recovery | Human approval for consequential actions, reversible operations, recovery notes with explicit opt-in | Assistant tool policy and local-memory tests | Unregistered/destructive actions fail closed; chat is not silently persisted |
| CORE — deterministic tool contracts | Named tools, version/hash pins, schema validation, bounded I/O, fail-closed behavior | `library/ai_tools.py`, rule manifests, runner tests | Invalid input/hash/version/capability never executes a rule |
| CORE — service operations and data boundaries | Authentication before actions, data minimization, auditable state transitions, no secret leakage | Future API/service layer; no import into current CLI merely for completeness | API contract, permission tests, secret-redaction tests, migration/restore evidence |
| CORE — masterplan/domain knowledge | Public-safe, factual domain material about Kawasan Masjid | Separate future domain corpus, not the language/engine index | Owner-reviewed source list and a domain-specific retrieval benchmark |

Do not copy code or lengthy document text from repositories unless its licensing and permissions clearly allow that. Prefer a short independently written summary with an immutable source citation, or independently implement the idea and test the behavior. Exclude credentials, private personal/financial material, unverified claims, and operational records from AI retrieval. A source citation proves where a claim came from; it does not prove the claim is true.

Each migrated source record must state: why it matters to PusingCuk, the exact immutable source path/commit, public-safe classification, the distilled principle, the test or acceptance check that makes it useful, and an owner for reevaluation. Remove a record if its evidence becomes obsolete or the acceptance test no longer holds. Keep the index curated and bounded.

## Prioritas ekstraksi selektif dari CORE

Ambil **pola yang reusable**, bukan layanan CORE atau riwayat operasionalnya. Kerjakan dalam urutan berikut; catat satu sumber primer dan satu tujuan PusingCuk untuk setiap aset yang benar-benar dipakai.

1. **P0 — aturan deterministik dan kontrak artefak.** Pelajari kontrak ID stabil, versi bahasa, hash sumber, skema input/output, batas ukuran/waktu, dan hasil enumerasi dari [kontrak runner PusingCuk yang sudah ada](integrations/CORE_TOOL_CONTRACT.md) serta contoh aturan milik PusingCuk. Tujuan: fungsi `.cuk` murni, manifest terdaftar, fixture bersama. Tidak menyalin service endpoint CORE.
2. **P1 — batas tool dan izin minimum.** Ambil pola allowlist tool, validasi skema, capability deny-by-default, pembatasan output, dan bukti hasil tool. Tujuan: `library/ai_tools.py` dan tes yang sudah ada; handler yang tidak terdaftar harus tetap gagal tertutup.
3. **P1 — provider dan penanganan kegagalan.** Ambil klasifikasi error autentikasi, model/endpoint tidak ditemukan, timeout, rate limit/kuota, dan cooldown/backoff. Tujuan: adapter Ollama/Gemini yang tidak saling bergantung; tes pakai provider tiruan agar tidak membutuhkan API berbayar.
4. **P2 — grounding dan provenance.** Ambil aturan kutipan sumber, validasi URL/commit/path, pembedaan bukti dari teks model, dan penanganan prompt injection dalam dokumen. Tujuan: indeks kecil milik PusingCuk; jangan crawl CORE/Founder-OS otomatis.
5. **P3 — pola operasional yang berguna untuk AI lokal.** Catat hanya pelajaran tentang retry terbatas, idempotensi, review manusia, dan redaksi rahasia jika benar-benar relevan. Tujuan: kebijakan dan implementasi lokal yang ditulis ulang, bukan memindahkan antrean/cron Supabase.
6. **Nanti atau tidak dimigrasikan — domain dan infrastruktur lama.** Materi masterplan yang aman untuk publik dapat masuk korpus domain terpisah setelah ada kebutuhan nyata. Tabel Supabase, Auth, pembayaran/webhook, data operasional pribadi, API key, notifikasi, cron, dan log historis bukan fitur inti bahasa/AI; arsipkan sebagai catatan sejarah atau pensiunkan, jangan salin ke runtime atau indeks AI.

Checklist penerimaan per aset:
- [ ] sumber primer dan commit/path spesifik tercatat;
- [ ] alasan relevansi dan klasifikasi aman untuk digunakan dicatat;
- [ ] prinsip ditulis ulang dalam istilah PusingCuk, tanpa menyalin rahasia atau data pribadi;
- [ ] perubahan runtime yang nyata punya tes/fixture yang membuktikan perilaku, bukan sekadar tes keberadaan teks;
- [ ] tidak ada fetch, import, indeks runtime, atau panggilan layanan ke repositori lama;
- [ ] bila aset tidak menambah kemampuan pengguna, hapus dari antrean migrasi.

Migrasi pengetahuan ini **bukan pelatihan bobot model**. Fine-tuning adalah proyek terpisah setelah ada dataset legal/aman, benchmark, anggaran komputasi, dan bukti bahwa prompt, aturan, atau retrieval tidak cukup.

## Source-repository deletion and cloud-resource boundary

Source-repository deletion is an owner decision; it is separate from retirement of deployed services and from data deletion. The owner has decided that Founder-OS and CORE are no longer development repositories needed by PusingCuk and reports that the old connections/keys have been removed. This repository review does not execute those GitHub deletions or independently verify provider-side secret revocation.

The transfer into PusingCuk is **selective**, not a byte-for-byte archive:

1. The live AI index is PusingCuk-owned and does not crawl either external repository.
2. The currently indexed source records and summaries preserve selected technical principles; they do not copy every source file, Git object, workflow run, issue, or historical decision.
3. Supabase stores its own database records and deployed resources, not the GitHub source tree or its complete commit history.
4. Deleting a GitHub repository does not automatically stop a Supabase Edge Function, cron job, webhook, external caller, or project. Those resources are managed separately.
5. Keep the PusingCuk language baseline and its current regression harness intact. Files with historic `CORE` naming inside this repository are not proof of a live connection; they remain only where an explicit regression workflow still tests them.

For PusingCuk development, the target state is no runtime/API-key/repository dependency on Founder-OS or CORE. If any legacy Supabase resource is later shut down, review its callers, required records, retention, export/restore, and external integrations independently of the GitHub repository deletion.

## Immediate acceptance target

Keep the 22-source curated index, 22-case baseline and 12-case adversarial corpus aligned by automated test. CI prints reproducible top-1/top-3 and structural safety metrics with `python tools/evaluate_knowledge_retrieval.py`. Maintain a non-contradictory grounding contract and document release gates. Live-model refusal and general response quality remain unmeasured; the AI Engine is not claimed production-ready.


## AI engine evidence-status regression

`examples/ai/engine_contract.cuk` is the language-owned source of the deterministic compile/runtime evidence labels. Regression tests execute it through both the Python reference interpreter and generated JavaScript, and require each supported status to appear in both outputs. A successful compile-check remains explicitly **not runtime proof**; only a separately observed runtime result may be labeled runtime-tested.


### Compile-check input rejection

The `cuk_compile_check` host boundary classifies empty/non-string source, embedded NUL, invalid UTF-8 encodability, and oversized source before compilation. Invalid source text consistently reports `SOURCE_INPUT_TIDAK_VALID`; source size is measured in UTF-8 bytes, with values above 16 KiB reporting `SOURCE_MELEBIHI_BATAS`. Regression tests cover malformed inputs and the byte-size boundary.
