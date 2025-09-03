#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
地理问答系统测试脚本
"""

import json
import os
import sys
from pathlib import Path

def test_data_loading():
    """测试数据加载功能"""
    print("🧪 测试数据加载...")
    
    try:
        data_file = Path("data/geography_qa_dataset.json")
        if not data_file.exists():
            print("❌ 数据文件不存在")
            return False
        
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            print("❌ 数据格式错误，应为列表")
            return False
        
        if len(data) == 0:
            print("❌ 数据为空")
            return False
        
        print(f"✅ 数据加载成功，共 {len(data)} 条记录")
        
        # 检查数据结构
        required_fields = ['question', 'answer', 'category', 'difficulty']
        for i, item in enumerate(data):
            for field in required_fields:
                if field not in item:
                    print(f"❌ 第 {i+1} 条记录缺少字段: {field}")
                    return False
        
        print("✅ 数据结构检查通过")
        return True
        
    except Exception as e:
        print(f"❌ 数据加载失败: {e}")
        return False

def test_qa_model():
    """测试问答模型"""
    print("\n🤖 测试问答模型...")
    
    try:
        # 尝试导入问答模型
        from qa_model import GeographyQA
        
        # 检查模型文件
        model_path = "./models"
        if os.path.exists(model_path):
            print("✅ 模型目录存在")
            try:
                qa_system = GeographyQA(model_path)
                print("✅ 模型加载成功")
                return True
            except Exception as e:
                print(f"⚠️  模型加载失败，将使用知识库模式: {e}")
        else:
            print("⚠️  模型目录不存在，将使用知识库模式")
        
        # 测试知识库模式
        try:
            qa_system = GeographyQA()
            print("✅ 知识库模式初始化成功")
            return True
        except Exception as e:
            print(f"❌ 知识库模式初始化失败: {e}")
            return False
            
    except ImportError as e:
        print(f"❌ 无法导入问答模型: {e}")
        return False
    except Exception as e:
        print(f"❌ 问答模型测试失败: {e}")
        return False

def test_web_app():
    """测试Web应用"""
    print("\n🌐 测试Web应用...")
    
    try:
        # 检查Streamlit是否可用
        import streamlit as st
        print("✅ Streamlit可用")
        
        # 检查Web应用文件
        web_app_file = Path("web_app.py")
        if not web_app_file.exists():
            print("❌ Web应用文件不存在")
            return False
        
        print("✅ Web应用文件存在")
        return True
        
    except ImportError:
        print("❌ Streamlit未安装")
        return False
    except Exception as e:
        print(f"❌ Web应用测试失败: {e}")
        return False

def test_dependencies():
    """测试依赖包"""
    print("\n📚 测试依赖包...")
    
    required_packages = [
        'torch',
        'transformers', 
        'streamlit',
        'pandas',
        'numpy',
        'scikit-learn'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  缺少依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    print("✅ 所有依赖包已安装")
    return True

def test_file_structure():
    """测试文件结构"""
    print("\n📁 测试文件结构...")
    
    required_files = [
        "requirements.txt",
        "data/geography_qa_dataset.json",
        "train_model.py",
        "qa_model.py", 
        "web_app.py",
        "README.md"
    ]
    
    required_dirs = [
        "data",
        "scripts"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
            print(f"❌ {file_path}")
        else:
            print(f"✅ {file_path}")
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing_dirs.append(dir_path)
            print(f"❌ {dir_path}/")
        else:
            print(f"✅ {dir_path}/")
    
    if missing_files or missing_dirs:
        print(f"\n⚠️  缺少文件/目录:")
        for item in missing_files + missing_dirs:
            print(f"  - {item}")
        return False
    
    print("✅ 文件结构完整")
    return True

def run_quick_test():
    """运行快速测试"""
    print("\n🚀 运行快速问答测试...")
    
    try:
        from qa_model import GeographyQA
        
        # 初始化问答系统
        qa_system = GeographyQA()
        
        # 测试问题
        test_questions = [
            "中国的首都是哪个城市？",
            "长江有多长？",
            "珠穆朗玛峰在哪里？"
        ]
        
        for question in test_questions:
            print(f"\n问题: {question}")
            try:
                result = qa_system.answer_question(question)
                print(f"答案: {result['answer']}")
                if 'confidence' in result:
                    print(f"置信度: {result['confidence']:.3f}")
                print("✅ 回答成功")
            except Exception as e:
                print(f"❌ 回答失败: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 快速测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🌍 地理问答系统 - 系统测试")
    print("=" * 50)
    
    # 运行各项测试
    tests = [
        ("文件结构", test_file_structure),
        ("依赖包", test_dependencies),
        ("数据加载", test_data_loading),
        ("问答模型", test_qa_model),
        ("Web应用", test_web_app)
    ]
    
    test_results = {}
    for test_name, test_func in tests:
        try:
            result = test_func()
            test_results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name}测试异常: {e}")
            test_results[test_name] = False
    
    # 显示测试结果
    print("\n" + "=" * 50)
    print("📊 测试结果汇总:")
    
    passed = 0
    total = len(tests)
    
    for test_name, result in test_results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总体结果: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统可以正常使用。")
        
        # 询问是否运行快速测试
        try:
            response = input("\n是否运行快速问答测试? (y/N): ").strip().lower()
            if response in ['y', 'yes']:
                run_quick_test()
        except KeyboardInterrupt:
            print("\n测试已取消")
    else:
        print("⚠️  部分测试失败，请检查系统配置。")
        
        # 提供修复建议
        print("\n🔧 修复建议:")
        if not test_results.get("依赖包", True):
            print("  1. 安装依赖: pip install -r requirements.txt")
        if not test_results.get("数据加载", True):
            print("  2. 检查数据文件: data/geography_qa_dataset.json")
        if not test_results.get("问答模型", True):
            print("  3. 训练模型: python train_model.py")
        if not test_results.get("Web应用", True):
            print("  4. 检查Web应用文件: web_app.py")

if __name__ == "__main__":
    main()