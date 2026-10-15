const test = require("node:test");
const assert = require("node:assert/strict");
const core = require("./accounting-core.js");
const rules = require("./accounting-rules.generated.js");

test("aturan akuntansi yang dikompilasi dari .cuk dipakai sebagai modul JavaScript", () => {
  assert.deepEqual(rules.hitung_ringkasan(1250000, 300000, 4450000, 1500000, 2000000), [950000, 2950000, 0]);
  assert.deepEqual(rules.hitung_ringkasan(100, 125, 1000, 400, 300), [-25, 275, 325]);
});

test("menerima transaksi berpasangan yang seimbang", () => {
  const result = core.groupTransactions([{ transactionId: "TX-1", d: 1500, c: 0 }, { transactionId: "TX-1", d: 0, c: 1500 }]);
  assert.equal(result.length, 1); assert.equal(result[0].status, "Seimbang"); assert.equal(result[0].difference, 0);
});
test("menolak transaksi tidak seimbang walau total semua transaksi sama", () => {
  const result = core.groupTransactions([
    { transactionId: "TX-A", d: 100, c: 0 }, { transactionId: "TX-A", d: 0, c: 80 },
    { transactionId: "TX-B", d: 0, c: 100 }, { transactionId: "TX-B", d: 80, c: 0 }
  ]);
  assert.equal(result.reduce((sum, x) => sum + x.debit, 0), result.reduce((sum, x) => sum + x.credit, 0));
  assert.equal(result.find(x => x.transactionId === "TX-A").status, "Periksa");
  assert.equal(result.find(x => x.transactionId === "TX-B").status, "Periksa");
});
test("transaksi bernilai nol belum dianggap sah", () => assert.equal(core.groupTransactions([{ transactionId: "TX-0", d: 0, c: 0 }])[0].status, "Periksa"));
test("nominal negatif dan angka tidak valid ditolak", () => {
  assert.throws(() => core.rupiahAmount(-1), RangeError);
  assert.throws(() => core.rupiahAmount("bukan angka"), TypeError);
});
test("pembulatan nominal Rupiah ke bilangan bulat konsisten", () => {
  assert.equal(core.rupiahAmount(1.4), 1); assert.equal(core.rupiahAmount(1.5), 2); assert.equal(core.rupiahAmount(0), 0);
});
test("menolak nominal di luar rentang integer aman JavaScript", () => assert.throws(() => core.rupiahAmount(Number.MAX_SAFE_INTEGER + 2), RangeError));
test("satu baris yang mengisi debit dan kredit sekaligus tidak sah", () => {
  const result = core.groupTransactions([{ transactionId: "TX-BOTH", d: 100, c: 100 }]);
  assert.equal(result[0].status, "Periksa"); assert.ok(result[0].issues.some(issue => issue.includes("sekaligus")));
});
test("migrasi data lama mengelompokkan baris dengan tanggal dan keterangan sama", () => {
  const rows = core.migrateRows([
    { date: "2026-01-01", desc: "Setoran modal", d: 100, c: 0 },
    { date: "2026-01-01", desc: "Setoran modal", d: 0, c: 100 },
    { date: "2026-01-02", desc: "", d: 0, c: 0 }
  ]);
  assert.equal(rows[0].transactionId, rows[1].transactionId); assert.notEqual(rows[1].transactionId, rows[2].transactionId);
});
test("laporan akun dapat difilter menurut periode tanggal", () => {
  const rows = [
    { date: "2026-01-01", account: "Kas", cat: "Aset", d: 100, c: 0 },
    { date: "2026-02-01", account: "Kas", cat: "Aset", d: 200, c: 0 }
  ];
  assert.equal(core.accountBalances(rows, "2026-01-01", "2026-01-31")[0].balance, 100);
  assert.equal(core.accountBalances(rows, "2026-02-01", "2026-02-28")[0].balance, 200);
});
