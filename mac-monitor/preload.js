const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('system', {
  getMetrics: () => ipcRenderer.invoke('metrics:get'),
});

