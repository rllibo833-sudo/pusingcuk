# Pusingcuk Vision and Community Principles

## 1. What Pusingcuk is

Pusingcuk is an experimental, open programming-language project exploring how programming can feel more approachable through Indonesian-friendly wording, local slang, clear examples, and a community that welcomes different levels of experience.

The goal is not to replace established programming languages or claim that slang makes programming automatically easier. The goal is to create a place where beginners can learn, experienced engineers can experiment, and people from different language communities can contribute to a shared language project.

Pusingcuk is a work in progress. Runtime support, compiler targets, and security guarantees differ by feature. The project must describe those limits honestly.

## 2. Who should feel welcome

Pusingcuk welcomes:
- People who are new to programming and want to learn by reading or running small examples.
- Experienced developers, compiler engineers, testers, educators, designers, and security reviewers.
- People who use different programming languages and want to compare ideas across ecosystems.
- Contributors who speak Indonesian, regional languages, English, or other languages.
- People who contribute without writing implementation code, including documentation, translations, examples, reproducible bug reports, test cases, and design feedback.
- People using modest hardware, Android, or free tools.

No one needs to know every technical term to offer useful feedback. Technical changes still need appropriate tests and review; accessibility does not mean lowering correctness or security standards.

## 3. Language style: local roots, open doors

Pusingcuk uses informal Indonesian and slang as part of its identity. That style should invite curiosity, not become a barrier.

Principles:
1. **Canonical meaning first.** Every keyword and alias must have one documented meaning and consistent tests.
2. **Slang is optional.** Existing canonical syntax must remain understandable; slang aliases should not be required to learn the language.
3. **Local does not mean universal.** A word may be funny, friendly, offensive, or confusing in another region or language. Explain context and welcome respectful feedback.
4. **Gen Z and Gen Alpha are not one culture.** Do not assume a single slang list represents every young person, region, or country.
5. **Respectful by default.** Examples and community interactions must not target or demean people. Strong language may be part of the language's identity, but it should be clearly contextualized.
6. **International participation matters.** Keep the root README and core contributor instructions in English, while providing Indonesian and other community translations where possible.

Regional vocabulary packs, localized aliases, or configurable slang profiles are possible future ideas, not features that should be claimed as implemented today. Any proposal must consider parser ambiguity, compatibility, readability, and test coverage.

## 4. Source files and language ergonomics

New Pusingcuk source files use the canonical `.cuk` extension. The older `.pusingcuk` extension remains a compatibility path for existing projects, not a competing format. The extension is the public file identity; the language's distinctive identity must come from its Indonesian-readable syntax, explicit semantics, documented built-ins, and predictable diagnostics—not from the suffix alone. Examples, editor tooling, and tutorials should prefer `.cuk`. File-extension support never implies feature parity: runtimes must pass the same conformance fixtures for each feature they claim.

## 5. Design principles

- **Correctness before feature count.** Define semantics and tests before expanding the language surface.
- **One clear source of truth.** Keep the language specification, semantic contract, vocabulary registry, examples, and tests aligned.
- **Honest capability labels.** Distinguish implemented, tested, experimental, proposed, and unavailable features.
- **Portable foundations.** Keep core language behavior separate from host-specific APIs and compiler backends.
- **Offline-first by default.** The normal runtime should not require API keys, hosted services, or automatic external network access.
- **Security is explicit.** Compilation or bytecode execution is not automatically a sandbox. Host capabilities must be documented and tested.
- **Small, reviewable changes.** Prefer focused changes with clear reasons and regression tests over sweeping rewrites.
- **Learn in public.** Explain decisions in plain language and record important trade-offs so future contributors can understand them.

## 6. Ways to contribute

Contributions do not have to begin with compiler code.

### For beginners and non-coders
- Try a tutorial and report exactly where it becomes confusing.
- Suggest a clearer explanation or translate a page.
- Create a small program that demonstrates a real use case.
- Report a bug with steps to reproduce it and the output you observed.
- Propose a keyword or example, including its intended meaning and cultural context.
- Review whether a guide makes sense on a phone with limited tools.

### For engineers and technical contributors
- Add regression and conformance tests.
- Improve parser, interpreter, runtime, diagnostics, and compiler backends.
- Audit security boundaries, resource limits, and file operations.
- Improve type-system and standard-library contracts.
- Propose compatibility rules and test alternate implementations.
- Document limitations and provide evidence for support claims.

### For educators and language communities
- Review beginner learning paths.
- Contribute examples, exercises, translations, and regional-language feedback.
- Help evaluate whether terminology is clear, respectful, and understandable outside its original region.

See [CONTRIBUTING.md](../CONTRIBUTING.md), the [beginner guide](PEMULA.md), the [technical dictionary](DICTIONARY.md), and the [Indonesian dictionary](KAMUS_PUSINGCUK.md).

## 7. How decisions should be made

- Discuss the problem and intended outcome before large changes.
- Ask for examples, trade-offs, compatibility impact, security impact, and a way to test the proposal.
- Evaluate technical changes on evidence, not status, credentials, or how confidently someone uses jargon.
- Explain rejections respectfully and record important decisions in the relevant specification.
- Preserve experimental branches and user data unless there is a clear, reviewed reason to change them.
- No contributor is entitled to merge access, and no contributor should be pressured to surrender ownership of their work.

The project maintainer can set priorities and protect the repository, while technical reviewers help validate implementation decisions. This division allows the project to welcome expertise without making one person responsible for knowing everything.

## 8. Current phase and future direction

The current engineering goal is a dependable, understandable language with two maintained execution paths:

- **Python reference interpreter:** `pusingcuk_new.py` using the modular lexer, parser, and evaluator. This is the reference for intended language behavior.
- **Native C runtime:** `native/pusingcuk.c`, a standalone C11 implementation for a smaller, explicitly documented subset.

The language specification, semantic contract, vocabulary registry, and executable fixtures must agree. A feature may be called compatible across Python and C only when the same conformance fixture is required and passes on both. If a feature exists only in Python, document it as reference-only; do not silently treat it as native support.

For this phase, priority is given to:
1. Fixing mismatches in keywords, values, operators, errors, and documented built-ins.
2. Expanding and maintaining the shared Python/C conformance suite.
3. Keeping the CLI, Termux instructions, packaging, and developer tests reliable.
4. Keeping security and runtime limitations visible.

Transpiler backends, PVM work, and Android Studio APK development are deferred. Their source and design documents are retained as experiments, but they are not part of the supported baseline. A native executable build for Termux is distinct from building an Android application. CI cross-compilation is not a substitute for testing on a physical Termux device.

Database adapters, server/API tooling, frontend integration, WebAssembly, stable FFI/ABI, blockchain integrations, and configurable regional vocabulary remain future work unless a specific implementation and tests demonstrate otherwise.

Security limitations are documented in [SECURITY.md](../SECURITY.md) and the [security review guide](security/README.md). The current runtimes are not a general-purpose operating-system sandbox; do not run untrusted programs or bytecode with access to sensitive files or credentials.

## 9. A healthy measure of progress

Progress means that:
- More examples work consistently and have tests.
- New users can complete a tutorial without guessing.
- Error messages help people recover.
- The vocabulary registry and documentation match actual behavior.
- Contributors can understand the architecture and make focused changes.
- Bugs and security limitations are acknowledged and reduced.
- People can disagree, fork, experiment, and contribute without pressure to promote the project.

Pusingcuk should grow because it becomes more useful, understandable, and trustworthy—not because it makes exaggerated claims or chases popularity.

---

## Ringkasan Bahasa Indonesia

Pusingcuk ingin menjadi ruang belajar dan eksperimen bahasa pemrograman yang terbuka untuk pemula, engineer berpengalaman, pengajar, penguji, penerjemah, dan komunitas bahasa lokal maupun internasional.

Gaya Gen Z/Gen Alpha dan slang lokal adalah identitas, bukan syarat untuk ikut. Setiap kata harus punya arti yang jelas dan tes. Istilah lokal bisa punya arti berbeda di wilayah lain, jadi masukan budaya harus diterima dengan hormat. Profil kosakata daerah yang bisa dipilih masih berupa gagasan masa depan, bukan fitur yang sudah tersedia.

Kontribusi tidak harus berupa kode. Orang bisa membantu lewat dokumentasi, contoh, terjemahan, laporan bug, tes, dan kritik desain. Perubahan teknis tetap perlu bukti, tes, dan peninjauan. Pusingcuk harus jujur soal fitur yang sudah berjalan, eksperimental, direncanakan, dan belum tersedia.