#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
地理问答系统本地运行脚本
"""

import os
import sys
import subprocess
import argparse
import json
from pathlib import Path

def check_dependencies():
    """检查依赖是否安装"""
    required_packages = [
        'torch', 'transformers', 'streamlit', 'pandas', 'numpy'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ 缺少依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    print("✅ 所有依赖包已安装")
    return True

def check_data_files():
    """检查数据文件是否存在"""
    data_file = Path("data/geography_qa_dataset.json")
    if not data_file.exists():
        print("❌ 数据文件不存在: data/geography_qa_dataset.json")
        return False
    
    print("✅ 数据文件存在")
    return True

def check_model_files():
    """检查模型文件是否存在"""
    model_dir = Path("models")
    if not model_dir.exists():
        print("⚠️  模型目录不存在，将使用知识库匹配模式")
        return False
    
    # 检查是否有必要的模型文件
    model_files = list(model_dir.glob("*.bin")) + list(model_dir.glob("*.safetensors"))
    if not model_files:
        print("⚠️  模型文件不存在，将使用知识库匹配模式")
        return False
    
    print("✅ 模型文件存在")
    return True

def start_streamlit(port=8501, host="localhost"):
    """启动Streamlit应用"""
    print(f"🚀 启动地理问答系统...")
    print(f"🌐 访问地址: http://{host}:{port}")
    print("按 Ctrl+C 停止服务")
    
    try:
        # 启动Streamlit
        cmd = [
            sys.executable, "-m", "streamlit", "run", "web_app.py",
            "--server.port", str(port),
            "--server.address", host,
            "--server.headless", "true"
        ]
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n🛑 服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

def train_model():
    """训练模型"""
    print("🎯 开始训练模型...")
    
    if not check_data_files():
        return False
    
    try:
        # 运行训练脚本
        result = subprocess.run([sys.executable, "train_model.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 模型训练完成")
            return True
        else:
            print(f"❌ 模型训练失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 训练脚本执行失败: {e}")
        return False

def test_qa_system():
    """测试问答系统"""
    print("🧪 测试问答系统...")
    
    try:
        # 运行测试脚本
        result = subprocess.run([sys.executable, "qa_model.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 问答系统测试通过")
            return True
        else:
            print(f"❌ 问答系统测试失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 测试脚本执行失败: {e}")
        return False

def show_system_info():
    """显示系统信息"""
    print("📊 系统信息:")
    print(f"  Python版本: {sys.version}")
    print(f"  工作目录: {os.getcwd()}")
    
    # 检查文件结构
    print("\n📁 项目结构:")
    for item in Path(".").iterdir():
        if item.is_dir() and not item.name.startswith("."):
            print(f"  📂 {item.name}/")
        elif item.is_file() and item.suffix in [".py", ".json", ".txt", ".yml"]:
            print(f"  📄 {item.name}")
    
    # 检查数据统计
    try:
        with open("data/geography_qa_dataset.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            print(f"\n📚 知识库统计:")
            print(f"  总条目数: {len(data)}")
            
            categories = {}
            difficulties = {}
            for item in data:
                cat = item.get('category', '其他')
                diff = item.get('difficulty', '未知')
                categories[cat] = categories.get(cat, 0) + 1
                difficulties[diff] = difficulties.get(diff, 0) + 1
            
            print(f"  分类数: {len(categories)}")
            print(f"  难度等级: {len(difficulties)}")
            
    except Exception as e:
        print(f"  无法读取知识库: {e}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="地理问答系统本地运行工具")
    parser.add_argument("--port", type=int, default=8501, help="服务端口 (默认: 8501)")
    parser.add_argument("--host", default="localhost", help="服务地址 (默认: localhost)")
    parser.add_argument("--train", action="store_true", help="训练模型")
    parser.add_argument("--test", action="store_true", help="测试系统")
    parser.add_argument("--info", action="store_true", help="显示系统信息")
    
    args = parser.parse_args()
    
    print("🌍 地理问答系统")
    print("=" * 50)
    
    # 显示系统信息
    if args.info:
        show_system_info()
        return
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 检查数据文件
    if not check_data_files():
        sys.exit(1)
    
    # 检查模型文件
    has_model = check_model_files()
    
    # 训练模型
    if args.train:
        if train_model():
            has_model = True
        else:
            print("⚠️  模型训练失败，将使用知识库匹配模式")
    
    # 测试系统
    if args.test:
        test_qa_system()
        return
    
    # 启动Web界面
    if has_model:
        print("🤖 使用AI模型模式")
    else:
        print("📚 使用知识库匹配模式")
    
    start_streamlit(args.port, args.host)

if __name__ == "__main__":
    main()