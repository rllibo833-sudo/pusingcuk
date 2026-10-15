(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.PusingCukAccountingCore = api;
})(typeof globalThis === "object" ? globalThis : this, function () {
  "use strict";
  function rupiahAmount(value) {
    if (value === null || value === undefined || value === "") return 0;
    const number = Number(value);
    if (!Number.isFinite(number)) throw new TypeError("Nominal harus berupa angka yang valid.");
    if (number < 0) throw new RangeError("Nominal Rupiah tidak boleh negatif.");
    const rounded = Math.round(number);
    if (!Number.isSafeInteger(rounded)) throw new RangeError("Nominal melampaui batas angka yang aman.");
    return rounded;
  }
  function migrateRows(rows) {
    const ids = new Map();
    let sequence = 1;
    return rows.map((row, index) => {
      const copy = { ...row };
      for (const key of ["d", "c"]) {
        try { copy[key] = rupiahAmount(copy[key]); } catch { copy[key] = 0; }
      }
      if (copy.transactionId !== undefined && String(copy.transactionId).trim()) {
        copy.transactionId = String(copy.transactionId).trim();
        return copy;
      }
      const date = String(copy.date || "").trim();
      const description = String(copy.desc || "").trim();
      const legacyKey = date && description ? `${date}\u0000${description}` : `row:${index}`;
      if (!ids.has(legacyKey)) ids.set(legacyKey, `TX-LEGACY-${String(sequence++).padStart(4, "0")}`);
      copy.transactionId = ids.get(legacyKey);
      return copy;
    });
  }
  function groupTransactions(rows) {
    const groups = new Map();
    rows.forEach((row, index) => {
      const transactionId = String(row.transactionId || "").trim() || `UNASSIGNED-${index + 1}`;
      if (!groups.has(transactionId)) groups.set(transactionId, { transactionId, debit: 0, credit: 0, lineCount: 0, issues: [] });
      const group = groups.get(transactionId);
      group.lineCount += 1;
      let debit, credit;
      try { debit = rupiahAmount(row.d); credit = rupiahAmount(row.c); }
      catch (error) { group.issues.push(error.message); return; }
      group.debit += debit;
      group.credit += credit;
      if (debit > 0 && credit > 0) group.issues.push(`Baris ${index + 1}: debit dan kredit terisi sekaligus.`);
      if (debit === 0 && credit === 0) group.issues.push(`Baris ${index + 1}: nominal masih kosong atau nol.`);
    });
    return Array.from(groups.values()).map(group => {
      const balanced = group.debit === group.credit && group.debit > 0 && group.issues.length === 0;
      return { ...group, difference: group.debit - group.credit, status: balanced ? "Seimbang" : "Periksa" };
    });
  }
  function accountBalances(rows, startDate, endDate) {
    const filtered = rows.filter(row => (!startDate || String(row.date || "") >= startDate) && (!endDate || String(row.date || "") <= endDate));
    const accounts = new Map();
    filtered.forEach(row => {
      const account = String(row.account || "Akun belum diisi");
      if (!accounts.has(account)) accounts.set(account, { account, cat: row.cat || "Aset", debit: 0, credit: 0 });
      const entry = accounts.get(account);
      entry.debit += rupiahAmount(row.d);
      entry.credit += rupiahAmount(row.c);
      entry.cat = row.cat || entry.cat;
    });
    return Array.from(accounts.values()).map(entry => ({ ...entry, balance: ["Aset", "Beban"].includes(entry.cat) ? entry.debit - entry.credit : entry.credit - entry.debit })).sort((a, b) => a.account.localeCompare(b.account, "id"));
  }
  return { rupiahAmount, migrateRows, groupTransactions, accountBalances };
});
