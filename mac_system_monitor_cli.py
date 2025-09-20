#!/usr/bin/env python3
"""
Mac系统监控应用程序 - 命令行版本
监控CPU、内存和网络使用情况
"""

import psutil
import time
import os
import platform
from datetime import datetime


class MacSystemMonitorCLI:
    def __init__(self):
        self.network_stats_base = psutil.net_io_counters()
        self.last_network_time = time.time()
        
    def clear_screen(self):
        """清屏"""
        os.system('clear' if os.name == 'posix' else 'cls')
        
    def format_bytes(self, bytes_value):
        """格式化字节数"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_value < 1024:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024
        return f"{bytes_value:.2f} TB"
        
    def get_system_info(self):
        """获取系统信息"""
        system_info = platform.uname()
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        
        return {
            'system': f"{system_info.system} {system_info.release}",
            'machine': system_info.machine,
            'boot_time': boot_time.strftime('%Y-%m-%d %H:%M:%S'),
            'hostname': system_info.node
        }
        
    def get_cpu_info(self):
        """获取CPU信息"""
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count_physical = psutil.cpu_count(logical=False)
        cpu_count_logical = psutil.cpu_count(logical=True)
        cpu_freq = psutil.cpu_freq()
        
        return {
            'usage_percent': cpu_percent,
            'physical_cores': cpu_count_physical,
            'logical_cores': cpu_count_logical,
            'frequency': cpu_freq.current if cpu_freq else 0
        }
        
    def get_memory_info(self):
        """获取内存信息"""
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            'total': memory.total,
            'available': memory.available,
            'used': memory.used,
            'percent': memory.percent,
            'swap_total': swap.total,
            'swap_used': swap.used,
            'swap_percent': swap.percent
        }
        
    def get_network_info(self):
        """获取网络信息"""
        current_network = psutil.net_io_counters()
        current_time = time.time()
        time_delta = current_time - self.last_network_time
        
        if time_delta > 0:
            sent_speed = (current_network.bytes_sent - self.network_stats_base.bytes_sent) / time_delta
            recv_speed = (current_network.bytes_recv - self.network_stats_base.bytes_recv) / time_delta
            
            self.network_stats_base = current_network
            self.last_network_time = current_time
            
            return {
                'sent_speed': sent_speed,
                'recv_speed': recv_speed,
                'total_sent': current_network.bytes_sent,
                'total_recv': current_network.bytes_recv,
                'packets_sent': current_network.packets_sent,
                'packets_recv': current_network.packets_recv
            }
        
        return {
            'sent_speed': 0,
            'recv_speed': 0,
            'total_sent': current_network.bytes_sent,
            'total_recv': current_network.bytes_recv,
            'packets_sent': current_network.packets_sent,
            'packets_recv': current_network.packets_recv
        }
        
    def get_disk_info(self):
        """获取磁盘信息"""
        disk_usage = psutil.disk_usage('/')
        return {
            'total': disk_usage.total,
            'used': disk_usage.used,
            'free': disk_usage.free,
            'percent': (disk_usage.used / disk_usage.total) * 100
        }
        
    def create_progress_bar(self, percent, width=40):
        """创建进度条"""
        filled = int(width * percent / 100)
        bar = '█' * filled + '░' * (width - filled)
        return f"[{bar}] {percent:.1f}%"
        
    def display_system_info(self, info):
        """显示系统信息"""
        print("=" * 80)
        print("🖥️  MAC系统监控器")
        print("=" * 80)
        print(f"系统: {info['system']}")
        print(f"主机名: {info['hostname']}")
        print(f"处理器: {info['machine']}")
        print(f"启动时间: {info['boot_time']}")
        print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
    def display_cpu_info(self, info):
        """显示CPU信息"""
        print("🔥 CPU使用情况")
        print("-" * 40)
        print(f"使用率: {self.create_progress_bar(info['usage_percent'])}")
        print(f"物理核心: {info['physical_cores']} 个")
        print(f"逻辑核心: {info['logical_cores']} 个")
        if info['frequency'] > 0:
            print(f"当前频率: {info['frequency']:.1f} MHz")
        print()
        
    def display_memory_info(self, info):
        """显示内存信息"""
        print("💾 内存使用情况")
        print("-" * 40)
        print(f"使用率: {self.create_progress_bar(info['percent'])}")
        print(f"总内存: {self.format_bytes(info['total'])}")
        print(f"已使用: {self.format_bytes(info['used'])}")
        print(f"可用: {self.format_bytes(info['available'])}")
        
        if info['swap_total'] > 0:
            print(f"交换分区: {self.create_progress_bar(info['swap_percent'])}")
            print(f"交换总量: {self.format_bytes(info['swap_total'])}")
            print(f"交换使用: {self.format_bytes(info['swap_used'])}")
        print()
        
    def display_network_info(self, info):
        """显示网络信息"""
        print("🌐 网络使用情况")
        print("-" * 40)
        print(f"上传速度: {self.format_bytes(info['sent_speed'])}/s")
        print(f"下载速度: {self.format_bytes(info['recv_speed'])}/s")
        print(f"总发送: {self.format_bytes(info['total_sent'])}")
        print(f"总接收: {self.format_bytes(info['total_recv'])}")
        print(f"发送包数: {info['packets_sent']:,}")
        print(f"接收包数: {info['packets_recv']:,}")
        print()
        
    def display_disk_info(self, info):
        """显示磁盘信息"""
        print("💽 磁盘使用情况")
        print("-" * 40)
        print(f"使用率: {self.create_progress_bar(info['percent'])}")
        print(f"总容量: {self.format_bytes(info['total'])}")
        print(f"已使用: {self.format_bytes(info['used'])}")
        print(f"可用: {self.format_bytes(info['free'])}")
        print()
        
    def run_once(self):
        """运行一次监控"""
        self.clear_screen()
        
        # 获取所有信息
        system_info = self.get_system_info()
        cpu_info = self.get_cpu_info()
        memory_info = self.get_memory_info()
        network_info = self.get_network_info()
        disk_info = self.get_disk_info()
        
        # 显示信息
        self.display_system_info(system_info)
        self.display_cpu_info(cpu_info)
        self.display_memory_info(memory_info)
        self.display_network_info(network_info)
        self.display_disk_info(disk_info)
        
        print("按 Ctrl+C 退出监控")
        
    def run(self, refresh_interval=2):
        """运行监控循环"""
        try:
            while True:
                self.run_once()
                time.sleep(refresh_interval)
        except KeyboardInterrupt:
            self.clear_screen()
            print("监控已停止。感谢使用Mac系统监控器！")


def main():
    """主函数"""
    print("正在启动Mac系统监控器...")
    
    # 检查系统类型
    system_type = platform.system()
    if system_type == 'Darwin':
        print("✅ 检测到Mac系统")
    else:
        print(f"⚠️  检测到{system_type}系统，某些功能可能不可用")
    
    # 创建并运行监控器
    monitor = MacSystemMonitorCLI()
    monitor.run()


if __name__ == "__main__":
    main()