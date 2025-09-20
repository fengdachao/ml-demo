#!/bin/bash
# 直接启动命令行版本
echo "🚀 启动Mac系统监控器 - 命令行版本"
echo "💡 提示: 按 Ctrl+C 退出监控"
echo ""

source venv/bin/activate
python3 mac_system_monitor_cli.py
deactivate