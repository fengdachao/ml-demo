#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
腾讯云部署脚本
用于部署地理问答系统到腾讯云
"""

import os
import json
import subprocess
import sys
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.cvm.v20170312 import cvm_client, models
from tencentcloud.lighthouse.v20200324 import lighthouse_client, lighthouse_models

class TencentCloudDeployer:
    def __init__(self, secret_id, secret_key, region="ap-guangzhou"):
        """
        初始化腾讯云部署器
        
        Args:
            secret_id: 腾讯云API密钥ID
            secret_key: 腾讯云API密钥Key
            region: 地域
        """
        self.secret_id = secret_id
        self.secret_key = secret_key
        self.region = region
        
        # 初始化认证
        self.cred = credential.Credential(secret_id, secret_key)
        
    def create_lighthouse_instance(self, instance_name="geography-qa-system"):
        """创建轻量应用服务器实例"""
        try:
            client = lighthouse_client.LighthouseClient(self.cred, self.region)
            
            # 创建实例请求
            req = lighthouse_models.CreateInstancesRequest()
            req.InstanceName = instance_name
            req.BundleId = "bundle2022_gen_01_02"  # 2核4GB配置
            req.BlueprintId = "lhbp-f1lkcd1k"  # Ubuntu 20.04 LTS
            req.Region = self.region
            req.Zone = "ap-guangzhou-2"  # 可用区
            
            # 设置防火墙规则
            firewall_rules = []
            # SSH端口
            ssh_rule = lighthouse_models.FirewallRule()
            ssh_rule.Protocol = "TCP"
            ssh_rule.Port = "22"
            ssh_rule.Source = "0.0.0.0/0"
            ssh_rule.Description = "SSH"
            firewall_rules.append(ssh_rule)
            
            # HTTP端口
            http_rule = lighthouse_models.FirewallRule()
            http_rule.Protocol = "TCP"
            http_rule.Port = "80"
            http_rule.Source = "0.0.0.0/0"
            http_rule.Description = "HTTP"
            firewall_rules.append(http_rule)
            
            # HTTPS端口
            https_rule = lighthouse_models.FirewallRule()
            https_rule.Protocol = "TCP"
            https_rule.Port = "443"
            https_rule.Source = "0.0.0.0/0"
            https_rule.Description = "HTTPS"
            firewall_rules.append(https_rule)
            
            # Streamlit端口
            streamlit_rule = lighthouse_models.FirewallRule()
            streamlit_rule.Protocol = "TCP"
            streamlit_rule.Port = "8501"
            streamlit_rule.Source = "0.0.0.0/0"
            streamlit_rule.Description = "Streamlit"
            firewall_rules.append(streamlit_rule)
            
            req.FirewallTemplateId = "lhtemplate-default"
            
            print("正在创建轻量应用服务器实例...")
            resp = client.CreateInstances(req)
            
            if resp.InstanceIdSet:
                instance_id = resp.InstanceIdSet[0]
                print(f"实例创建成功！实例ID: {instance_id}")
                return instance_id
            else:
                print("实例创建失败")
                return None
                
        except TencentCloudSDKException as err:
            print(f"创建实例失败: {err}")
            return None
    
    def get_instance_info(self, instance_id):
        """获取实例信息"""
        try:
            client = lighthouse_client.LighthouseClient(self.cred, self.region)
            
            req = lighthouse_models.DescribeInstancesRequest()
            req.InstanceIds = [instance_id]
            
            resp = client.DescribeInstances(req)
            
            if resp.InstanceSet:
                instance = resp.InstanceSet[0]
                return {
                    'public_ip': instance.PublicIpAddresses[0] if instance.PublicIpAddresses else None,
                    'private_ip': instance.PrivateIpAddresses[0] if instance.PrivateIpAddresses else None,
                    'status': instance.State,
                    'instance_name': instance.InstanceName
                }
            return None
            
        except TencentCloudSDKException as err:
            print(f"获取实例信息失败: {err}")
            return None
    
    def wait_for_instance_ready(self, instance_id, timeout=300):
        """等待实例就绪"""
        import time
        
        print("等待实例就绪...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            info = self.get_instance_info(instance_id)
            if info and info['status'] == 'RUNNING':
                print("实例已就绪！")
                return info
            time.sleep(10)
            print("等待中...")
        
        print("等待超时")
        return None
    
    def create_deployment_script(self, public_ip):
        """创建部署脚本"""
        script_content = f"""#!/bin/bash
# 地理问答系统部署脚本

echo "开始部署地理问答系统..."

# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Python和pip
sudo apt install -y python3 python3-pip python3-venv

# 安装Git
sudo apt install -y git

# 创建项目目录
mkdir -p /home/ubuntu/geography-qa
cd /home/ubuntu/geography-qa

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt

# 创建必要的目录
mkdir -p data models

# 设置环境变量
export STREAMLIT_SERVER_PORT=8501
export STREAMLIT_SERVER_ADDRESS=0.0.0.0

# 创建systemd服务文件
sudo tee /etc/systemd/system/geography-qa.service > /dev/null <<EOF
[Unit]
Description=Geography QA System
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/geography-qa
Environment=PATH=/home/ubuntu/geography-qa/venv/bin
ExecStart=/home/ubuntu/geography-qa/venv/bin/streamlit run web_app.py --server.port 8501 --server.address 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 重新加载systemd
sudo systemctl daemon-reload

# 启用并启动服务
sudo systemctl enable geography-qa
sudo systemctl start geography-qa

# 检查服务状态
sudo systemctl status geography-qa

echo "部署完成！"
echo "访问地址: http://{public_ip}:8501"
"""

        # 保存部署脚本
        with open("deploy.sh", "w") as f:
            f.write(script_content)
        
        # 设置执行权限
        os.chmod("deploy.sh", 0o755)
        print("部署脚本已创建: deploy.sh")
    
    def create_nginx_config(self, public_ip):
        """创建Nginx配置文件"""
        nginx_config = f"""server {{
    listen 80;
    server_name {public_ip};
    
    location / {{
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }}
}}
"""
        
        with open("nginx.conf", "w") as f:
            f.write(nginx_config)
        
        print("Nginx配置文件已创建: nginx.conf")
    
    def create_docker_compose(self):
        """创建Docker Compose配置"""
        docker_compose = """version: '3.8'

services:
  geography-qa:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
      - ./models:/app/models
    environment:
      - STREAMLIT_SERVER_PORT=8501
      - STREAMLIT_SERVER_ADDRESS=0.0.0.0
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 4G
        reservations:
          memory: 2G

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - geography-qa
    restart: unless-stopped
"""
        
        with open("docker-compose.yml", "w") as f:
            f.write(docker_compose)
        
        print("Docker Compose配置已创建: docker-compose.yml")
    
    def create_dockerfile(self):
        """创建Dockerfile"""
        dockerfile = """FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8501

# 启动命令
CMD ["streamlit", "run", "web_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
"""
        
        with open("Dockerfile", "w") as f:
            f.write(dockerfile)
        
        print("Dockerfile已创建")
    
    def create_ssl_cert(self, domain):
        """创建SSL证书配置"""
        ssl_config = f"""# SSL证书配置
# 使用Let's Encrypt免费证书
# 安装certbot: sudo apt install certbot python3-certbot-nginx

# 获取证书命令:
# sudo certbot --nginx -d {domain}

# 自动续期:
# sudo crontab -e
# 0 12 * * * /usr/bin/certbot renew --quiet
"""
        
        with open("ssl_setup.md", "w") as f:
            f.write(ssl_config)
        
        print("SSL配置说明已创建: ssl_setup.md")

def main():
    """主函数"""
    print("=== 腾讯云地理问答系统部署工具 ===\n")
    
    # 检查环境变量
    secret_id = os.getenv('TENCENT_SECRET_ID')
    secret_key = os.getenv('TENCENT_SECRET_KEY')
    
    if not secret_id or not secret_key:
        print("请设置环境变量:")
        print("export TENCENT_SECRET_ID='your_secret_id'")
        print("export TENCENT_SECRET_KEY='your_secret_key'")
        return
    
    # 创建部署器
    deployer = TencentCloudDeployer(secret_id, secret_key)
    
    print("选择部署方式:")
    print("1. 轻量应用服务器")
    print("2. 云服务器CVM")
    print("3. 仅生成配置文件")
    
    choice = input("请输入选择 (1-3): ").strip()
    
    if choice == "1":
        # 轻量应用服务器部署
        instance_name = input("请输入实例名称 (默认: geography-qa-system): ").strip()
        if not instance_name:
            instance_name = "geography-qa-system"
        
        instance_id = deployer.create_lighthouse_instance(instance_name)
        if instance_id:
            print(f"实例创建成功，ID: {instance_id}")
            
            # 等待实例就绪
            instance_info = deployer.wait_for_instance_ready(instance_id)
            if instance_info and instance_info['public_ip']:
                print(f"实例公网IP: {instance_info['public_ip']}")
                
                # 创建部署脚本
                deployer.create_deployment_script(instance_info['public_ip'])
                deployer.create_nginx_config(instance_info['public_ip'])
                
                print(f"\n部署说明:")
                print(f"1. 将项目文件上传到服务器: {instance_info['public_ip']}")
                print(f"2. 运行部署脚本: bash deploy.sh")
                print(f"3. 访问地址: http://{instance_info['public_ip']}:8501")
    
    elif choice == "2":
        print("云服务器CVM部署功能开发中...")
    
    elif choice == "3":
        # 仅生成配置文件
        domain = input("请输入域名 (可选): ").strip()
        public_ip = input("请输入服务器IP: ").strip()
        
        deployer.create_deployment_script(public_ip)
        deployer.create_nginx_config(public_ip)
        deployer.create_docker_compose()
        deployer.create_dockerfile()
        
        if domain:
            deployer.create_ssl_cert(domain)
        
        print("\n配置文件已生成完成！")
        print("请根据实际情况修改配置文件，然后部署到服务器。")
    
    else:
        print("无效选择")

if __name__ == "__main__":
    main()