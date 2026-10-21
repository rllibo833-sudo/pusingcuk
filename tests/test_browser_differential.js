"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { spawnSync } = require("node:child_process");
const browser = require("../site/runtime.js");

const root = path.resolve(__dirname, "..");
const conformanceDir = path.join(root, "tests", "conformance");
const corpus = JSON.parse(fs.readFileSync(path.join(conformanceDir, "manifest.json"), "utf8"));
const selected = JSON.parse(fs.readFileSync(path.join(conformanceDir, "browser_manifest.json"), "utf8"));
assert.equal(selected.schema_version, 1, "browser manifest schema must be version 1");
const byId = new Map(corpus.fixtures.map(item => [item.id, item]));
assert.ok(selected.fixtures.length >= 50, "browser parity suite must cover at least 50 fixtures");
assert.equal(new Set(selected.fixtures).size, selected.fixtures.length, "browser manifest must not contain duplicate IDs");

function classifyReference(result) {
  if (result.status === null) return "harness_error";
  if (result.status === 0) return result.stderr ? "error" : null;
  const first = (result.stderr || "").trimStart().split(/\r?\n/, 1)[0] || "";
  if (first.includes("Kesalahan sintaks:")) return "syntax_error";
  if (first.includes("Kesalahan runtime:")) return "runtime_error";
  return "error";
}
function sourceLine(stderr) {
  let m = /\bBaris\s+(\d+)\b/i.exec(stderr || "");
  if (!m) m = /\[[^\]\n]*:(\d+):\d+\]/.exec(stderr || "");
  return m ? Number(m[1]) : null;
}
function runReference(sourcePath, stdin) {
  const result = spawnSync(process.env.PYTHON || "python", [path.join(root, "pusingcuk_new.py"), sourcePath], {
    cwd: root, input: stdin || "", encoding: "utf8", timeout: 8000, maxBuffer: 1024 * 1024
  });
  if (result.error) return { exit_code: null, stdout: result.stdout || "", stderr: String(result.error), stderr_class: "harness_error", source_line: null };
  return {
    exit_code: result.status,
    stdout: result.stdout || "",
    stderr: result.stderr || "",
    stderr_class: classifyReference(result),
    source_line: sourceLine(result.stderr || "")
  };
}
function runBrowser(source) {
  try {
    const result = browser.run(source);
    return { exit_code: 0, stdout: result.stdout, stderr_class: null, source_line: null };
  } catch (error) {
    const message = String(error && error.message || error);
    const isRuntime = /Kesalahan runtime pada baris/.test(message);
    return {
      exit_code: isRuntime ? 1 : 2,
      stdout: "",
      stderr_class: isRuntime ? "runtime_error" : "syntax_error",
      source_line: Number.isInteger(error && error.line) ? error.line : sourceLine(message)
    };
  }
}
function comparable(observation) {
  return {
    exit_code: observation.exit_code,
    stdout: observation.stdout,
    stderr_class: observation.stderr_class,
    source_line: observation.source_line
  };
}

const mismatches = [];
for (const id of selected.fixtures) {
  const item = byId.get(id);
  assert.ok(item, "browser manifest references unknown conformance fixture: " + id);
  assert.equal(item.runtimes.reference, "required", id + " must have a required reference result");
  const sourcePath = path.resolve(conformanceDir, item.source);
  assert.ok(sourcePath.startsWith(conformanceDir + path.sep), id + " source path must remain in conformance directory");
  const source = fs.readFileSync(sourcePath, "utf8");
  const reference = runReference(sourcePath, item.expected.stdin || "");
  const expected = {
    exit_code: item.expected.exit_code,
    stdout: item.expected.stdout,
    stderr_class: item.expected.stderr_class ?? null,
    source_line: item.expected.source_line ?? null
  };
  assert.deepEqual(comparable(reference), expected, id + " reference runtime must still match the pinned conformance contract");
  const actual = runBrowser(source);
  const refComparable = comparable(reference);
  const browserComparable = comparable(actual);
  try {
    assert.deepEqual(browserComparable, refComparable);
  } catch (error) {
    mismatches.push({ id, expected: refComparable, actual: browserComparable, error: error.message });
  }
}
if (mismatches.length) {
  console.error(JSON.stringify({ status: "fail", checked: selected.fixtures.length, mismatch_count: mismatches.length, mismatches }, null, 2));
  process.exitCode = 1;
} else {
  console.log("Browser differential parity passed: " + selected.fixtures.length + " fixtures match the Python reference on exit code, stdout, error class, and source line.");
}
