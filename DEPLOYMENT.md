# 腾讯云部署指南

本文档详细介绍如何将地理问答系统部署到腾讯云平台。

## 部署方案对比

| 方案 | 适用场景 | 成本 | 难度 | 扩展性 |
|------|----------|------|------|--------|
| 轻量应用服务器 | 小型项目、学习测试 | 低 | 简单 | 有限 |
| 容器服务TKE | 生产环境、高可用 | 中等 | 中等 | 优秀 |
| 云函数SCF | 轻量级、按需计费 | 很低 | 简单 | 自动 |

## 方案一：腾讯云轻量应用服务器部署

### 1. 购买服务器

1. 登录腾讯云控制台
2. 选择"轻量应用服务器"
3. 推荐配置：
   - 地域：根据用户分布选择
   - 镜像：Ubuntu 20.04 LTS
   - 套餐：2核2G内存（最低配置）
   - 系统盘：40GB SSD

### 2. 配置安全组

开放以下端口：
- 22 (SSH)
- 80 (HTTP)
- 443 (HTTPS)
- 5000 (应用端口，可选)

### 3. 连接服务器

```bash
ssh ubuntu@your-server-ip
```

### 4. 环境准备

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Docker
curl -fsSL https://get.docker.com | bash
sudo systemctl enable docker
sudo systemctl start docker

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 安装Git
sudo apt install git -y
```

### 5. 部署应用

```bash
# 克隆代码
git clone <your-repository-url>
cd geography-qa-system

# 启动服务
docker-compose up -d

# 查看服务状态
docker-compose ps
```

### 6. 配置域名（可选）

1. 在腾讯云DNS解析中添加A记录
2. 申请SSL证书
3. 配置Nginx HTTPS

## 方案二：腾讯云容器服务TKE部署

### 1. 创建TKE集群

1. 登录腾讯云控制台
2. 选择"容器服务TKE"
3. 创建集群：
   - 集群类型：托管集群
   - Kubernetes版本：1.20+
   - 节点配置：2核4G内存

### 2. 配置容器镜像服务

1. 开通"容器镜像服务TCR"
2. 创建命名空间
3. 获取登录命令

### 3. 构建和推送镜像

```bash
# 登录镜像仓库
docker login ccr.ccs.tencentyun.com

# 构建镜像
docker build -t ccr.ccs.tencentyun.com/your-namespace/geography-qa:latest .

# 推送镜像
docker push ccr.ccs.tencentyun.com/your-namespace/geography-qa:latest
```

### 4. 部署到TKE

使用提供的部署脚本：

```bash
./scripts/deploy_tencent.sh
```

或手动创建Kubernetes资源：

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: geography-qa
spec:
  replicas: 2
  selector:
    matchLabels:
      app: geography-qa
  template:
    metadata:
      labels:
        app: geography-qa
    spec:
      containers:
      - name: geography-qa
        image: ccr.ccs.tencentyun.com/your-namespace/geography-qa:latest
        ports:
        - containerPort: 5000
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: geography-qa-service
spec:
  selector:
    app: geography-qa
  ports:
  - port: 80
    targetPort: 5000
  type: LoadBalancer
```

### 5. 配置负载均衡

1. 创建CLB负载均衡器
2. 配置监听器
3. 绑定后端服务

## 方案三：腾讯云云函数SCF部署

### 1. 修改应用为无服务器架构

创建 `scf_main.py`:

```python
import json
from web.app import app

def main_handler(event, context):
    """SCF入口函数"""
    # 解析API Gateway事件
    method = event.get('httpMethod', 'GET')
    path = event.get('path', '/')
    headers = event.get('headers', {})
    body = event.get('body', '')
    
    # 创建WSGI环境
    with app.test_client() as client:
        if method == 'GET':
            response = client.get(path, headers=headers)
        elif method == 'POST':
            response = client.post(path, data=body, headers=headers)
        
        return {
            'statusCode': response.status_code,
            'headers': dict(response.headers),
            'body': response.get_data(as_text=True)
        }
```

### 2. 创建部署包

```bash
# 安装依赖到本地目录
pip install -r requirements.txt -t ./

# 打包
zip -r geography-qa-scf.zip .
```

### 3. 部署到SCF

1. 登录腾讯云控制台
2. 选择"云函数SCF"
3. 创建函数：
   - 运行环境：Python 3.8
   - 执行方法：scf_main.main_handler
   - 内存：512MB
   - 超时时间：30秒

### 4. 配置API网关

1. 创建API网关服务
2. 配置路由规则
3. 绑定云函数

## 域名和SSL配置

### 1. 域名解析

在腾讯云DNS解析中添加记录：
```
类型: A
主机记录: @
记录值: your-server-ip
TTL: 600
```

### 2. SSL证书申请

1. 在腾讯云SSL证书服务中申请免费证书
2. 下载Nginx格式证书
3. 上传到服务器 `/etc/nginx/ssl/` 目录

### 3. Nginx HTTPS配置

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    location / {
        proxy_pass http://geography-qa:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

## 监控和维护

### 1. 日志监控

```bash
# 查看应用日志
docker-compose logs -f geography-qa

# 查看Nginx日志
docker-compose logs -f nginx
```

### 2. 性能监控

使用腾讯云监控服务：
1. 配置云监控告警
2. 设置关键指标阈值
3. 配置通知方式

### 3. 备份策略

```bash
# 备份数据
docker-compose exec geography-qa cp -r /app/data /backup/

# 备份数据库（如果使用）
# mysqldump -u root -p database_name > backup.sql
```

### 4. 更新部署

```bash
# 拉取最新代码
git pull origin main

# 重新构建和部署
docker-compose down
docker-compose build
docker-compose up -d
```

## 成本估算

### 轻量应用服务器
- 2核2G内存：约60元/月
- 流量费用：约0.8元/GB
- 总计：约80-100元/月

### 容器服务TKE
- 集群管理费：免费
- 节点费用：按CVM计费
- 负载均衡：约18元/月
- 总计：约150-300元/月

### 云函数SCF
- 调用次数：前100万次免费
- 执行时间：前40万GB-s免费
- API网关：前100万次免费
- 总计：小流量几乎免费

## 故障排除

### 常见问题

1. **容器启动失败**
   ```bash
   docker-compose logs geography-qa
   ```

2. **端口访问问题**
   ```bash
   # 检查端口占用
   netstat -tlnp | grep 5000
   
   # 检查防火墙
   sudo ufw status
   ```

3. **域名解析问题**
   ```bash
   # 检查DNS解析
   nslookup your-domain.com
   
   # 检查证书
   openssl s_client -connect your-domain.com:443
   ```

4. **性能问题**
   - 增加容器资源限制
   - 使用CDN加速静态资源
   - 优化数据库查询

## 安全建议

1. **服务器安全**
   - 定期更新系统
   - 配置防火墙
   - 使用密钥登录
   - 定期备份数据

2. **应用安全**
   - 使用HTTPS
   - 配置请求限流
   - 输入验证和过滤
   - 定期更新依赖

3. **网络安全**
   - 配置安全组规则
   - 使用私有网络VPC
   - 启用DDoS防护
   - 配置Web应用防火墙

通过以上配置，您的地理问答系统就可以稳定运行在腾讯云平台上了。