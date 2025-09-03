# 🌍 地理问答系统

一个基于AI的智能地理问答系统，支持中国和世界地理知识的智能问答，提供美观的Web界面和腾讯云部署方案。

## ✨ 功能特性

- 🤖 **AI智能问答**: 基于Transformer模型的地理知识问答
- 📚 **知识库管理**: 支持添加、编辑、分类管理地理知识
- 🔍 **智能搜索**: 关键词搜索相关问题
- 📊 **分类浏览**: 按地理分类和难度等级浏览知识
- 💬 **对话历史**: 保存用户问答记录
- 🌐 **Web界面**: 基于Streamlit的现代化UI界面
- ☁️ **云部署**: 支持腾讯云轻量应用服务器和云服务器部署

## 🏗️ 系统架构

```
地理问答系统
├── 数据层 (data/)
│   └── geography_qa_dataset.json  # 地理知识数据集
├── 模型层 (models/)
│   ├── train_model.py             # 模型训练脚本
│   └── qa_model.py               # 问答推理脚本
├── 界面层 (web/)
│   └── web_app.py                # Streamlit Web界面
├── 部署层 (deploy/)
│   └── deploy_tencent.py         # 腾讯云部署脚本
└── 配置文件
    ├── requirements.txt           # Python依赖
    ├── Dockerfile                 # Docker镜像配置
    └── docker-compose.yml        # Docker Compose配置
```

## 🚀 快速开始

### 环境要求

- Python 3.8+
- CUDA 11.0+ (可选，用于GPU加速)
- 8GB+ 内存
- 20GB+ 磁盘空间

### 安装依赖

```bash
# 克隆项目
git clone <repository-url>
cd geography-qa-system

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 本地运行

1. **启动Web界面**
```bash
streamlit run web_app.py
```

2. **访问系统**
打开浏览器访问: http://localhost:8501

3. **测试问答**
在界面中输入地理问题，如"中国的首都是哪个城市？"

## 🎯 模型训练

### 准备数据

系统已包含基础的地理知识数据集，位于 `data/geography_qa_dataset.json`。

### 训练模型

```bash
python train_model.py
```

训练完成后，模型将保存在 `models/` 目录中。

### 模型配置

可以在 `train_model.py` 中调整以下参数：
- 模型类型: `bert-base-chinese`
- 最大长度: 512
- 训练轮数: 3
- 批次大小: 8
- 学习率: 默认

## 🌐 Web界面使用

### 主要功能

1. **智能问答**: 输入地理问题，获取AI回答
2. **知识库管理**: 浏览、搜索、添加地理知识
3. **分类浏览**: 按中国地理、世界地理等分类查看
4. **系统管理**: 查看系统状态、管理配置

### 界面特色

- 响应式设计，支持移动端
- 现代化UI，美观易用
- 实时对话历史
- 置信度显示
- 分类标签系统

## ☁️ 腾讯云部署

### 方式一：轻量应用服务器（推荐）

1. **设置环境变量**
```bash
export TENCENT_SECRET_ID='your_secret_id'
export TENCENT_SECRET_KEY='your_secret_key'
```

2. **运行部署脚本**
```bash
python deploy_tencent.py
```

3. **选择部署方式**
选择"轻量应用服务器"，系统将自动：
- 创建2核4GB实例
- 配置防火墙规则
- 生成部署脚本
- 提供部署说明

### 方式二：手动部署

1. **生成配置文件**
```bash
python deploy_tencent.py
# 选择"仅生成配置文件"
```

2. **上传到服务器**
```bash
scp -r . user@your-server-ip:/home/user/geography-qa/
```

3. **运行部署脚本**
```bash
ssh user@your-server-ip
cd geography-qa
bash deploy.sh
```

### 方式三：Docker部署

1. **构建镜像**
```bash
docker build -t geography-qa .
```

2. **运行容器**
```bash
docker-compose up -d
```

## 📊 性能优化

### 模型优化

- 使用模型量化减少内存占用
- 实现模型缓存机制
- 支持批处理推理

### 系统优化

- 实现问答结果缓存
- 异步处理用户请求
- 负载均衡支持

## 🔧 配置说明

### 环境变量

```bash
# Streamlit配置
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0

# 模型配置
MODEL_PATH=./models
MAX_LENGTH=512

# 腾讯云配置
TENCENT_SECRET_ID=your_secret_id
TENCENT_SECRET_KEY=your_secret_key
TENCENT_REGION=ap-guangzhou
```

### 端口配置

- **8501**: Streamlit Web界面
- **80**: HTTP访问（Nginx代理）
- **443**: HTTPS访问
- **22**: SSH管理

## 📈 监控和维护

### 系统监控

- 服务状态监控
- 性能指标统计
- 错误日志记录

### 定期维护

- 模型更新和重训练
- 知识库扩充
- 系统安全更新

## 🛠️ 故障排除

### 常见问题

1. **模型加载失败**
   - 检查模型文件是否存在
   - 验证模型文件完整性
   - 检查内存是否充足

2. **Web界面无法访问**
   - 检查端口是否开放
   - 验证防火墙配置
   - 检查服务状态

3. **部署失败**
   - 检查腾讯云API密钥
   - 验证网络连接
   - 查看错误日志

### 日志查看

```bash
# 查看服务状态
sudo systemctl status geography-qa

# 查看服务日志
sudo journalctl -u geography-qa -f

# 查看Nginx日志
sudo tail -f /var/log/nginx/access.log
```

## 🤝 贡献指南

欢迎贡献代码和想法！

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系方式

- 项目主页: [GitHub Repository]
- 问题反馈: [Issues]
- 邮箱: your-email@example.com

## 🙏 致谢

- 感谢 [Hugging Face](https://huggingface.co/) 提供的Transformer模型
- 感谢 [Streamlit](https://streamlit.io/) 提供的Web框架
- 感谢腾讯云提供的云服务支持

---

**注意**: 首次使用需要训练模型或使用预训练模型。建议在GPU环境下进行模型训练以获得更好的性能。