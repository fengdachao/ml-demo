#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
地理问答系统启动脚本
提供菜单式操作界面
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def print_banner():
    """打印系统横幅"""
    print("""
🌍 地理问答系统
==========================================
🤖 AI智能地理问答 | 📚 知识库管理 | 🌐 Web界面
==========================================
""")

def check_environment():
    """检查运行环境"""
    print("🔍 检查运行环境...")
    
    # 检查Python版本
    python_version = sys.version_info
    if python_version < (3, 8):
        print(f"❌ Python版本过低: {python_version.major}.{python_version.minor}")
        print("   需要Python 3.8+")
        return False
    
    print(f"✅ Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # 检查必要文件
    required_files = [
        "web_app.py",
        "qa_model.py", 
        "data/geography_qa_dataset.json"
    ]
    
    for file_path in required_files:
        if not Path(file_path).exists():
            print(f"❌ 缺少文件: {file_path}")
            return False
    
    print("✅ 必要文件检查通过")
    return True

def install_dependencies():
    """安装依赖"""
    print("📚 安装依赖包...")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True)
        print("✅ 依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        return False
    except FileNotFoundError:
        print("❌ 未找到requirements.txt文件")
        return False

def start_web_app(port=8501, host="localhost"):
    """启动Web应用"""
    print(f"🚀 启动地理问答系统...")
    print(f"🌐 访问地址: http://{host}:{port}")
    print("按 Ctrl+C 停止服务")
    
    try:
        # 设置环境变量
        env = os.environ.copy()
        env['STREAMLIT_SERVER_PORT'] = str(port)
        env['STREAMLIT_SERVER_ADDRESS'] = host
        
        # 启动Streamlit
        cmd = [sys.executable, "-m", "streamlit", "run", "web_app.py"]
        subprocess.run(cmd, env=env)
        
    except KeyboardInterrupt:
        print("\n🛑 服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

def train_model():
    """训练模型"""
    print("🎯 开始训练模型...")
    
    try:
        result = subprocess.run([sys.executable, "train_model.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 模型训练完成")
        else:
            print(f"❌ 模型训练失败: {result.stderr}")
            
    except Exception as e:
        print(f"❌ 训练脚本执行失败: {e}")

def test_system():
    """测试系统"""
    print("🧪 运行系统测试...")
    
    try:
        subprocess.run([sys.executable, "test_system.py"])
    except Exception as e:
        print(f"❌ 测试脚本执行失败: {e}")

def open_browser(port=8501):
    """打开浏览器"""
    url = f"http://localhost:{port}"
    print(f"🌐 正在打开浏览器: {url}")
    
    try:
        webbrowser.open(url)
        print("✅ 浏览器已打开")
    except Exception as e:
        print(f"❌ 无法打开浏览器: {e}")
        print(f"请手动访问: {url}")

def show_help():
    """显示帮助信息"""
    print("""
📖 使用说明
==========================================

🎯 主要功能:
  1. 启动Web界面 - 启动地理问答系统Web界面
  2. 训练模型 - 训练AI问答模型
  3. 系统测试 - 运行系统功能测试
  4. 安装依赖 - 安装必要的Python包

🌐 Web界面功能:
  - 智能问答: 输入地理问题，获取AI回答
  - 知识库管理: 浏览、搜索、添加地理知识
  - 分类浏览: 按分类和难度查看知识
  - 系统管理: 查看系统状态和配置

🔧 技术特性:
  - 基于Transformer的AI模型
  - 支持中文地理知识问答
  - 美观的Streamlit界面
  - 支持腾讯云部署

📁 文件说明:
  - web_app.py: Web界面主程序
  - qa_model.py: 问答模型核心
  - train_model.py: 模型训练脚本
  - data/: 地理知识数据集
  - models/: 训练好的模型文件

🚀 快速开始:
  1. 选择"启动Web界面"
  2. 等待系统启动
  3. 在浏览器中访问系统
  4. 开始使用地理问答功能

==========================================
""")

def main_menu():
    """主菜单"""
    while True:
        print("\n" + "=" * 50)
        print("📋 主菜单")
        print("=" * 50)
        print("1. 🚀 启动Web界面")
        print("2. 🎯 训练模型")
        print("3. 🧪 系统测试")
        print("4. 📚 安装依赖")
        print("5. 🌐 打开浏览器")
        print("6. 📖 使用说明")
        print("7. 🔍 环境检查")
        print("0. 🚪 退出")
        print("=" * 50)
        
        try:
            choice = input("请选择操作 (0-7): ").strip()
            
            if choice == "0":
                print("👋 再见！")
                break
            elif choice == "1":
                port = input("请输入端口号 (默认8501): ").strip()
                port = int(port) if port.isdigit() else 8501
                start_web_app(port)
            elif choice == "2":
                train_model()
            elif choice == "3":
                test_system()
            elif choice == "4":
                install_dependencies()
            elif choice == "5":
                port = input("请输入端口号 (默认8501): ").strip()
                port = int(port) if port.isdigit() else 8501
                open_browser(port)
            elif choice == "6":
                show_help()
            elif choice == "7":
                check_environment()
            else:
                print("❌ 无效选择，请输入0-7")
                
        except KeyboardInterrupt:
            print("\n\n👋 再见！")
            break
        except Exception as e:
            print(f"❌ 操作失败: {e}")
        
        input("\n按回车键继续...")

def main():
    """主函数"""
    print_banner()
    
    # 检查环境
    if not check_environment():
        print("\n⚠️  环境检查失败，请检查系统配置")
        response = input("是否继续? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            return
    
    # 显示主菜单
    main_menu()

if __name__ == "__main__":
    main()