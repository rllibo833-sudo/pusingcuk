"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const runtime = require("../site/runtime.js");
const html = fs.readFileSync(path.join(__dirname, "..", "site", "playground.html"), "utf8");
const inline = [...html.matchAll(/<script>([\\s\\S]*?)<\\/script>/g)].at(-1);
assert.ok(inline, "playground must include its controller script");
assert.match(html, /<script src="runtime\\.js"><\\/script>/, "runtime must be a local asset");
assert.doesNotMatch(inline[1], /\\beval\\s*\\(|new\\s+Function\\s*\\(/, "controller must not evaluate user source as host code");

class Element {
  constructor(id, value = "") {
    this.id = id;
    this.value = value;
    this.textContent = "";
    this.disabled = false;
    this.dataset = {};
    this.listeners = {};
    this.focused = false;
  }
  addEventListener(name, fn) { this.listeners[name] = fn; }
  click() { return this.listeners.click?.({ target: this }); }
  keydown(event) { return this.listeners.keydown?.(event); }
  input() { return this.listeners.input?.({ target: this }); }
  focus() { this.focused = true; }
}
const ids = {};
for (const id of ["sourceEditor", "exampleSelect", "runCode", "loadExample", "clearOutput", "output", "runStatus", "statusText", "sourceCount", "executionInfo"]) ids[id] = new Element(id);
ids.sourceEditor.value = 'jancuk\\n\\nlah nama = "Dunia"\\nhedeh "Halo, " + nama\\n\\nselesai jancuk';
ids.exampleSelect.value = "halo.pusingcuk";
const document = { getElementById(id) { assert.ok(ids[id], "unexpected DOM lookup: " + id); return ids[id]; } };
const context = { document, TextEncoder, encodeURIComponent, fetch: async () => ({ ok: true, status: 200, text: async () => 'jancuk\\nhedeh "contoh dimuat"\\nselesai jancuk' }) };
context.window = context;
context.PusingCukBrowser = runtime;
vm.runInNewContext(inline[1], context, { timeout: 1000, filename: "playground-controller.js" });
assert.equal(ids.output.textContent, "Halo, Dunia\\n", "initial editor content must execute");
assert.equal(ids.statusText.textContent, "Berhasil");
assert.match(ids.sourceCount.textContent, /byte$/);

ids.sourceEditor.value = "jancuk\\nhedeh 6 * 7\\nselesai jancuk";
ids.runCode.click();
assert.equal(ids.output.textContent, "42\\n", "Run button must execute current editor contents");
assert.equal(ids.statusText.textContent, "Berhasil");
assert.match(ids.executionInfo.textContent, /langkah/);

ids.sourceEditor.value = "jancuk\\nhedeh nama_yang_tidak_ada\\nselesai jancuk";
ids.runCode.click();
assert.match(ids.output.textContent, /nama belum didefinisikan/);
assert.equal(ids.statusText.textContent, "Perlu diperbaiki");
assert.equal(ids.runStatus.dataset.state, "error");

ids.sourceEditor.value = "jancuk\\nhedeh 9\\nselesai jancuk";
let prevented = false;
ids.sourceEditor.keydown({ ctrlKey: true, metaKey: false, key: "Enter", preventDefault() { prevented = true; } });
assert.equal(prevented, true, "Ctrl+Enter should suppress the editor newline");
assert.equal(ids.output.textContent, "9\\n", "Ctrl+Enter must execute the current program");

ids.clearOutput.click();
assert.equal(ids.output.textContent, "Output dibersihkan.");
assert.equal(ids.statusText.textContent, "Siap dijalankan");

(async () => {
  ids.exampleSelect.value = "halo.pusingcuk";
  await ids.loadExample.click();
  assert.equal(ids.sourceEditor.value, 'jancuk\\nhedeh "contoh dimuat"\\nselesai jancuk');
  assert.equal(ids.output.textContent, "Output dibersihkan.", "loading an example must not silently execute it");
  assert.equal(ids.statusText.textContent, "Contoh dimuat");
  assert.equal(ids.sourceEditor.focused, true);
  assert.equal(ids.loadExample.disabled, false);

  context.fetch = async () => ({ ok: false, status: 404, text: async () => "" });
  ids.sourceEditor.value = "kode lama";
  await ids.loadExample.click();
  assert.equal(ids.sourceEditor.value, "kode lama", "failed example load must preserve editor contents");
  assert.match(ids.output.textContent, /HTTP 404/);
  assert.equal(ids.statusText.textContent, "Gagal memuat contoh");
  assert.equal(ids.loadExample.disabled, false);
  console.log("Browser playground end-to-end controller passed: initial run, Run button, runtime error, Ctrl+Enter, clear output, successful example load, and failed-load preservation.");
})().catch(error => { console.error(error); process.exitCode = 1; });
