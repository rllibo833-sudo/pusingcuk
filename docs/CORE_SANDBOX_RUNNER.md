# CORE budget-rule sandbox runbook

## What this protects

The HTTP runner accepts only registered program IDs and hashes. It does not accept source code. Every .cuk execution uses the prebuilt Docker image; it fails closed if `PUSINGCUK_SANDBOX_IMAGE` is missing or is not an immutable local `sha256:<64 hex>` image ID.

The image builds two registered artifacts from fixed commits:
- `budget.threshold.v1`: runtime/source commit `e367f45b0a35ccb8fdb91424099b8046b346d77d`, source hash `e79058b314d921a4b4353133b30a7a7b0da64d32785a39f66cb5ce356406067d`.
- `budget.sufficiency.v1`: runtime/source commit `411c532454028d2d5e733373d085050eca1d402a`, source hash `d6fcee54d17afbf0fc0a1aee115b2c0c9f57dcc172e56a6c6cf1d0dd9a789771`.

The container runs with no network, read-only root, dropped capabilities, no-new-privileges, UID 65534, 64 MiB RAM/no swap, 0.5 CPU, 16-PID limit, 2 CPU-second and file/descriptor ulimits. The host runner enforces a hard timeout and output cap, kills the container on timeout/output overflow, and validates the exact allowed result set.

## Build and start locally

Requirements: Linux host with Docker Engine and permission to use its daemon. Do not run the runner on a shared/untrusted host.

```sh
sh tools/sandbox/build-image.sh
export PUSINGCUK_SANDBOX_IMAGE="$(docker image inspect --format '{{.Id}}' pusingcuk-core-sandbox:build)"
export PUSINGCUK_RUNNER_TOKEN="$(openssl rand -hex 32)"
PUSINGCUK_RUNNER_HOST=127.0.0.1 PUSINGCUK_RUNNER_PORT=8787 node tools/core-rule-runner.mjs
```

Keep the listener on loopback by default. Do not bind it to a public interface directly. For CORE remote use, place it behind a TLS reverse proxy or private network, preserve bearer-token authentication, rotate the token through the deployment secret store, and configure the CORE Edge Function secrets `PUSINGCUK_RUNNER_URL` (HTTPS base URL) and `PUSINGCUK_RUNNER_TOKEN`. Never put the runner token in PUBLIC, a repository, or the browser.

## Fail-closed behavior

- Missing/mutable image ID: runner refuses to start.
- Missing Docker daemon/image or failed container: request fails; CORE must not mark the rule successful.
- Hash, source commit, runtime build, sandbox attestation, image ID, elapsed time or result mismatch: CORE rejects the result evidence.
- Missing CORE runner URL/token: intake persists as `rule_pending`; no production rule execution is claimed.

## Verification

The PusingCuk GitHub Actions security regression builds the image from both immutable source commits, calls both registered rules over the authenticated local HTTP contract, tests hash/timeout/capability/auth failures, and checks that resource/isolation flags remain present. This CI is not proof that a production runner host or its secret configuration exists.
