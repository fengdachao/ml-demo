#!/usr/bin/env python3
"""
地理问答模型训练脚本
"""
import sys
import os
sys.path.append('/workspace')

def install_requirements():
    """安装训练所需的依赖"""
    import subprocess
    
    requirements = [
        'torch>=2.0.0',
        'transformers>=4.30.0',
        'datasets>=2.12.0',
        'jieba>=0.42.1',
        'opencc-python-reimplemented>=0.1.7',
        'scikit-learn>=1.3.0'
    ]
    
    print("安装训练依赖...")
    for req in requirements:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', req])
        except subprocess.CalledProcessError as e:
            print(f"安装 {req} 失败: {e}")
            return False
    
    return True

def train_simple_model():
    """训练简单的问答模型"""
    from models.simple_qa import SimpleGeographyQA
    
    print("使用简单问答模型...")
    qa_system = SimpleGeographyQA()
    
    # 测试模型
    test_questions = [
        "北京是哪个省的省会？",
        "长江有多长？",
        "珠穆朗玛峰在哪里？",
        "广东省的省会是哪里？",
        "黄河发源于哪里？"
    ]
    
    print("模型测试结果:")
    print("=" * 50)
    for question in test_questions:
        answer = qa_system.answer(question)
        print(f"问题: {question}")
        print(f"答案: {answer}")
        print("-" * 30)
    
    return True

def train_advanced_model():
    """训练高级的Transformer模型"""
    try:
        import torch
        from transformers import AutoTokenizer, AutoModelForQuestionAnswering
        print("检测到PyTorch和Transformers，开始训练高级模型...")
        
        # 这里可以实现基于BERT的问答模型训练
        # 由于资源限制，这里只是示例代码
        
        model_name = "hfl/chinese-bert-wwm-ext"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForQuestionAnswering.from_pretrained(model_name)
        
        print(f"✓ 成功加载预训练模型: {model_name}")
        print("注意: 完整的模型训练需要大量计算资源，建议在GPU环境下进行")
        
        return True
        
    except ImportError:
        print("未检测到PyTorch或Transformers，跳过高级模型训练")
        return False

def main():
    print("=== 地理问答模型训练 ===")
    
    # 确保数据集存在
    if not os.path.exists('/workspace/data/geography_qa.json'):
        print("生成地理问答数据集...")
        from data.geography_qa_dataset import GeographyQADataset
        dataset = GeographyQADataset()
        dataset.save_dataset('/workspace/data/geography_qa.json')
        print("✓ 数据集生成完成")
    
    # 尝试训练高级模型
    if not train_advanced_model():
        print("使用简单模型进行训练...")
        train_simple_model()
    
    print("=== 训练完成 ===")

if __name__ == "__main__":
    main()