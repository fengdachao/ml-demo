#!/usr/bin/env python3
"""
Mac系统监控应用程序 - Web版本
监控CPU、内存和网络使用情况
"""

from flask import Flask, render_template, jsonify
import psutil
import time
import platform
from datetime import datetime
import json


app = Flask(__name__)

class SystemMonitor:
    def __init__(self):
        self.network_stats_base = psutil.net_io_counters()
        self.last_network_time = time.time()
        
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
            'hostname': system_info.node,
            'current_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
    def get_cpu_info(self):
        """获取CPU信息"""
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count_physical = psutil.cpu_count(logical=False)
        cpu_count_logical = psutil.cpu_count(logical=True)
        cpu_freq = psutil.cpu_freq()
        
        return {
            'usage_percent': round(cpu_percent, 1),
            'physical_cores': cpu_count_physical,
            'logical_cores': cpu_count_logical,
            'frequency': round(cpu_freq.current, 1) if cpu_freq else 0
        }
        
    def get_memory_info(self):
        """获取内存信息"""
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            'total': memory.total,
            'total_formatted': self.format_bytes(memory.total),
            'available': memory.available,
            'available_formatted': self.format_bytes(memory.available),
            'used': memory.used,
            'used_formatted': self.format_bytes(memory.used),
            'percent': round(memory.percent, 1),
            'swap_total': swap.total,
            'swap_total_formatted': self.format_bytes(swap.total),
            'swap_used': swap.used,
            'swap_used_formatted': self.format_bytes(swap.used),
            'swap_percent': round(swap.percent, 1) if swap.total > 0 else 0
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
                'sent_speed_formatted': self.format_bytes(sent_speed) + '/s',
                'recv_speed': recv_speed,
                'recv_speed_formatted': self.format_bytes(recv_speed) + '/s',
                'total_sent': current_network.bytes_sent,
                'total_sent_formatted': self.format_bytes(current_network.bytes_sent),
                'total_recv': current_network.bytes_recv,
                'total_recv_formatted': self.format_bytes(current_network.bytes_recv),
                'packets_sent': current_network.packets_sent,
                'packets_recv': current_network.packets_recv
            }
        
        return {
            'sent_speed': 0,
            'sent_speed_formatted': '0 B/s',
            'recv_speed': 0,
            'recv_speed_formatted': '0 B/s',
            'total_sent': current_network.bytes_sent,
            'total_sent_formatted': self.format_bytes(current_network.bytes_sent),
            'total_recv': current_network.bytes_recv,
            'total_recv_formatted': self.format_bytes(current_network.bytes_recv),
            'packets_sent': current_network.packets_sent,
            'packets_recv': current_network.packets_recv
        }
        
    def get_disk_info(self):
        """获取磁盘信息"""
        disk_usage = psutil.disk_usage('/')
        return {
            'total': disk_usage.total,
            'total_formatted': self.format_bytes(disk_usage.total),
            'used': disk_usage.used,
            'used_formatted': self.format_bytes(disk_usage.used),
            'free': disk_usage.free,
            'free_formatted': self.format_bytes(disk_usage.free),
            'percent': round((disk_usage.used / disk_usage.total) * 100, 1)
        }
        
    def get_all_info(self):
        """获取所有系统信息"""
        return {
            'system': self.get_system_info(),
            'cpu': self.get_cpu_info(),
            'memory': self.get_memory_info(),
            'network': self.get_network_info(),
            'disk': self.get_disk_info()
        }

# 创建监控器实例
monitor = SystemMonitor()

@app.route('/')
def index():
    """主页面"""
    return render_template('monitor.html')

@app.route('/api/system')
def api_system():
    """获取系统信息API"""
    try:
        data = monitor.get_all_info()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # 创建模板目录和文件
    import os
    os.makedirs('templates', exist_ok=True)
    
    # 创建HTML模板
    html_template = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mac系统监控器</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
        }
        
        .card h2 {
            color: #333;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            font-size: 1.4em;
        }
        
        .card h2 .icon {
            margin-right: 10px;
            font-size: 1.2em;
        }
        
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }
        
        .info-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px;
            background: rgba(0, 0, 0, 0.05);
            border-radius: 8px;
        }
        
        .info-label {
            font-weight: 500;
            color: #666;
        }
        
        .info-value {
            font-weight: 600;
            color: #333;
        }
        
        .progress-bar {
            width: 100%;
            height: 20px;
            background: #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(45deg, #4CAF50, #45a049);
            border-radius: 10px;
            transition: width 0.3s ease;
        }
        
        .progress-fill.warning {
            background: linear-gradient(45deg, #ff9800, #f57c00);
        }
        
        .progress-fill.danger {
            background: linear-gradient(45deg, #f44336, #d32f2f);
        }
        
        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #4CAF50;
            margin-right: 5px;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .loading {
            text-align: center;
            color: #666;
            font-style: italic;
        }
        
        .error {
            color: #f44336;
            text-align: center;
            padding: 20px;
        }
        
        @media (max-width: 768px) {
            .header h1 {
                font-size: 2em;
            }
            
            .info-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🖥️ Mac系统监控器</h1>
            <p><span class="status-indicator"></span>实时监控中...</p>
        </div>
        
        <div id="system-info" class="card">
            <h2><span class="icon">ℹ️</span>系统信息</h2>
            <div class="loading">正在加载系统信息...</div>
        </div>
        
        <div id="cpu-info" class="card">
            <h2><span class="icon">🔥</span>CPU使用情况</h2>
            <div class="loading">正在加载CPU信息...</div>
        </div>
        
        <div id="memory-info" class="card">
            <h2><span class="icon">💾</span>内存使用情况</h2>
            <div class="loading">正在加载内存信息...</div>
        </div>
        
        <div id="network-info" class="card">
            <h2><span class="icon">🌐</span>网络使用情况</h2>
            <div class="loading">正在加载网络信息...</div>
        </div>
        
        <div id="disk-info" class="card">
            <h2><span class="icon">💽</span>磁盘使用情况</h2>
            <div class="loading">正在加载磁盘信息...</div>
        </div>
    </div>
    
    <script>
        function formatNumber(num) {
            return num.toLocaleString();
        }
        
        function getProgressBarClass(percent) {
            if (percent >= 80) return 'danger';
            if (percent >= 60) return 'warning';
            return '';
        }
        
        function updateSystemInfo(data) {
            const container = document.getElementById('system-info');
            container.innerHTML = `
                <h2><span class="icon">ℹ️</span>系统信息</h2>
                <div class="info-grid">
                    <div class="info-item">
                        <span class="info-label">系统</span>
                        <span class="info-value">${data.system}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">主机名</span>
                        <span class="info-value">${data.hostname}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">处理器</span>
                        <span class="info-value">${data.machine}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">启动时间</span>
                        <span class="info-value">${data.boot_time}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">当前时间</span>
                        <span class="info-value">${data.current_time}</span>
                    </div>
                </div>
            `;
        }
        
        function updateCPUInfo(data) {
            const container = document.getElementById('cpu-info');
            container.innerHTML = `
                <h2><span class="icon">🔥</span>CPU使用情况</h2>
                <div class="progress-bar">
                    <div class="progress-fill ${getProgressBarClass(data.usage_percent)}" 
                         style="width: ${data.usage_percent}%"></div>
                </div>
                <div class="info-grid">
                    <div class="info-item">
                        <span class="info-label">使用率</span>
                        <span class="info-value">${data.usage_percent}%</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">物理核心</span>
                        <span class="info-value">${data.physical_cores} 个</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">逻辑核心</span>
                        <span class="info-value">${data.logical_cores} 个</span>
                    </div>
                    ${data.frequency > 0 ? `
                    <div class="info-item">
                        <span class="info-label">频率</span>
                        <span class="info-value">${data.frequency} MHz</span>
                    </div>
                    ` : ''}
                </div>
            `;
        }
        
        function updateMemoryInfo(data) {
            const container = document.getElementById('memory-info');
            container.innerHTML = `
                <h2><span class="icon">💾</span>内存使用情况</h2>
                <div class="progress-bar">
                    <div class="progress-fill ${getProgressBarClass(data.percent)}" 
                         style="width: ${data.percent}%"></div>
                </div>
                <div class="info-grid">
                    <div class="info-item">
                        <span class="info-label">使用率</span>
                        <span class="info-value">${data.percent}%</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">总内存</span>
                        <span class="info-value">${data.total_formatted}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">已使用</span>
                        <span class="info-value">${data.used_formatted}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">可用</span>
                        <span class="info-value">${data.available_formatted}</span>
                    </div>
                    ${data.swap_total > 0 ? `
                    <div class="info-item">
                        <span class="info-label">交换分区</span>
                        <span class="info-value">${data.swap_percent}%</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">交换总量</span>
                        <span class="info-value">${data.swap_total_formatted}</span>
                    </div>
                    ` : ''}
                </div>
            `;
        }
        
        function updateNetworkInfo(data) {
            const container = document.getElementById('network-info');
            container.innerHTML = `
                <h2><span class="icon">🌐</span>网络使用情况</h2>
                <div class="info-grid">
                    <div class="info-item">
                        <span class="info-label">上传速度</span>
                        <span class="info-value">${data.sent_speed_formatted}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">下载速度</span>
                        <span class="info-value">${data.recv_speed_formatted}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">总发送</span>
                        <span class="info-value">${data.total_sent_formatted}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">总接收</span>
                        <span class="info-value">${data.total_recv_formatted}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">发送包数</span>
                        <span class="info-value">${formatNumber(data.packets_sent)}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">接收包数</span>
                        <span class="info-value">${formatNumber(data.packets_recv)}</span>
                    </div>
                </div>
            `;
        }
        
        function updateDiskInfo(data) {
            const container = document.getElementById('disk-info');
            container.innerHTML = `
                <h2><span class="icon">💽</span>磁盘使用情况</h2>
                <div class="progress-bar">
                    <div class="progress-fill ${getProgressBarClass(data.percent)}" 
                         style="width: ${data.percent}%"></div>
                </div>
                <div class="info-grid">
                    <div class="info-item">
                        <span class="info-label">使用率</span>
                        <span class="info-value">${data.percent}%</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">总容量</span>
                        <span class="info-value">${data.total_formatted}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">已使用</span>
                        <span class="info-value">${data.used_formatted}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">可用</span>
                        <span class="info-value">${data.free_formatted}</span>
                    </div>
                </div>
            `;
        }
        
        function showError(message) {
            document.querySelectorAll('.card').forEach(card => {
                if (card.querySelector('.loading')) {
                    card.innerHTML = `<div class="error">错误: ${message}</div>`;
                }
            });
        }
        
        function fetchSystemData() {
            fetch('/api/system')
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        showError(data.error);
                        return;
                    }
                    
                    updateSystemInfo(data.system);
                    updateCPUInfo(data.cpu);
                    updateMemoryInfo(data.memory);
                    updateNetworkInfo(data.network);
                    updateDiskInfo(data.disk);
                })
                .catch(error => {
                    console.error('Error:', error);
                    showError('无法获取系统数据');
                });
        }
        
        // 初始加载
        fetchSystemData();
        
        // 每2秒更新一次
        setInterval(fetchSystemData, 2000);
    </script>
</body>
</html>'''
    
    with open('templates/monitor.html', 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print("🚀 Mac系统监控器 Web版本正在启动...")
    print("📱 请在浏览器中访问: http://localhost:5000")
    print("🛑 按 Ctrl+C 停止服务")
    
    app.run(host='0.0.0.0', port=5000, debug=False)