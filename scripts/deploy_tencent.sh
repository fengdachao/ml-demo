#!/bin/bash

# 腾讯云部署脚本
# 使用方法: ./scripts/deploy_tencent.sh

set -e

echo "=== 地理问答系统腾讯云部署脚本 ==="

# 配置变量
PROJECT_NAME="geography-qa"
DOCKER_REGISTRY="ccr.ccs.tencentyun.com"
NAMESPACE="your-namespace"  # 请替换为您的命名空间
IMAGE_NAME="${DOCKER_REGISTRY}/${NAMESPACE}/${PROJECT_NAME}"
VERSION=$(date +%Y%m%d_%H%M%S)

# 检查必要的工具
check_requirements() {
    echo "检查部署环境..."
    
    if ! command -v docker &> /dev/null; then
        echo "错误: Docker未安装"
        exit 1
    fi
    
    if ! command -v kubectl &> /dev/null; then
        echo "错误: kubectl未安装"
        exit 1
    fi
    
    echo "✓ 环境检查通过"
}

# 构建Docker镜像
build_image() {
    echo "构建Docker镜像..."
    docker build -t ${IMAGE_NAME}:${VERSION} .
    docker tag ${IMAGE_NAME}:${VERSION} ${IMAGE_NAME}:latest
    echo "✓ 镜像构建完成: ${IMAGE_NAME}:${VERSION}"
}

# 推送镜像到腾讯云容器镜像服务
push_image() {
    echo "推送镜像到腾讯云容器镜像服务..."
    
    # 登录到腾讯云容器镜像服务
    echo "请确保已经登录腾讯云容器镜像服务:"
    echo "docker login ${DOCKER_REGISTRY}"
    
    docker push ${IMAGE_NAME}:${VERSION}
    docker push ${IMAGE_NAME}:latest
    echo "✓ 镜像推送完成"
}

# 部署到腾讯云容器服务TKE
deploy_to_tke() {
    echo "部署到腾讯云容器服务TKE..."
    
    # 创建Kubernetes部署配置
    cat > k8s-deployment.yaml << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ${PROJECT_NAME}
  labels:
    app: ${PROJECT_NAME}
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ${PROJECT_NAME}
  template:
    metadata:
      labels:
        app: ${PROJECT_NAME}
    spec:
      containers:
      - name: ${PROJECT_NAME}
        image: ${IMAGE_NAME}:${VERSION}
        ports:
        - containerPort: 5000
        env:
        - name: FLASK_ENV
          value: "production"
        - name: PYTHONPATH
          value: "/app"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /api/health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/health
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: ${PROJECT_NAME}-service
spec:
  selector:
    app: ${PROJECT_NAME}
  ports:
    - protocol: TCP
      port: 80
      targetPort: 5000
  type: LoadBalancer
EOF

    # 应用配置
    kubectl apply -f k8s-deployment.yaml
    
    echo "✓ 部署完成"
    echo "获取服务状态:"
    kubectl get pods -l app=${PROJECT_NAME}
    kubectl get service ${PROJECT_NAME}-service
}

# 部署到腾讯云轻量应用服务器
deploy_to_lighthouse() {
    echo "部署到腾讯云轻量应用服务器..."
    echo "请确保已经配置好服务器连接信息"
    
    # 这里需要替换为您的服务器IP
    SERVER_IP="your-server-ip"
    
    echo "上传代码到服务器..."
    rsync -avz --exclude='venv' --exclude='__pycache__' --exclude='.git' . root@${SERVER_IP}:/opt/${PROJECT_NAME}/
    
    echo "在服务器上部署..."
    ssh root@${SERVER_IP} << EOF
        cd /opt/${PROJECT_NAME}
        
        # 安装Docker和Docker Compose
        if ! command -v docker &> /dev/null; then
            curl -fsSL https://get.docker.com | bash
            systemctl enable docker
            systemctl start docker
        fi
        
        if ! command -v docker-compose &> /dev/null; then
            curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-\$(uname -s)-\$(uname -m)" -o /usr/local/bin/docker-compose
            chmod +x /usr/local/bin/docker-compose
        fi
        
        # 启动服务
        docker-compose down
        docker-compose up -d
        
        echo "✓ 服务已启动"
        docker-compose ps
EOF
}

# 主函数
main() {
    echo "选择部署方式:"
    echo "1) 腾讯云容器服务TKE"
    echo "2) 腾讯云轻量应用服务器"
    echo "3) 仅构建和推送镜像"
    
    read -p "请输入选择 (1-3): " choice
    
    check_requirements
    
    case $choice in
        1)
            build_image
            push_image
            deploy_to_tke
            ;;
        2)
            deploy_to_lighthouse
            ;;
        3)
            build_image
            push_image
            ;;
        *)
            echo "无效选择"
            exit 1
            ;;
    esac
    
    echo "=== 部署完成 ==="
}

# 运行主函数
main