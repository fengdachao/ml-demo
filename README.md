# 地理问答系统

一个基于人工智能的中国地理知识问答系统，支持省份、河流、山脉等地理信息查询。

## 功能特点

- 🗺️ **省份信息查询**: 查询中国各省份的省会城市、地理位置等信息
- 🌊 **河流山脉信息**: 了解主要河流、山脉的长度、位置、海拔等信息  
- 🧠 **智能问答**: 支持自然语言问题，智能匹配最相关的答案
- 🌐 **现代Web界面**: 响应式设计，支持桌面和移动设备
- ☁️ **云端部署**: 支持腾讯云等主流云平台部署

## 系统架构

```
地理问答系统/
├── data/                    # 数据文件
│   ├── geography_qa_dataset.py  # 数据集生成器
│   ├── geography_qa.json       # 问答数据集
│   ├── train_data.json         # 训练数据
│   └── test_data.json          # 测试数据
├── models/                  # 模型文件
│   ├── simple_qa.py            # 简单问答模型
│   └── geography_qa_model.py   # 高级模型（需要PyTorch）
├── web/                     # Web应用
│   └── app.py                  # Flask应用主文件
├── templates/               # HTML模板
│   └── index.html              # 主页面
├── static/                  # 静态文件
│   ├── css/style.css           # 样式文件
│   └── js/main.js              # JavaScript文件
├── scripts/                 # 脚本文件
│   ├── train_model.py          # 模型训练脚本
│   └── deploy_tencent.sh       # 腾讯云部署脚本
├── Dockerfile              # Docker配置
├── docker-compose.yml      # Docker Compose配置
├── nginx.conf             # Nginx配置
└── requirements.txt       # Python依赖
```

## 快速开始

### 本地运行

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd geography-qa-system
   ```

2. **安装依赖**
   ```bash
   # 安装系统依赖
   sudo apt update
   sudo apt install python3-flask python3-flask-cors
   
   # 或使用pip安装（推荐使用虚拟环境）
   pip3 install flask flask-cors
   ```

3. **生成数据集**
   ```bash
   python3 data/geography_qa_dataset.py
   ```

4. **启动应用**
   ```bash
   python3 web/app.py
   ```

5. **访问应用**
   打开浏览器访问: http://localhost:5000

### 使用Docker运行

1. **构建镜像**
   ```bash
   docker build -t geography-qa .
   ```

2. **运行容器**
   ```bash
   docker run -p 5000:5000 geography-qa
   ```

3. **使用Docker Compose**
   ```bash
   docker-compose up -d
   ```

## 腾讯云部署

### 方式一：腾讯云容器服务TKE

1. **准备工作**
   - 开通腾讯云容器镜像服务TCR
   - 创建TKE集群
   - 安装kubectl并配置集群访问

2. **执行部署脚本**
   ```bash
   ./scripts/deploy_tencent.sh
   ```
   选择选项1进行TKE部署

3. **配置域名和SSL**
   - 在腾讯云DNS解析中配置域名
   - 申请SSL证书并配置HTTPS

### 方式二：腾讯云轻量应用服务器

1. **购买轻量应用服务器**
   - 选择Ubuntu 20.04镜像
   - 配置安全组开放80、443端口

2. **修改部署脚本**
   编辑 `scripts/deploy_tencent.sh`，替换服务器IP:
   ```bash
   SERVER_IP="your-server-ip"
   ```

3. **执行部署**
   ```bash
   ./scripts/deploy_tencent.sh
   ```
   选择选项2进行轻量服务器部署

## API接口

### 健康检查
```http
GET /api/health
```

响应:
```json
{
  "status": "healthy",
  "message": "地理问答系统运行正常"
}
```

### 问答接口
```http
POST /api/ask
Content-Type: application/json

{
  "question": "北京是哪个省的省会？"
}
```

响应:
```json
{
  "success": true,
  "question": "北京是哪个省的省会？",
  "answer": "北京是北京省的省会。"
}
```

### 统计信息
```http
GET /api/stats
```

响应:
```json
{
  "success": true,
  "stats": {
    "total_qa_pairs": 91,
    "categories": ["省会城市", "河流", "山脉", "综合"]
  }
}
```

## 模型训练

### 简单模型
系统默认使用基于规则的简单问答模型，无需额外训练。

### 高级模型（可选）
如需使用基于Transformer的高级模型：

1. **安装训练依赖**
   ```bash
   pip install torch transformers datasets jieba opencc-python-reimplemented
   ```

2. **运行训练脚本**
   ```bash
   python3 scripts/train_model.py
   ```

## 数据集

系统包含91个中国地理相关的问答对，涵盖：

- **省会城市** (68对): 34个省级行政区的省会查询
- **河流信息** (12对): 主要河流的长度、发源地、流向
- **山脉信息** (12对): 主要山脉的最高峰、海拔、位置
- **综合信息** (3对): 综合性地理知识

## 性能优化

- 使用Nginx反向代理
- 启用Gzip压缩
- 静态文件缓存
- API请求限流
- 容器健康检查

## 监控和日志

- 应用健康检查: `/api/health`
- 容器健康监控
- Nginx访问日志
- 应用错误日志

## 常见问题

### Q: 如何添加新的问答数据？
A: 编辑 `data/geography_qa_dataset.py` 文件，在相应的数据结构中添加新的问答对，然后重新运行数据生成脚本。

### Q: 如何自定义Web界面？
A: 修改 `templates/index.html` 和 `static/css/style.css` 文件来自定义界面外观。

### Q: 如何扩展到其他地理区域？
A: 修改数据生成器，添加其他国家或地区的地理数据。

### Q: 如何提高问答准确性？
A: 可以训练基于Transformer的高级模型，或者优化简单模型的匹配算法。

## 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 许可证

MIT License

## 联系方式

如有问题或建议，请创建Issue或联系项目维护者。