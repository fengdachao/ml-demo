#!/bin/bash
# 地理问答系统自动安装脚本 (Linux)

set -e

echo "🌍 地理问答系统 - 自动安装脚本"
echo "=================================="

# 检查操作系统
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "❌ 此脚本仅支持Linux系统"
    exit 1
fi

# 检查是否为root用户
if [[ $EUID -eq 0 ]]; then
    echo "⚠️  检测到root用户，建议使用普通用户运行"
    read -p "是否继续? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 更新系统包
echo "📦 更新系统包..."
sudo apt update

# 安装系统依赖
echo "🔧 安装系统依赖..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    git \
    curl \
    wget \
    unzip

# 检查Python版本
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python版本过低，需要3.8+，当前版本: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python版本检查通过: $PYTHON_VERSION"

# 创建项目目录
PROJECT_DIR="$HOME/geography-qa"
echo "📁 创建项目目录: $PROJECT_DIR"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# 创建虚拟环境
echo "🐍 创建Python虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 升级pip
echo "⬆️  升级pip..."
pip install --upgrade pip

# 安装Python依赖
echo "📚 安装Python依赖..."
pip install -r requirements.txt

# 创建必要的目录
echo "📂 创建必要的目录..."
mkdir -p data models logs

# 检查CUDA可用性
if command -v nvidia-smi &> /dev/null; then
    echo "🚀 检测到NVIDIA GPU，安装CUDA版本的PyTorch..."
    pip uninstall torch torchvision torchaudio -y
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
    echo "✅ CUDA版本PyTorch安装完成"
else
    echo "💻 未检测到NVIDIA GPU，使用CPU版本"
fi

# 下载预训练模型（可选）
echo "🤖 下载预训练模型..."
if [ ! -d "models" ] || [ -z "$(ls -A models)" ]; then
    echo "📥 下载bert-base-chinese模型..."
    python3 -c "
from transformers import AutoTokenizer, AutoModelForQuestionAnswering
tokenizer = AutoTokenizer.from_pretrained('bert-base-chinese')
model = AutoModelForQuestionAnswering.from_pretrained('bert-base-chinese')
tokenizer.save_pretrained('./models')
model.save_pretrained('./models')
print('模型下载完成')
"
else
    echo "✅ 模型目录已存在"
fi

# 创建启动脚本
echo "📝 创建启动脚本..."
cat > start.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
export STREAMLIT_SERVER_PORT=8501
export STREAMLIT_SERVER_ADDRESS=0.0.0.0
streamlit run web_app.py
EOF

chmod +x start.sh

# 创建systemd服务文件
echo "🔧 创建systemd服务..."
sudo tee /etc/systemd/system/geography-qa.service > /dev/null << EOF
[Unit]
Description=Geography QA System
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$PROJECT_DIR/venv/bin
ExecStart=$PROJECT_DIR/venv/bin/streamlit run web_app.py --server.port 8501 --server.address 0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 重新加载systemd
sudo systemctl daemon-reload

# 启用服务
sudo systemctl enable geography-qa

echo "✅ 安装完成！"
echo ""
echo "🚀 启动方式:"
echo "  1. 手动启动: ./start.sh"
echo "  2. 服务启动: sudo systemctl start geography-qa"
echo "  3. 查看状态: sudo systemctl status geography-qa"
echo ""
echo "🌐 访问地址: http://localhost:8501"
echo ""
echo "📚 使用说明:"
echo "  - 查看日志: sudo journalctl -u geography-qa -f"
echo "  - 停止服务: sudo systemctl stop geography-qa"
echo "  - 重启服务: sudo systemctl restart geography-qa"
echo ""
echo "🎯 下一步:"
echo "  1. 运行 ./start.sh 启动系统"
echo "  2. 在浏览器中访问 http://localhost:8501"
echo "  3. 开始使用地理问答系统！"