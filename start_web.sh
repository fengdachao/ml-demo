#!/bin/bash
# 直接启动Web版本
echo "🚀 启动Mac系统监控器 - Web版本"
echo "🌐 请在浏览器中访问: http://localhost:5000"
echo "🛑 按 Ctrl+C 停止服务"
echo ""

source venv/bin/activate
python3 mac_system_monitor_web.py
deactivate