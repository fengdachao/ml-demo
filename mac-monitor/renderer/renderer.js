function formatBytes(bytes) {
  if (!Number.isFinite(bytes)) return '--';
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  let value = bytes;
  let unitIndex = 0;
  while (value >= 1024 && unitIndex < units.length - 1) {
    value /= 1024;
    unitIndex += 1;
  }
  return `${value.toFixed(value >= 100 ? 0 : value >= 10 ? 1 : 2)} ${units[unitIndex]}`;
}

function formatRate(bytesPerSec) {
  if (!Number.isFinite(bytesPerSec)) return '--';
  const units = ['B/s', 'KB/s', 'MB/s', 'GB/s'];
  let value = bytesPerSec;
  let unitIndex = 0;
  while (value >= 1024 && unitIndex < units.length - 1) {
    value /= 1024;
    unitIndex += 1;
  }
  return `${value.toFixed(value >= 100 ? 0 : value >= 10 ? 1 : 2)} ${units[unitIndex]}`;
}

async function refresh() {
  try {
    const data = await window.system.getMetrics();
    if (data && !data.error) {
      document.getElementById('cpu-load').textContent = data.cpu.loadPercent.toFixed(1);

      document.getElementById('mem-total').textContent = formatBytes(data.memory.totalBytes);
      document.getElementById('mem-used').textContent = formatBytes(data.memory.usedBytes);
      document.getElementById('mem-percent').textContent = data.memory.usedPercent.toFixed(1);

      document.getElementById('rx-rate').textContent = formatRate(data.network.rxBytesPerSec);
      document.getElementById('tx-rate').textContent = formatRate(data.network.txBytesPerSec);
      document.getElementById('rx-total').textContent = formatBytes(data.network.totalRxBytes);
      document.getElementById('tx-total').textContent = formatBytes(data.network.totalTxBytes);

      const dt = new Date(data.timestamp);
      document.getElementById('updated').textContent = `${dt.toLocaleTimeString()}`;
    } else {
      document.getElementById('updated').textContent = `Error: ${data && data.error ? data.error : 'Unknown'}`;
    }
  } catch (err) {
    document.getElementById('updated').textContent = `Error: ${err instanceof Error ? err.message : String(err)}`;
  }
}

setInterval(refresh, 1000);
window.addEventListener('DOMContentLoaded', refresh);

