#!/usr/bin/env python3
"""
Mac系统监控应用程序
监控CPU、内存和网络使用情况
"""

import tkinter as tk
from tkinter import ttk, font
import psutil
import threading
import time
from datetime import datetime
import platform
from collections import deque
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation


class MacSystemMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("Mac系统监控器")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        # 设置应用图标和样式
        self.setup_styles()
        
        # 数据存储
        self.cpu_data = deque(maxlen=60)  # 保存60个数据点
        self.memory_data = deque(maxlen=60)
        self.network_sent_data = deque(maxlen=60)
        self.network_recv_data = deque(maxlen=60)
        
        # 网络统计基准值
        self.network_stats_base = psutil.net_io_counters()
        self.last_network_time = time.time()
        
        # 创建界面
        self.create_widgets()
        
        # 启动监控线程
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self.monitor_system, daemon=True)
        self.monitor_thread.start()
        
        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_styles(self):
        """设置应用样式"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 配置样式
        style.configure('Title.TLabel', font=('Helvetica', 16, 'bold'))
        style.configure('Info.TLabel', font=('Helvetica', 12))
        style.configure('Value.TLabel', font=('Helvetica', 14, 'bold'))
        
    def create_widgets(self):
        """创建界面组件"""
        # 主标题
        title_frame = ttk.Frame(self.root)
        title_frame.pack(pady=10, padx=20, fill='x')
        
        title_label = ttk.Label(title_frame, text="Mac系统监控器", style='Title.TLabel')
        title_label.pack()
        
        # 系统信息
        self.create_system_info()
        
        # 创建notebook用于标签页
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(pady=10, padx=20, fill='both', expand=True)
        
        # CPU监控标签页
        self.create_cpu_tab()
        
        # 内存监控标签页
        self.create_memory_tab()
        
        # 网络监控标签页
        self.create_network_tab()
        
        # 状态栏
        self.create_status_bar()
        
    def create_system_info(self):
        """创建系统信息显示区域"""
        info_frame = ttk.LabelFrame(self.root, text="系统信息", padding="10")
        info_frame.pack(pady=5, padx=20, fill='x')
        
        # 获取系统信息
        system_info = platform.uname()
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        
        info_text = f"系统: {system_info.system} {system_info.release}\n"
        info_text += f"处理器: {system_info.machine}\n"
        info_text += f"启动时间: {boot_time.strftime('%Y-%m-%d %H:%M:%S')}"
        
        info_label = ttk.Label(info_frame, text=info_text, style='Info.TLabel')
        info_label.pack(anchor='w')
        
    def create_cpu_tab(self):
        """创建CPU监控标签页"""
        cpu_frame = ttk.Frame(self.notebook)
        self.notebook.add(cpu_frame, text="CPU监控")
        
        # CPU信息显示区域
        cpu_info_frame = ttk.LabelFrame(cpu_frame, text="CPU使用情况", padding="10")
        cpu_info_frame.pack(pady=10, padx=10, fill='x')
        
        # CPU使用率标签
        self.cpu_usage_label = ttk.Label(cpu_info_frame, text="CPU使用率: 0%", style='Value.TLabel')
        self.cpu_usage_label.pack(anchor='w')
        
        # CPU核心数
        cpu_count = psutil.cpu_count(logical=False)
        logical_count = psutil.cpu_count(logical=True)
        cpu_info_text = f"物理核心数: {cpu_count}    逻辑核心数: {logical_count}"
        cpu_info_label = ttk.Label(cpu_info_frame, text=cpu_info_text, style='Info.TLabel')
        cpu_info_label.pack(anchor='w')
        
        # CPU进度条
        self.cpu_progress = ttk.Progressbar(cpu_info_frame, length=400, mode='determinate')
        self.cpu_progress.pack(pady=5, anchor='w')
        
        # CPU图表
        self.create_cpu_chart(cpu_frame)
        
    def create_memory_tab(self):
        """创建内存监控标签页"""
        memory_frame = ttk.Frame(self.notebook)
        self.notebook.add(memory_frame, text="内存监控")
        
        # 内存信息显示区域
        memory_info_frame = ttk.LabelFrame(memory_frame, text="内存使用情况", padding="10")
        memory_info_frame.pack(pady=10, padx=10, fill='x')
        
        # 内存使用率标签
        self.memory_usage_label = ttk.Label(memory_info_frame, text="内存使用率: 0%", style='Value.TLabel')
        self.memory_usage_label.pack(anchor='w')
        
        # 内存详细信息
        self.memory_detail_label = ttk.Label(memory_info_frame, text="", style='Info.TLabel')
        self.memory_detail_label.pack(anchor='w')
        
        # 内存进度条
        self.memory_progress = ttk.Progressbar(memory_info_frame, length=400, mode='determinate')
        self.memory_progress.pack(pady=5, anchor='w')
        
        # 内存图表
        self.create_memory_chart(memory_frame)
        
    def create_network_tab(self):
        """创建网络监控标签页"""
        network_frame = ttk.Frame(self.notebook)
        self.notebook.add(network_frame, text="网络监控")
        
        # 网络信息显示区域
        network_info_frame = ttk.LabelFrame(network_frame, text="网络使用情况", padding="10")
        network_info_frame.pack(pady=10, padx=10, fill='x')
        
        # 网络速度标签
        self.network_speed_label = ttk.Label(network_info_frame, text="", style='Value.TLabel')
        self.network_speed_label.pack(anchor='w')
        
        # 网络统计信息
        self.network_stats_label = ttk.Label(network_info_frame, text="", style='Info.TLabel')
        self.network_stats_label.pack(anchor='w')
        
        # 网络图表
        self.create_network_chart(network_frame)
        
    def create_cpu_chart(self, parent):
        """创建CPU使用率图表"""
        chart_frame = ttk.LabelFrame(parent, text="CPU使用率趋势", padding="10")
        chart_frame.pack(pady=10, padx=10, fill='both', expand=True)
        
        self.cpu_fig = Figure(figsize=(8, 3), dpi=100)
        self.cpu_ax = self.cpu_fig.add_subplot(111)
        self.cpu_ax.set_title("CPU使用率 (%)")
        self.cpu_ax.set_ylabel("使用率 (%)")
        self.cpu_ax.set_ylim(0, 100)
        self.cpu_fig.tight_layout()
        
        self.cpu_canvas = FigureCanvasTkAgg(self.cpu_fig, chart_frame)
        self.cpu_canvas.draw()
        self.cpu_canvas.get_tk_widget().pack(fill='both', expand=True)
        
    def create_memory_chart(self, parent):
        """创建内存使用率图表"""
        chart_frame = ttk.LabelFrame(parent, text="内存使用率趋势", padding="10")
        chart_frame.pack(pady=10, padx=10, fill='both', expand=True)
        
        self.memory_fig = Figure(figsize=(8, 3), dpi=100)
        self.memory_ax = self.memory_fig.add_subplot(111)
        self.memory_ax.set_title("内存使用率 (%)")
        self.memory_ax.set_ylabel("使用率 (%)")
        self.memory_ax.set_ylim(0, 100)
        self.memory_fig.tight_layout()
        
        self.memory_canvas = FigureCanvasTkAgg(self.memory_fig, chart_frame)
        self.memory_canvas.draw()
        self.memory_canvas.get_tk_widget().pack(fill='both', expand=True)
        
    def create_network_chart(self, parent):
        """创建网络使用率图表"""
        chart_frame = ttk.LabelFrame(parent, text="网络速度趋势", padding="10")
        chart_frame.pack(pady=10, padx=10, fill='both', expand=True)
        
        self.network_fig = Figure(figsize=(8, 3), dpi=100)
        self.network_ax = self.network_fig.add_subplot(111)
        self.network_ax.set_title("网络速度 (KB/s)")
        self.network_ax.set_ylabel("速度 (KB/s)")
        self.network_fig.tight_layout()
        
        self.network_canvas = FigureCanvasTkAgg(self.network_fig, chart_frame)
        self.network_canvas.draw()
        self.network_canvas.get_tk_widget().pack(fill='both', expand=True)
        
    def create_status_bar(self):
        """创建状态栏"""
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(side='bottom', fill='x', padx=20, pady=5)
        
        self.status_label = ttk.Label(self.status_frame, text="监控中...", style='Info.TLabel')
        self.status_label.pack(side='left')
        
        self.time_label = ttk.Label(self.status_frame, text="", style='Info.TLabel')
        self.time_label.pack(side='right')
        
    def format_bytes(self, bytes_value):
        """格式化字节数"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_value < 1024:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024
        return f"{bytes_value:.2f} TB"
        
    def monitor_system(self):
        """系统监控主循环"""
        while self.monitoring:
            try:
                # 获取CPU使用率
                cpu_percent = psutil.cpu_percent(interval=1)
                self.cpu_data.append(cpu_percent)
                
                # 获取内存信息
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
                self.memory_data.append(memory_percent)
                
                # 获取网络信息
                current_network = psutil.net_io_counters()
                current_time = time.time()
                time_delta = current_time - self.last_network_time
                
                if time_delta > 0:
                    sent_speed = (current_network.bytes_sent - self.network_stats_base.bytes_sent) / time_delta / 1024  # KB/s
                    recv_speed = (current_network.bytes_recv - self.network_stats_base.bytes_recv) / time_delta / 1024  # KB/s
                    
                    self.network_sent_data.append(sent_speed)
                    self.network_recv_data.append(recv_speed)
                    
                    self.network_stats_base = current_network
                    self.last_network_time = current_time
                
                # 更新界面
                self.root.after(0, self.update_ui, cpu_percent, memory, sent_speed if 'sent_speed' in locals() else 0, recv_speed if 'recv_speed' in locals() else 0)
                
            except Exception as e:
                print(f"监控错误: {e}")
                
            time.sleep(1)
            
    def update_ui(self, cpu_percent, memory, sent_speed, recv_speed):
        """更新用户界面"""
        try:
            # 更新CPU信息
            self.cpu_usage_label.config(text=f"CPU使用率: {cpu_percent:.1f}%")
            self.cpu_progress['value'] = cpu_percent
            
            # 更新内存信息
            self.memory_usage_label.config(text=f"内存使用率: {memory.percent:.1f}%")
            memory_detail = f"总内存: {self.format_bytes(memory.total)}    "
            memory_detail += f"已使用: {self.format_bytes(memory.used)}    "
            memory_detail += f"可用: {self.format_bytes(memory.available)}"
            self.memory_detail_label.config(text=memory_detail)
            self.memory_progress['value'] = memory.percent
            
            # 更新网络信息
            network_text = f"上传速度: {sent_speed:.2f} KB/s    下载速度: {recv_speed:.2f} KB/s"
            self.network_speed_label.config(text=network_text)
            
            # 更新网络统计
            net_stats = psutil.net_io_counters()
            stats_text = f"总发送: {self.format_bytes(net_stats.bytes_sent)}    "
            stats_text += f"总接收: {self.format_bytes(net_stats.bytes_recv)}"
            self.network_stats_label.config(text=stats_text)
            
            # 更新时间
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.time_label.config(text=f"更新时间: {current_time}")
            
            # 更新图表
            self.update_charts()
            
        except Exception as e:
            print(f"界面更新错误: {e}")
            
    def update_charts(self):
        """更新图表"""
        try:
            # 更新CPU图表
            if len(self.cpu_data) > 1:
                self.cpu_ax.clear()
                self.cpu_ax.plot(list(self.cpu_data), 'b-', linewidth=2)
                self.cpu_ax.set_title("CPU使用率 (%)")
                self.cpu_ax.set_ylabel("使用率 (%)")
                self.cpu_ax.set_ylim(0, 100)
                self.cpu_ax.grid(True, alpha=0.3)
                self.cpu_canvas.draw()
            
            # 更新内存图表
            if len(self.memory_data) > 1:
                self.memory_ax.clear()
                self.memory_ax.plot(list(self.memory_data), 'g-', linewidth=2)
                self.memory_ax.set_title("内存使用率 (%)")
                self.memory_ax.set_ylabel("使用率 (%)")
                self.memory_ax.set_ylim(0, 100)
                self.memory_ax.grid(True, alpha=0.3)
                self.memory_canvas.draw()
            
            # 更新网络图表
            if len(self.network_sent_data) > 1 and len(self.network_recv_data) > 1:
                self.network_ax.clear()
                self.network_ax.plot(list(self.network_sent_data), 'r-', linewidth=2, label='上传')
                self.network_ax.plot(list(self.network_recv_data), 'b-', linewidth=2, label='下载')
                self.network_ax.set_title("网络速度 (KB/s)")
                self.network_ax.set_ylabel("速度 (KB/s)")
                self.network_ax.legend()
                self.network_ax.grid(True, alpha=0.3)
                self.network_canvas.draw()
                
        except Exception as e:
            print(f"图表更新错误: {e}")
            
    def on_closing(self):
        """关闭应用程序"""
        self.monitoring = False
        self.root.destroy()


def main():
    """主函数"""
    # 检查是否在Mac系统上运行
    if platform.system() != 'Darwin':
        print("警告: 此应用程序专为Mac系统设计，但可以在其他系统上运行。")
    
    root = tk.Tk()
    app = MacSystemMonitor(root)
    root.mainloop()


if __name__ == "__main__":
    main()