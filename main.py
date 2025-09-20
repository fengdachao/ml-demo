#!/usr/bin/env python3

"""
Simple macOS-friendly system monitor showing CPU, memory, and network usage.

Run locally:
  python3 -m venv .venv && source .venv/bin/activate
  pip install -r requirements.txt
  python main.py

Optional: Build a macOS app bundle using PyInstaller (on macOS):
  pip install pyinstaller
  pyinstaller --noconfirm --windowed --name "Mac System Monitor" main.py
"""

from __future__ import annotations

import sys
import time
from dataclasses import dataclass
from typing import Optional

import psutil
import tkinter as tk
from tkinter import ttk


def format_bytes(num_bytes: float) -> str:
    """Return a human-readable byte size string."""
    if num_bytes < 0:
        num_bytes = 0
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    size = float(num_bytes)
    unit_index = 0
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    return f"{size:.2f} {units[unit_index]}"


def format_rate(num_bytes_per_sec: float) -> str:
    """Return a human-readable rate string, e.g., MB/s."""
    return f"{format_bytes(num_bytes_per_sec)}/s"


def format_percent(value: float) -> str:
    if value < 0:
        value = 0
    if value > 100:
        value = 100
    return f"{value:.1f}%"


@dataclass
class NetSnapshot:
    timestamp: float
    bytes_sent: int
    bytes_recv: int


class SystemMonitorApp:
    def __init__(self, tkinter_root: tk.Tk, update_interval_ms: int = 1000) -> None:
        self.root = tkinter_root
        self.root.title("Mac System Monitor")
        self.root.geometry("420x240")
        self.root.resizable(False, False)

        # macOS-friendly default theme
        self.style = ttk.Style()
        try:
            # Use 'clam' which looks decent cross-platform
            self.style.theme_use("clam")
        except Exception:
            pass

        self.update_interval_ms = update_interval_ms

        self.cpu_progress: Optional[ttk.Progressbar] = None
        self.cpu_value_label: Optional[ttk.Label] = None
        self.mem_progress: Optional[ttk.Progressbar] = None
        self.mem_value_label: Optional[ttk.Label] = None
        self.net_up_label: Optional[ttk.Label] = None
        self.net_down_label: Optional[ttk.Label] = None
        self.net_total_label: Optional[ttk.Label] = None

        self._prev_net: Optional[NetSnapshot] = None

        self._build_ui()
        self._schedule_update(initial=True)

    def _build_ui(self) -> None:
        container = ttk.Frame(self.root, padding=(16, 16, 16, 16))
        container.pack(fill=tk.BOTH, expand=True)

        # CPU Section
        cpu_frame = ttk.LabelFrame(container, text="CPU")
        cpu_frame.pack(fill=tk.X, expand=False, pady=(0, 12))

        self.cpu_progress = ttk.Progressbar(cpu_frame, orient=tk.HORIZONTAL, length=300, mode="determinate", maximum=100)
        self.cpu_progress.pack(side=tk.LEFT, padx=(12, 8), pady=10, fill=tk.X, expand=True)

        self.cpu_value_label = ttk.Label(cpu_frame, width=8, anchor=tk.E)
        self.cpu_value_label.pack(side=tk.RIGHT, padx=(8, 12))

        # Memory Section
        mem_frame = ttk.LabelFrame(container, text="Memory")
        mem_frame.pack(fill=tk.X, expand=False, pady=(0, 12))

        self.mem_progress = ttk.Progressbar(mem_frame, orient=tk.HORIZONTAL, length=300, mode="determinate", maximum=100)
        self.mem_progress.pack(side=tk.LEFT, padx=(12, 8), pady=10, fill=tk.X, expand=True)

        self.mem_value_label = ttk.Label(mem_frame, width=18, anchor=tk.E)
        self.mem_value_label.pack(side=tk.RIGHT, padx=(8, 12))

        # Network Section
        net_frame = ttk.LabelFrame(container, text="Network")
        net_frame.pack(fill=tk.BOTH, expand=True)

        net_row1 = ttk.Frame(net_frame)
        net_row1.pack(fill=tk.X, padx=12, pady=(10, 4))
        ttk.Label(net_row1, text="Upload:").pack(side=tk.LEFT)
        self.net_up_label = ttk.Label(net_row1, text="—")
        self.net_up_label.pack(side=tk.LEFT, padx=(6, 0))

        net_row2 = ttk.Frame(net_frame)
        net_row2.pack(fill=tk.X, padx=12, pady=(0, 4))
        ttk.Label(net_row2, text="Download:").pack(side=tk.LEFT)
        self.net_down_label = ttk.Label(net_row2, text="—")
        self.net_down_label.pack(side=tk.LEFT, padx=(6, 0))

        net_row3 = ttk.Frame(net_frame)
        net_row3.pack(fill=tk.X, padx=12, pady=(0, 10))
        ttk.Label(net_row3, text="Totals:").pack(side=tk.LEFT)
        self.net_total_label = ttk.Label(net_row3, text="—")
        self.net_total_label.pack(side=tk.LEFT, padx=(6, 0))

    def _schedule_update(self, initial: bool = False) -> None:
        # First network snapshot for baseline
        if initial and self._prev_net is None:
            self._prev_net = self._take_net_snapshot()
        self.root.after(self.update_interval_ms, self._update_metrics)

    def _update_metrics(self) -> None:
        # CPU
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
        except Exception:
            cpu_percent = 0.0
        if self.cpu_progress is not None:
            self.cpu_progress["value"] = cpu_percent
        if self.cpu_value_label is not None:
            self.cpu_value_label.configure(text=format_percent(cpu_percent))

        # Memory
        try:
            vm = psutil.virtual_memory()
            mem_percent = float(vm.percent)
            mem_used = vm.used
            mem_total = vm.total
        except Exception:
            mem_percent = 0.0
            mem_used = 0
            mem_total = 0
        if self.mem_progress is not None:
            self.mem_progress["value"] = mem_percent
        if self.mem_value_label is not None:
            self.mem_value_label.configure(
                text=f"{format_percent(mem_percent)}  {format_bytes(mem_used)} / {format_bytes(mem_total)}"
            )

        # Network
        try:
            current = self._take_net_snapshot()
            previous = self._prev_net
            if previous is not None:
                dt = max(1e-6, current.timestamp - previous.timestamp)
                up_rate = (current.bytes_sent - previous.bytes_sent) / dt
                down_rate = (current.bytes_recv - previous.bytes_recv) / dt
            else:
                up_rate = 0.0
                down_rate = 0.0
            self._prev_net = current
        except Exception:
            up_rate = 0.0
            down_rate = 0.0
            current = None  # type: ignore

        if self.net_up_label is not None:
            self.net_up_label.configure(text=format_rate(up_rate))
        if self.net_down_label is not None:
            self.net_down_label.configure(text=format_rate(down_rate))
        if self.net_total_label is not None:
            try:
                totals = psutil.net_io_counters()
                self.net_total_label.configure(
                    text=f"Sent {format_bytes(totals.bytes_sent)}  •  Recv {format_bytes(totals.bytes_recv)}"
                )
            except Exception:
                self.net_total_label.configure(text="—")

        # Schedule next update
        self._schedule_update()

    def _take_net_snapshot(self) -> NetSnapshot:
        counters = psutil.net_io_counters()
        return NetSnapshot(timestamp=time.monotonic(), bytes_sent=counters.bytes_sent, bytes_recv=counters.bytes_recv)


def main() -> int:
    root = tk.Tk()
    app = SystemMonitorApp(root)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())

