"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const runtime = require("../site/runtime.js");
const root = path.join(__dirname, "..", "site", "examples", "playground");
let count = 0;
for (const file of fs.readdirSync(root).filter(x => x.endsWith(".pusingcuk")).sort()) {
  const source = fs.readFileSync(path.join(root, file), "utf8");
  const expected = fs.readFileSync(path.join(root, file.replace(/\.pusingcuk$/, ".expected.txt")), "utf8").trimEnd();
  assert.equal(runtime.run(source).stdout.trimEnd(), expected, file + " browser output must match expected fixture");
  count++;
}
assert.ok(count >= 5, "expected a meaningful curated gallery");
function run(body) { return runtime.run("jancuk\n" + body + "\nselesai jancuk"); }
assert.equal(run("hedeh -7 // 3\nhedeh -7 % 3").stdout, "-3\n2\n");
assert.equal(run("hedeh salah dan (1 // 0 == 0)\nhedeh benar atau (1 // 0 == 0)").stdout, "tidak\nokelah\n");
assert.equal(run('lah x = {"nama":"Budi","items":[1,{"ok":benar}]}\nhedeh x["items"][1]["ok"]\nhedeh json.teks(x)').stdout, 'okelah\n{"nama":"Budi","items":[1,{"ok":true}]}\n');
const escapingSource = "jancuk\nhedeh html_aman(\"<b>&\\\"'\")\nhedeh csv_baris([\"Budi\",\"kopi, susu\",\"dia bilang \\\"hai\\\"\"])\nselesai jancuk";
assert.equal(runtime.run(escapingSource).stdout, "&lt;b&gt;&amp;&quot;&#x27;\nBudi,\"kopi, susu\",\"dia bilang \"\"hai\"\"\"\n");
assert.throws(() => run('hedeh json_baca("not json")'), /JSON|json|Unexpected token/);
assert.throws(() => runtime.run("jancuk\nhedeh missing_name\nselesai jancuk"), /nama belum didefinisikan/);
assert.throws(() => runtime.run("jancuk\nmumet benar\nlah x = 1\nselesai mumet\nselesai jancuk"), /batas eksekusi|10000 iterasi/);
assert.throws(() => runtime.run("jancuk\nhedeh globalThis.process.exit()\nselesai jancuk"));
assert.throws(() => runtime.run('jancuk\nhedeh "unclosed\nselesai jancuk'), /teks tidak boleh melewati baris|string belum ditutup/);
assert.equal(run("fungsi dobel(n)\nbalek n * 2\nselesai fungsi\nhedeh dobel(21)").stdout, "42\n", "function parameters and return values must work");
assert.equal(run("lah xs = [3, 4]\nxs[0] = 9\nhedeh xs[0]\nuntuk n dalam rentang(1, 4)\nhedeh n\nselesai untuk").stdout, "9\n1\n2\n3\n", "mutable indexes and bounded iteration must work");
const caught = run('coba\nhedeh 1 // 0\nketangkep err\nhedeh "tertangkap"\nakhirnya\nhedeh "final"\nselesai coba');
assert.equal(caught.stdout, "tertangkap\nfinal\n", "try/catch/finally must run handler and finalizer");
assert.throws(() => run("hedeh 1 +"), /mengharapkan|ekspresi tidak valid/, "incomplete expressions must report syntax errors");
assert.throws(() => run('hedeh json_teks({1: "x"})'), /kunci objek JSON harus teks/, "JSON must reject non-string object keys");
assert.throws(() => runtime.run('jancuk\nhedeh "x" * 65536\nselesai jancuk'), /output melebihi batas|hasil pengulangan terlalu besar/, "large output must be bounded");
assert.throws(() => runtime.run("x".repeat(65537)), /kode melewati batas/, "source byte limit must be enforced");
assert.throws(() => run("hedeh rentang(0, 10001)"), /10000 item/, "collection item limit must be enforced");
console.log("Browser runtime passed " + count + " gallery fixtures plus arithmetic, short-circuit, nested JSON, escaping, functions, mutable indexes, iteration, exception handling, malformed syntax, input validation, safety, and resource-limit tests.");
