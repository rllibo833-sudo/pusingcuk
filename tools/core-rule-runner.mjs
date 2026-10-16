#!/usr/bin/env node
/**
 * Local-only authenticated gateway for fixed PusingCuk programs.
 * All rule execution fails closed unless routed through the prebuilt, digest-pinned
 * Docker sandbox. The caller can select only registered program IDs, never source.
 */
import crypto from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { spawn } from "node:child_process";
import { createServer } from "node:http";

const PINNED_COMMIT = "e367f45b0a35ccb8fdb91424099b8046b346d77d";
const LANGUAGE_VERSION = "0.6-dev";
const RUNTIME_VERSION = "Pusingcuk native 0.8.0.dev0";
const CONTRACT_VERSION = "pusingcuk.core.tool.v1";
const SOURCE_PATH = "examples/core/anggaran_threshold_service.cuk";
const PROGRAMS = new Map([
  ["budget.threshold.v1", {
    sha256: "e79058b314d921a4b4353133b30a7a7b0da64d32785a39f66cb5ce356406067d",
    source_commit: PINNED_COMMIT, language_version: LANGUAGE_VERSION, entrypoint: "status_anggaran",
    safe_results: ["DALAM_BATAS", "PERLU_PERSETUJUAN", "INPUT_TIDAK_VALID"],
  }],
  ["budget.sufficiency.v1", {
    sha256: "d6fcee54d17afbf0fc0a1aee115b2c0c9f57dcc172e56a6c6cf1d0dd9a789771",
    source_commit: "411c532454028d2d5e733373d085050eca1d402a",
    language_version: LANGUAGE_VERSION, entrypoint: "cek_kecukupan_saldo",
    safe_results: ["SALDO_CUKUP", "SALDO_TIDAK_CUKUP", "INPUT_TIDAK_VALID"],
  }],
]);
const MAX_BODY_BYTES = 4096;
const MAX_OUTPUT_BYTES = 1024;
const MAX_INPUT_NUMBER = 1_000_000_000_000;
const RUN_TIMEOUT_MS = 3000;
const MAX_CONCURRENCY = 2;

function runGit(cwd, args) {
  return execFileSync("git", args, { cwd, encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] }).trim();
}

function pinnedSourceRoot() {
  const configured = process.env.PUSINGCUK_SOURCE_ROOT;
  if (configured) {
    const root = path.resolve(configured);
    if (runGit(root, ["rev-parse", "HEAD"]) !== PINNED_COMMIT) {
      throw new Error("PUSINGCUK_SOURCE_ROOT must be checked out at the pinned runtime commit.");
    }
    if (runGit(root, ["status", "--porcelain"])) {
      throw new Error("PUSINGCUK_SOURCE_ROOT must have a clean worktree before building the pinned runtime.");
    }
    return root;
  }

  const root = fs.mkdtempSync(path.join(os.tmpdir(), "pusingcuk-pinned-"));
  execFileSync("git", ["init", root], { stdio: "ignore" });
  runGit(root, ["remote", "add", "origin", "https://github.com/rllibo833-sudo/pusingcuk.git"]);
  runGit(root, ["fetch", "--depth", "1", "origin", PINNED_COMMIT]);
  runGit(root, ["checkout", "--detach", "FETCH_HEAD"]);
  if (runGit(root, ["rev-parse", "HEAD"]) !== PINNED_COMMIT) {
    throw new Error("Pinned PusingCuk source revision mismatch.");
  }
  return root;
}

function digestFile(filename) {
  return crypto.createHash("sha256").update(fs.readFileSync(filename)).digest("hex");
}

function buildRuntime(root) {
  const rule = path.join(root, SOURCE_PATH);
  if (!fs.existsSync(rule) || digestFile(rule) !== PROGRAMS.get("budget.threshold.v1").sha256) {
    throw new Error("Pinned registered .cuk artifact failed its SHA-256 check.");
  }

  const binary = path.join(root, "pusingcuk-native");
  execFileSync("make", ["native", "CC=gcc", `NATIVE_BIN=${binary}`], {
    cwd: root,
    stdio: "inherit",
    timeout: 120_000,
    env: { PATH: process.env.PATH || "/usr/bin:/bin", LANG: "C.UTF-8" },
  });
  const version = execFileSync(binary, ["--version"], {
    encoding: "utf8",
    timeout: 1000,
    env: { PATH: process.env.PATH || "/usr/bin:/bin", LANG: "C.UTF-8" },
  }).trim();
  if (version !== RUNTIME_VERSION) throw new Error("Native PusingCuk runtime version mismatch.");
  return { root, rule, binary, version };
}

function authorized(req, token) {
  const header = req.headers.authorization || "";
  const given = header.startsWith("Bearer ") ? header.slice(7) : "";
  const left = Buffer.from(given);
  const right = Buffer.from(token);
  return left.length === right.length && crypto.timingSafeEqual(left, right);
}

function send(res, status, payload) {
  const body = JSON.stringify(payload);
  res.writeHead(status, {
    "Content-Type": "application/json; charset=utf-8",
    "Cache-Control": "no-store",
    "X-Content-Type-Options": "nosniff",
    "Content-Length": Buffer.byteLength(body),
  });
  res.end(body);
}

function readJson(req) {
  return new Promise((resolve, reject) => {
    let size = 0;
    const chunks = [];
    req.on("data", (chunk) => {
      size += chunk.length;
      if (size > MAX_BODY_BYTES) {
        reject(new Error("BODY_TOO_LARGE"));
        req.destroy();
        return;
      }
      chunks.push(chunk);
    });
    req.on("end", () => {
      try { resolve(JSON.parse(Buffer.concat(chunks).toString("utf8"))); }
      catch { reject(new Error("INVALID_JSON")); }
    });
    req.on("error", () => reject(new Error("REQUEST_READ_FAILED")));
  });
}

function validateRequest(body) {
  if (!body || typeof body !== "object" || Array.isArray(body)) return "INVALID_CONTRACT";
  if (body.contract_version !== CONTRACT_VERSION) return "INVALID_CONTRACT";
  if (typeof body.request_id !== "string" || !/^[0-9a-f-]{36}$/i.test(body.request_id)) return "INVALID_CONTRACT";
  const program = PROGRAMS.get(body.program_id);
  if (!program) return "UNKNOWN_PROGRAM";
  if (body.program_sha256 !== program.sha256) return "ARTIFACT_HASH_MISMATCH";
  if (body.language_version !== program.language_version || body.entrypoint !== program.entrypoint) return "INVALID_CONTRACT";
  if (!Array.isArray(body.capabilities) || body.capabilities.length !== 0) return "CAPABILITY_DENIED";
  if (!body.limits || typeof body.limits !== "object") return "INVALID_CONTRACT";
  if (
    !Number.isInteger(body.limits.timeout_ms) || body.limits.timeout_ms < 1 ||
    body.limits.timeout_ms > RUN_TIMEOUT_MS ||
    !Number.isInteger(body.limits.input_bytes) || body.limits.input_bytes < 1 ||
    body.limits.input_bytes > 128 ||
    !Number.isInteger(body.limits.output_bytes) || body.limits.output_bytes < 1 ||
    body.limits.output_bytes > MAX_OUTPUT_BYTES
  ) return "RESOURCE_LIMIT";

  const input = body.input;
  if (!input || typeof input !== "object" || Array.isArray(input)) return "INVALID_INPUT";
  if (Object.keys(input).some((key) => !["nominal", "batas"].includes(key))) return "INVALID_INPUT";
  for (const key of ["nominal", "batas"]) {
    if (
      !Number.isSafeInteger(input[key]) ||
      Math.abs(input[key]) > MAX_INPUT_NUMBER
    ) return "INVALID_INPUT";
  }
  return null;
}

function runRule(runtime, input, timeoutMs, programId) {
  return new Promise((resolve) => {
    const program = PROGRAMS.get(programId);
    const image = process.env.PUSINGCUK_SANDBOX_IMAGE;
    const started = Date.now();
    const cidfile = path.join(os.tmpdir(), `pusingcuk-sandbox-${crypto.randomUUID()}.cid`);
    let stdout = "";
    let stderr = "";
    let finished = false;
    const args = [
      "run", "-i", "--rm", "--pull=never", "--cidfile", cidfile,
      "--network=none", "--memory=64m", "--memory-swap=64m", "--cpus=0.5",
      "--pids-limit=16", "--read-only", "--cap-drop=ALL",
      "--security-opt=no-new-privileges", "--user=65534:65534",
      "--tmpfs", "/tmp:rw,noexec,nosuid,nodev,size=1m",
      "--ulimit", "cpu=2:2", "--ulimit", "fsize=1024:1024",
      "--ulimit", "nofile=32:32", "--env", `PROGRAM_ID=${programId}`, image,
    ];
    const child = spawn("docker", args, { shell: false, stdio: ["pipe", "pipe", "pipe"] });
    const killSandbox = () => {
      try {
        const containerId = fs.readFileSync(cidfile, "utf8").trim();
        if (/^[0-9a-f]{64}$/.test(containerId)) {
          execFileSync("docker", ["kill", containerId], { stdio: "ignore", timeout: 1000 });
        }
      } catch { /* Container may not have been created yet. */ }
      try { child.kill("SIGKILL"); } catch { /* Process may already be gone. */ }
    };
    const finish = (result) => {
      if (finished) return;
      finished = true;
      clearTimeout(timer);
      try { fs.unlinkSync(cidfile); } catch { /* cidfile may not exist. */ }
      resolve({ ...result, elapsed_ms: Date.now() - started });
    };
    const timer = setTimeout(() => {
      killSandbox();
      finish({ status: "timed_out", diagnostics: { code: "TIMEOUT", message: "Sandbox execution timed out." } });
    }, timeoutMs);

    child.stdout.on("data", (chunk) => {
      stdout += chunk.toString("utf8");
      if (Buffer.byteLength(stdout) > MAX_OUTPUT_BYTES) {
        killSandbox();
        finish({ status: "resource_limited", diagnostics: { code: "RESOURCE_LIMIT", message: "Sandbox output limit exceeded." } });
      }
    });
    child.stderr.on("data", (chunk) => {
      if (Buffer.byteLength(stderr) < 1024) stderr += chunk.toString("utf8").slice(0, 1024);
    });
    child.on("error", () => finish({ status: "failed", diagnostics: { code: "SANDBOX_UNAVAILABLE", message: "Docker sandbox process could not start." } }));
    child.on("close", (code) => {
      if (finished) return;
      const result = stdout.trim();
      if (code !== 0 || !program.safe_results.includes(result)) {
        console.error("Registered sandbox rule failed", { programId, exitCode: code, stderr: stderr.slice(0, 256), outputBytes: Buffer.byteLength(stdout) });
        finish({ status: "failed", diagnostics: { code: "SANDBOX_EXECUTION_FAILED", message: "Registered rule failed inside the OS sandbox." } });
        return;
      }
      finish({ status: "succeeded", result });
    });
    child.stdin.end(`${input.nominal}\n${input.batas}\n`);
  });
}

const token = process.env.PUSINGCUK_RUNNER_TOKEN || "";
if (token.length < 32) {
  console.error("Set PUSINGCUK_RUNNER_TOKEN to a random value of at least 32 characters.");
  process.exit(2);
}

const sandboxImage = process.env.PUSINGCUK_SANDBOX_IMAGE || "";
if (!/^sha256:[0-9a-f]{64}$/.test(sandboxImage)) {
  console.error("Set PUSINGCUK_SANDBOX_IMAGE to the immutable sha256 image ID printed by tools/sandbox/build-image.sh.");
  process.exit(2);
}

const host = process.env.PUSINGCUK_RUNNER_HOST || "127.0.0.1";
if (!["127.0.0.1", "localhost", "::1", "0.0.0.0"].includes(host)) {
  console.error("Runner host must be loopback; 0.0.0.0 is allowed only for a protected local Docker bridge.");
  process.exit(2);
}
const port = Number(process.env.PUSINGCUK_RUNNER_PORT || "8787");
if (!Number.isInteger(port) || port < 1024 || port > 65535) {
  console.error("PUSINGCUK_RUNNER_PORT must be an unprivileged TCP port.");
  process.exit(2);
}

const runtime = buildRuntime(pinnedSourceRoot());
let activeRuns = 0;
const server = createServer(async (req, res) => {
  if (req.method === "GET" && req.url === "/health") {
    return send(res, 200, { ok: true, runtime_version: runtime.version, runtime_build_sha: PINNED_COMMIT, sandbox: "docker-isolated", sandbox_image: sandboxImage, registered_programs: [...PROGRAMS.keys()] });
  }
  if (req.method !== "POST" || req.url !== "/v1/execute") {
    return send(res, 404, { error: "NOT_FOUND" });
  }
  if (!authorized(req, token)) return send(res, 401, { error: "UNAUTHORIZED" });
  const length = Number(req.headers["content-length"] || 0);
  if (length > MAX_BODY_BYTES) return send(res, 413, { error: "RESOURCE_LIMIT" });

  let body;
  try { body = await readJson(req); }
  catch (error) {
    return send(res, error?.message === "BODY_TOO_LARGE" ? 413 : 400, {
      error: error?.message === "BODY_TOO_LARGE" ? "RESOURCE_LIMIT" : "INVALID_INPUT",
    });
  }

  const validationError = validateRequest(body);
  if (validationError) return send(res, 400, { error: validationError });
  if (activeRuns >= MAX_CONCURRENCY) return send(res, 503, { error: "RESOURCE_LIMIT" });

  activeRuns += 1;
  try {
    const program = PROGRAMS.get(body.program_id);
    const result = await runRule(runtime, body.input, body.limits.timeout_ms, body.program_id);
    return send(res, result.status === "succeeded" ? 200 : 422, {
      contract_version: CONTRACT_VERSION,
      request_id: body.request_id,
      program_id: body.program_id,
      program_sha256: program.sha256,
      source_commit: program.source_commit,
      runtime_version: runtime.version,
      runtime_build_sha: program.source_commit,
      sandbox: "docker-isolated",
      sandbox_image: sandboxImage,
      status: result.status,
      ...(result.status === "succeeded" ? { result: result.result } : { diagnostics: result.diagnostics }),
      elapsed_ms: result.elapsed_ms,
    });
  } finally {
    activeRuns -= 1;
  }
});

server.listen(port, host, () => {
  console.log(`PusingCuk local rule runner listening on ${host}:${port}`);
  console.log(`Pinned source: ${PINNED_COMMIT}; registered programs: ${[...PROGRAMS.keys()].join(", ")}`);
  if (host === "0.0.0.0") {
    console.warn("WARNING: binding to all interfaces. Protect with a firewall and the runner token; never expose this port to the public internet.");
  }
});
