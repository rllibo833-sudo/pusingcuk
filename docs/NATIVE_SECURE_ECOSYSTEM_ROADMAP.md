# Pusingcuk: Native Runtime, Secure Standard Library, and Ecosystem Migration

**Status:** Architecture proposal; implementation not yet complete  
**Target:** Pusingcuk becomes the primary application language for Founder-OS, kawasan-masjid-core, and kawasan-masjid-public  
**Baseline:** The main pipeline is Python-based; a C native runtime prototype exists.

## 1. Product definition

Pusingcuk is intended to become a beginner-friendly, production-oriented language for the Kawasan 1000 Hektar digital ecosystem: applications, APIs, data workflows, integrations, operational automation and bounded AI-agent tasks.

The long-term goal is that Python is not required to run or deploy Pusingcuk applications. Python may remain an optional migration/test tool during development, but must not be a hidden runtime dependency in the final toolchain.

This is a migration program, not a one-step rewrite. The existing Python implementation and tests remain the behavioral reference until native parity is demonstrated.

## 2. Non-negotiable principles

1. **Readable by default:** Indonesian-friendly keywords may remain; errors explain what failed, where, and how to fix it.
2. **One language across the stack:** CLI tools, APIs, background jobs, database access, migrations and agent workflows share one syntax and package format.
3. **Native execution:** the compiler/runtime executes Pusingcuk without requiring Python. A portable bytecode VM can support development; native binaries can follow.
4. **Secure by default:** no implicit file, process, network, secret, database or deployment access. A program receives only capabilities explicitly granted to it.
5. **Typed boundaries:** validated inputs, explicit errors, safe optional values, bounded resource use and parameterized SQL.
6. **Provider neutrality:** Supabase, database engines, AI vendors, hosting and payment systems are replaceable adapters, not language-level dependencies.
7. **Honest status:** distinguish specified, implemented, tested, independently reviewed and deployed. Never label a security feature complete without tests and review.
8. **Backward compatibility:** syntax changes require versioned specs, migration notes and regression tests.

## 3. Target architecture

~~~text
Pusingcuk source (.pusingcuk)
        |
        v
Lexer -> Parser -> AST -> Type/Effect Checker
        |                       |
        +----------+------------+
                   v
          Bytecode / Native backend
                   |
                   v
      Pusingcuk Runtime + Standard Library
       |        |        |        |
     HTTP      DB      Secrets   AI adapters
       |        |        |        |
       +--------+--------+--------+
                   |
       OS / network / external providers
       (only through granted capabilities)

Founder-OS (MEMORY) ---- decisions/specs/contracts
CORE (EXECUTION) ------- Pusingcuk services, agents, data, evidence
PUBLIC (PRESENTATION) -- Pusingcuk-powered public application
~~~

The compiler/runtime is shared, but each repository retains its purpose and data boundaries. Founder-OS is not a runtime database; PUBLIC must not contain privileged backend credentials.

## 4. Language design

- Lexer, parser and AST owned by Pusingcuk; no Python AST/eval/exec dependency.
- Variables, expressions, functions, lists/records, modules, imports and structured errors.
- Static type checking introduced gradually: Teks, Angka, Boolean, Daftar<T>, Hasil<T,E>, Mungkin<T>, records and typed function signatures.
- Explicit control flow, predictable evaluation order and defined numeric/string semantics.
- Resource limits: source size, nesting, call depth, memory, execution steps, output and time.
- Stable module/package format, lockfile and versioned standard library.
- Formatter, linter, test runner, package/build command and language-server support over time.

### Illustrative future syntax — not implemented yet

~~~pusingcuk
jancuk

fungsi salam(nama: Teks) -> Teks
    balek "Halo, " + nama
selesai fungsi

hedeh salam("Kawan")

selesai jancuk
~~~

A future database API should make authority and parameters visible instead of allowing arbitrary SQL strings or global credentials:

~~~pusingcuk
// Illustrative only; requires an explicitly granted database capability.
fungsi cari_proyek(db: DatabaseRead, id: UUID) -> Hasil<Proyek, DbError>
    balek db.proyek.ambil_dengan_id(id)
selesai fungsi
~~~

Exact keywords, type syntax and APIs must be decided in a versioned specification before implementation. These examples are not working features today.

## 5. Security model: default deny, explicit capabilities

Security cannot be promised absolutely. Pusingcuk must make unsafe actions difficult, visible, bounded and testable.

### Language/compiler controls
- No arbitrary code evaluation, shell escape, hidden imports or ambient global authority.
- Type-check external data after parsing/decoding; use explicit result and optional types instead of silent failure.
- Capability/effect checking: functions accessing network, files, database, secrets or process control must declare and receive that authority.
- Reject unknown syntax and malformed input safely; impose parser recursion and source-size limits.
- Dependency lockfiles, integrity hashes, package provenance and a policy for reviewing updates.

### Runtime controls
- Memory-safe implementation is the preferred long-term direction for production runtime/compiler; evaluate Rust for safety-critical components. The current C prototype is useful evidence but is not itself a security boundary.
- Bounds checks, checked arithmetic where appropriate, safe allocation/lifetime strategy, and fuzzing of parser/runtime entry points.
- Per-task limits for CPU/time, memory, recursion, I/O, output, concurrency and API calls.
- Run untrusted or AI-generated programs in OS-level isolation, such as dedicated low-privilege processes/containers with syscall/network restrictions where supported. Language checks alone are insufficient.
- No production secrets in source, logs, prompts, Git history or public bundles.
- Secrets arrive from a trusted runtime secret provider and are exposed only to authorized code, ideally as short-lived scoped handles.
- Default outbound network deny; allow only approved hosts/methods where the deployment platform supports enforcement.
- Structured audit events with secret redaction; avoid logging sensitive request bodies.

### Web/API/database controls
- HTTP framework with safe request parsing, body/size limits, request timeouts, rate limits, security headers and explicit routing.
- Authentication and authorization are separate. Enforce object/tenant ownership on every protected operation.
- SQL uses parameterized queries/prepared statements. Never build SQL by concatenating untrusted input.
- Database roles follow least privilege; row-level policies provide defense in depth where supported.
- Output encoding and safe template defaults reduce XSS; CSRF protection is needed where cookie-based browser sessions are used.
- Secure session/token handling, key rotation, webhook signature verification and replay protection.
- TLS verification enabled by default; no insecure certificate bypass in production mode.
- Threat model, dependency scanning, static checks, fuzzing, regression tests, secret scanning and external review before sensitive production use.

## 6. Standard library and replaceable adapters

Pusingcuk owns the stable interface and policy. Provider-specific implementations are adapters.

| Capability | Pusingcuk interface | Initial adapter strategy |
|---|---|---|
| Database | typed query, transaction, migration, result/error | PostgreSQL first; access Supabase through PostgreSQL or explicit HTTP adapter depending on current architecture |
| HTTP/API | server routes, client requests, validation, auth hooks | native HTTP implementation/library with bounded requests |
| Secrets | named scoped secret handles | environment/OS secret provider first; managed secret store later |
| AI | provider-neutral generate/stream/tool contract | Gemini if needed first; mock provider for tests; alternate providers later |
| Jobs | bounded jobs, retry policy, pause/resume | CORE-owned durable job interface |
| Logging | structured levels and redaction | stdout/stderr initially, replaceable sink |
| Files | explicit root-scoped read/write capabilities | denied unless granted; path traversal tests required |
| Web frontend | safe HTML/template or web target | server-rendered output first; browser code may still need JavaScript/WebAssembly or generated assets |

A language can provide native SQL syntax and safe database libraries without reinventing a database engine. Storage remains an external service until there is a compelling reason to build one.

API keys are not language features to hard-code. Pusingcuk should provide secure secret-access APIs while actual key storage stays outside source code.

## 7. Migration path — no big-bang rewrite

### Phase 0 — Freeze the contract
- Version the language specification and define what native means.
- Inventory Python dependencies, entry points, tests and the C prototype.
- Add a capability/security threat model and mark unsupported features.
- Protect existing tests and define one canonical test command.

**Exit criteria:** baseline documented and reproducible; no feature silently dropped.

### Phase 1 — Native interpreter parity
- Complete lexer/parser/AST/evaluator/runtime in the native toolchain.
- Keep Python as a test oracle only during transition, never as a native runtime dependency.
- Create shared golden fixtures that run against Python reference and native engine.
- Differential tests compare output, errors and exit codes; fuzz malformed input.

**Exit criteria:** every supported feature passes the same golden tests in native mode; native programs require no Python import or subprocess.

### Phase 2 — Memory-safe runtime and execution boundary
- Decide and document whether production runtime moves from C to Rust or uses another demonstrably safe strategy.
- Eliminate unbounded copies, unsafe list lifetime behavior and undefined behavior in the C prototype.
- Add per-program quotas and an OS-level isolation harness for untrusted code.
- Test malicious inputs, timeouts, resource exhaustion and denied capabilities.

**Exit criteria:** independent threat-model review and repeatable security regression suite. Ordinary unit tests alone are insufficient.

### Phase 3 — Type system and modules
- Add typed function signatures, records, optional/result types and module/import resolution.
- Introduce capability/effect declarations and compile-time rejection of unauthorized effects.
- Add dependency pinning, integrity verification and reproducible builds.

**Exit criteria:** capability violations are rejected before execution where statically knowable; runtime checks remain at trust boundaries.

### Phase 4 — Data and service stack
- Implement parameterized PostgreSQL access, migrations and transactions.
- Implement HTTP server/client, typed request validation and auth middleware.
- Implement secret handles and provider adapters.
- Test SQL injection, cross-tenant access, malformed HTTP requests, token leakage and quota failures.

**Exit criteria:** one real service runs in native Pusingcuk, uses a non-production database, and passes integration/security tests without Python in its runtime path.

### Phase 5 — First vertical slice in CORE
Build one bounded, low-risk capability end to end: validated API route -> authorization -> parameterized database query -> structured result -> audit evidence. Keep a rollback path to the existing implementation until parity and operational checks pass.

**Exit criteria:** tests, deployment, recovery and resource limits verified; no secret leakage; explicit owner and rollback.

### Phase 6 — Migrate the three repositories
1. **CORE first:** use Pusingcuk for a small service and internal automation, then expand by service boundaries.
2. **PUBLIC next:** move server-side routes/templates/build tasks to Pusingcuk where ready. Browser behavior may still need JavaScript/WebAssembly or generated assets; do not claim every browser can run without JavaScript.
3. **Founder-OS last:** migrate executable workflows and integrations. Preserve Markdown/docs and Git as durable memory; do not force every note into a database.
4. Keep adapters to current providers until replacements are tested. Remove a dependency only after a verified exit drill.

**Exit criteria:** each workload has parity evidence, operational owner, rollback plan and dependency list.

### Phase 7 — Production readiness
- Independent security review and remediation.
- SBOM, release signing/provenance, vulnerability response policy and reproducible builds.
- Backup/restore and provider-exit drills.
- Load, reliability, abuse and cost testing.
- Documented supported platforms and release channels.

**Exit criteria:** production approval is based on evidence and scoped risk, not a claim that a language is unhackable.

## 8. CI and acceptance gates

Every compiler/runtime pull request should run:
1. format/lint and compiler warnings as errors where practical;
2. unit and integration tests;
3. shared golden tests across reference/native engines;
4. malformed-input and fuzz regression corpus;
5. resource-limit/timeout tests;
6. static analysis and dependency/security scanning;
7. native builds on supported targets;
8. secret scanning and public artifact review.

Security-sensitive changes need focused review. A green CI job only proves the checks that actually ran.

## 9. First milestone

First deliverable: a **versioned native migration and security contract** plus a test inventory—not immediate edits across all three application repositories. It must identify:
- canonical engine and supported syntax/features;
- Python uses that are parser/runtime dependencies versus development tooling;
- native C features implemented and tested;
- security properties present versus planned;
- first workload safe to migrate.

Only after the baseline is confirmed should native database/HTTP/secret modules be built.

## 10. Definition of success

Pusingcuk succeeds when beginners can understand and build with it, experts can develop production services, the compiler/runtime runs without Python, integrations are replaceable, and permissions/security are explicit and testable.

The ecosystem migration succeeds when each workload runs on Pusingcuk because the native path has proven fit for that workload—not because the old path was deleted.

**Security statement:** Pusingcuk aims to reduce attack surface and prevent defined classes of vulnerabilities. It must never promise immunity from all cyberattacks.
