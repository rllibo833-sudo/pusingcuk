"use strict";
const { app, BrowserWindow, shell, ipcMain } = require("electron");
const path = require("node:path");
const { spawnSync } = require("node:child_process");
const fs = require("node:fs");

function createWindow() {
  const win = new BrowserWindow({
    width: 1180, height: 820, minWidth: 360, minHeight: 560,
    title: "CukAccount · PusingCuk UI Runtime", backgroundColor: "#f3f7f4",
    webPreferences: {
      preload: path.join(__dirname, "cuk-ui-preload.cjs"),
      contextIsolation: true, nodeIntegration: false, sandbox: true
    }
  });
  win.loadFile(path.join(__dirname, "dist", "index.html"));
  win.webContents.setWindowOpenHandler(({ url }) => {
    if (url.startsWith("https://")) shell.openExternal(url);
    return { action: "deny" };
  });
}

ipcMain.handle("cukaccount:request", (event, request) => {
  const frameUrl = event.senderFrame?.url || "";
  if (!frameUrl.startsWith("file://") || !frameUrl.endsWith("/dist/index.html")) {
    return { status: "rejected", diagnostic: { code: "CALLER_DENIED" } };
  }
  let encoded;
  try { encoded = JSON.stringify(request); } catch {
    return { status: "rejected", diagnostic: { code: "INVALID_REQUEST" } };
  }
  if (Buffer.byteLength(encoded, "utf8") > 65536) {
    return { status: "rejected", diagnostic: { code: "REQUEST_TOO_LARGE" } };
  }
  const root = path.resolve(__dirname, "../..");
  const database = path.join(app.getPath("userData"), "cukaccount.sqlite");
  fs.mkdirSync(path.dirname(database), { recursive: true });
  const python = process.env.PUSINGCUK_PYTHON || (process.platform === "win32" ? "python" : "python3");
  const run = spawnSync(python, [path.join(root, "apps/accounting/platform_bridge_cli.py")], {
    cwd: root, input: encoded, encoding: "utf8", timeout: 8000, maxBuffer: 65536,
    env: { PATH: process.env.PATH || "", CUKACCOUNT_DB: database, PYTHONIOENCODING: "utf-8" },
    windowsHide: true
  });
  if (run.error || run.status === null) {
    return { status: "rejected", diagnostic: { code: "BRIDGE_RUNTIME_UNAVAILABLE" } };
  }
  try {
    const response = JSON.parse(run.stdout || "{}");
    return response && typeof response === "object" ? response :
      { status: "rejected", diagnostic: { code: "INVALID_BRIDGE_RESPONSE" } };
  } catch {
    return { status: "rejected", diagnostic: { code: "INVALID_BRIDGE_RESPONSE" } };
  }
});

app.whenReady().then(() => {
  createWindow();
  app.on("activate", () => { if (BrowserWindow.getAllWindows().length === 0) createWindow(); });
});
app.on("window-all-closed", () => { if (process.platform !== "darwin") app.quit(); });
