const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const si = require('systeminformation');

/**
 * Collects CPU, memory, and network metrics.
 * Returns values suitable for direct UI display.
 */
async function collectMetrics() {
  const [load, memory, netStats] = await Promise.all([
    si.currentLoad(),
    si.mem(),
    si.networkStats(),
  ]);

  const cpuLoadPercent = load.currentLoad; // 0..100

  const totalBytes = memory.total;
  const usedBytes = memory.used;
  const freeBytes = memory.free;
  const usedPercent = totalBytes > 0 ? (usedBytes / totalBytes) * 100 : 0;

  // Aggregate all interfaces
  const aggregated = (Array.isArray(netStats) ? netStats : [netStats]).reduce(
    (acc, n) => {
      acc.rx_sec += n.rx_sec || 0;
      acc.tx_sec += n.tx_sec || 0;
      acc.rx_bytes += n.rx_bytes || 0;
      acc.tx_bytes += n.tx_bytes || 0;
      return acc;
    },
    { rx_sec: 0, tx_sec: 0, rx_bytes: 0, tx_bytes: 0 }
  );

  return {
    cpu: { loadPercent: cpuLoadPercent },
    memory: {
      totalBytes,
      usedBytes,
      freeBytes,
      usedPercent,
    },
    network: {
      rxBytesPerSec: aggregated.rx_sec,
      txBytesPerSec: aggregated.tx_sec,
      totalRxBytes: aggregated.rx_bytes,
      totalTxBytes: aggregated.tx_bytes,
    },
    timestamp: Date.now(),
  };
}

function createMainWindow() {
  const win = new BrowserWindow({
    width: 420,
    height: 560,
    title: 'Mac Monitor',
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      preload: path.join(__dirname, 'preload.js'),
    },
  });

  win.setMenuBarVisibility(false);
  win.loadFile(path.join(__dirname, 'renderer', 'index.html'));
}

app.whenReady().then(() => {
  createMainWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createMainWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

ipcMain.handle('metrics:get', async () => {
  try {
    return await collectMetrics();
  } catch (error) {
    return { error: error instanceof Error ? error.message : String(error) };
  }
});

