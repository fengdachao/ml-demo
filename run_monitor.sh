#!/bin/bash

# Mac系统监控器启动脚本

echo "🖥️  Mac系统监控器启动脚本"
echo "=========================="

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python 3。请安装Python 3。"
    exit 1
fi

echo "✅ 检测到Python 3"

# 检查是否存在虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔄 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📥 安装依赖包..."
pip install -r requirements.txt --quiet

echo ""
echo "请选择运行模式:"
echo "1) GUI版本 (需要图形界面)"
echo "2) 命令行版本"
echo "3) Web版本 (浏览器访问)"
echo ""

read -p "请输入选择 (1-3): " choice

case $choice in
    1)
        echo "🚀 启动GUI版本..."
        python3 mac_system_monitor.py
        ;;
    2)
        echo "🚀 启动命令行版本..."
        echo "💡 提示: 按 Ctrl+C 退出监控"
        python3 mac_system_monitor_cli.py
        ;;
    3)
        echo "🚀 启动Web版本..."
        echo "🌐 请在浏览器中访问: http://localhost:5000"
        echo "🛑 按 Ctrl+C 停止服务"
        python3 mac_system_monitor_web.py
        ;;
    *)
        echo "❌ 无效选择，默认启动命令行版本..."
        python3 mac_system_monitor_cli.py
        ;;
esac

# 停用虚拟环境
deactivate