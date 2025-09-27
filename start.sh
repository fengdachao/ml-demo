#!/bin/bash

# 智能新闻搜索智能体启动脚本

echo "🤖 启动智能新闻搜索智能体..."
echo "=================================="

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python3，请先安装 Python3"
    exit 1
fi

# 检查pip是否安装
if ! command -v pip3 &> /dev/null; then
    echo "❌ 错误: 未找到 pip3，请先安装 pip3"
    exit 1
fi

# 创建虚拟环境（如果不存在）
if [ ! -d "news_env" ]; then
    echo "📦 创建Python虚拟环境..."
    python3 -m venv news_env
    if [ $? -ne 0 ]; then
        echo "❌ 虚拟环境创建失败，请检查Python安装"
        exit 1
    fi
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source news_env/bin/activate

# 安装依赖
echo "📦 安装项目依赖..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ 依赖安装失败，请检查网络连接或手动安装"
    exit 1
fi

echo "✅ 依赖安装完成"

# 检查端口是否被占用
PORT=8000
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null; then
    echo "⚠️  警告: 端口 $PORT 已被占用，尝试使用其他端口..."
    PORT=8001
fi

# 启动应用
echo "🚀 启动Web应用..."
echo "访问地址: http://localhost:$PORT"
echo "按 Ctrl+C 停止服务"
echo "=================================="

uvicorn app:app --host 0.0.0.0 --port $PORT --reload

echo "👋 服务已停止"