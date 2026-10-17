"use strict";
const { contextBridge, ipcRenderer } = require("electron");
contextBridge.exposeInMainWorld("cukAccountBridge", Object.freeze({
  request: (request) => ipcRenderer.invoke("cukaccount:request", request)
}));
