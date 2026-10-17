# SandboxOS Mobile Workspace — Product Contract

Status: product requirements / implementation not yet verified  
Target device: Android phone, browser-first; no laptop or desktop required for the user's workflow.  
Repository: `rllibo833-sudo/pusingcuk`, target branch: `warungpusingcuk`.

## Product promise

SandboxOS Mobile Workspace is the first usable surface of the future SandboxOS. It is not a mock chatbot or a static landing page. Its central capability is an AI coding agent that can create and modify real project files, work in the PusingCuk `.cuk` language, invoke approved compiler/check tools, read diagnostics, propose fixes, and show exactly what changed.

A browser workspace is a first milestone, not yet a bootable operating system. Do not describe it as a standalone OS until an actual bootable distribution exists.

## Core Android experience

The UI must be mobile-first and usable by a person who cannot code and has no PC:

- Project/file explorer with `.cuk` as the first-class language.
- Code editor with readable line numbers, clear unsaved/saved state, and a large touch target.
- PusingCuk AI chat with Indonesian instructions and plain-language explanations.
- Output/diagnostics panel with file, line, column, error explanation, and a suggested correction when available.
- Actions: **Buat kode**, **Perbaiki error**, **Periksa**, **Jalankan**, and **Lihat perubahan**.
- Project save/export and clear loading, empty, success, and failure states.
- Usable in a narrow Android viewport; no desktop-only multi-column layout requirement.

## AI must actually code

The AI coding workflow is:

1. User describes the task in Indonesian.
2. Agent inspects the current project and relevant language/specification context.
3. Agent proposes or writes actual `.cuk` file changes—not just a code snippet in chat.
4. The workspace shows a diff/preview and explains the change in simple Indonesian.
5. The compiler/check endpoint validates the candidate code and returns real diagnostics.
6. When validation fails, the agent uses those diagnostics to propose a bounded correction and repeats the check within a small configured limit.
7. The user can accept or reject the change. Running code, accessing files, installing packages, or publishing an app must never happen silently.
8. The result records which checks actually ran. Never display “success” for simulated or skipped checks.

Initial coding tasks should include: explain existing `.cuk`, generate a small program, edit a selected file, fix a compiler diagnostic, add a regression fixture, and explain a diff.

## Architecture boundaries

- **Workspace frontend:** project/file UI, editor, chat, diff, diagnostics, and user approvals.
- **PusingCuk AI adapter:** provider-neutral orchestration over existing PusingCuk AI; no provider secret in browser JavaScript.
- **Project tools:** allowlisted read/write operations scoped to the current workspace.
- **Compiler adapter:** call the actual supported `.cuk` check/compiler path and return structured diagnostics. Do not fabricate compiler results.
- **Execution adapter:** separate from code generation. Until an OS-level isolation boundary is implemented and verified, do not run arbitrary AI-generated code as if it were sandboxed.
- **Storage:** make saving/exporting behavior explicit. Do not silently sync project source or personal data to Supabase.
- **Future OS layer:** Android workspace first, then assess a Linux-based distribution. Do not build a kernel from scratch as the first milestone.

## Security and privacy requirements

- Never put Gemini/API/provider secrets in frontend files, browser storage, or Git.
- AI-generated source is untrusted until reviewed and checked.
- Do not expose the existing loopback-only experimental AI service to the public internet or bypass its token/bind restrictions to make the UI appear connected.
- Do not allow arbitrary shell commands, unrestricted filesystem paths, arbitrary network access, or silent package installation from an AI response.
- Require explicit user approval before applying substantial edits, executing code, or exporting/publishing an app.
- Use synthetic examples in tests; do not send private financial/accounting data to a model by default.
- Clearly label offline/local AI versus cloud AI and explain when a prompt/code leaves the device.

## Delivery gates

### Gate 1 — Android workspace shell
Mobile UI, file list/editor, chat layout, status panel, and project save/export behavior. Any unavailable backend capability must be visibly marked as unavailable, not simulated.

### Gate 2 — Real AI coding
Connect the UI to an approved server-side/local adapter. Demonstrate that a request creates or edits a real `.cuk` file and shows a reviewable diff. A chat response alone does not pass.

### Gate 3 — Real compiler feedback loop
Compile/check the candidate using the existing supported compiler path; show actual errors with locations; allow a bounded AI fix attempt; verify the corrected file with the same check. Keep a record of pass/fail and tool availability.

### Gate 4 — Safe execution and app packaging
Only after the execution isolation model is reviewed and tested. Packaging an APK or a bootable OS is a separate gate and must not be implied by a working browser workspace.

## Acceptance criteria

- A beginner can ask in Indonesian for a small `.cuk` program and receive an actual file change.
- The user can inspect and reject the change before it is applied.
- A deliberately broken program produces real compiler diagnostics, not a green fake success.
- AI can use a diagnostic to propose a correction and re-check it.
- If the AI provider or compiler is unavailable, the UI says so and preserves the user's work.
- No secret is required to be pasted into frontend code.
- Core UI actions work at Android phone width and are accessible by touch.
- Documentation and UI clearly distinguish implemented, experimental, and not-yet-available features.

## Implementation status — 2026-10-17

The product contract remains the acceptance target. A first partial implementation now exists in the SaaS workspace branch:

- `apps/pusingcuk-ai-saas/index.html`: mobile-friendly project picker, `.cuk` source editor, AI proposal action, compiler-check action, save action, and a visible before/after source preview.
- `apps/pusingcuk-ai-saas/server.py`: authenticated project listing/creation, per-user project-file read/write routes backed by the existing Supabase workspace tables, an AI proposal endpoint, and a compiler-check endpoint.
- `library/assistant.py`: the internal assistant accepts bounded workspace prompts up to 16 KiB; the public SaaS chat endpoint still enforces its separate 300-character limit.
- `tests/test_assistant.py` and `tests/test_pusingcuk_ai_saas.py`: regression checks cover the bounded prompt limit and the presence of the workspace wiring.

**Status: implemented in source, not yet verified end-to-end.** The AI proposal is shown in the editor and is not saved automatically. Saving requires an explicit user action. Compiler success means compile validation only, not runtime correctness. The workspace routes require the workspace Supabase migration to be applied to the correct project and a configured AI provider. No deployment, real-model request, live Supabase operation, or successful CI run is claimed by this status.

Still not implemented/proven:

- A runtime-level repair loop that passes the actual report from `tools/diagnostic_repair_loop.py` back into the model and reruns runtime/fixture checks.
- An operating-system-level execution sandbox for arbitrary generated code.
- APK packaging, a bootable SandboxOS distribution, and production deployment.

Keep the acceptance criteria above as gates. Do not label the whole workspace as complete until the relevant checks are run against a configured environment and the results are recorded.
