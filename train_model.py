#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
地理问答系统模型训练脚本
"""

import json
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForQuestionAnswering,
    TrainingArguments, 
    Trainer,
    DataCollatorWithPadding
)
from datasets import Dataset
import numpy as np
from sklearn.model_selection import train_test_split
import os

class GeographyQATrainer:
    def __init__(self, model_name="bert-base-chinese", max_length=512):
        self.model_name = model_name
        self.max_length = max_length
        self.tokenizer = None
        self.model = None
        
    def load_data(self, data_path):
        """加载地理问答数据"""
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 将问答数据转换为训练格式
        formatted_data = []
        for item in data:
            # 将问题和答案组合成输入文本
            context = item['answer']
            question = item['question']
            
            # 找到答案在上下文中的位置
            start_pos = 0
            end_pos = len(context)
            
            formatted_data.append({
                'question': question,
                'context': context,
                'answer': item['answer'],
                'start_positions': start_pos,
                'end_positions': end_pos,
                'category': item['category'],
                'difficulty': item['difficulty']
            })
        
        return formatted_data
    
    def prepare_dataset(self, data):
        """准备数据集"""
        # 分割训练集和验证集
        train_data, val_data = train_test_split(data, test_size=0.2, random_state=42)
        
        # 转换为Dataset格式
        train_dataset = Dataset.from_list(train_data)
        val_dataset = Dataset.from_list(val_data)
        
        return train_dataset, val_dataset
    
    def tokenize_function(self, examples):
        """分词函数"""
        # 将问题和上下文组合
        questions = examples['question']
        contexts = examples['context']
        
        # 编码输入
        tokenized = self.tokenizer(
            questions,
            contexts,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        # 处理答案位置
        start_positions = examples['start_positions']
        end_positions = examples['end_positions']
        
        # 将字符位置转换为token位置
        tokenized['start_positions'] = start_positions
        tokenized['end_positions'] = end_positions
        
        return tokenized
    
    def train(self, train_dataset, val_dataset, output_dir="./models"):
        """训练模型"""
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 设置训练参数
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=3,
            per_device_train_batch_size=8,
            per_device_eval_batch_size=8,
            warmup_steps=500,
            weight_decay=0.01,
            logging_dir=f"{output_dir}/logs",
            logging_steps=100,
            evaluation_strategy="steps",
            eval_steps=500,
            save_steps=1000,
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
        )
        
        # 创建数据收集器
        data_collator = DataCollatorWithPadding(tokenizer=self.tokenizer)
        
        # 创建训练器
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            tokenizer=self.tokenizer,
            data_collator=data_collator,
        )
        
        # 开始训练
        print("开始训练模型...")
        trainer.train()
        
        # 保存模型
        trainer.save_model()
        self.tokenizer.save_pretrained(output_dir)
        print(f"模型已保存到 {output_dir}")
        
        return trainer
    
    def load_model(self, model_path):
        """加载预训练模型"""
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForQuestionAnswering.from_pretrained(model_path)
        print(f"模型已从 {model_path} 加载")
        
    def initialize_model(self):
        """初始化模型和分词器"""
        print(f"正在加载模型: {self.model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForQuestionAnswering.from_pretrained(self.model_name)
        print("模型加载完成")

def main():
    """主函数"""
    # 创建训练器实例
    trainer = GeographyQATrainer()
    
    # 初始化模型
    trainer.initialize_model()
    
    # 加载数据
    print("正在加载数据...")
    data = trainer.load_data("data/geography_qa_dataset.json")
    
    # 准备数据集
    print("正在准备数据集...")
    train_dataset, val_dataset = trainer.prepare_dataset(data)
    
    # 对数据集进行分词
    print("正在对数据集进行分词...")
    train_dataset = train_dataset.map(
        trainer.tokenize_function, 
        batched=True, 
        remove_columns=train_dataset.column_names
    )
    val_dataset = val_dataset.map(
        trainer.tokenize_function, 
        batched=True, 
        remove_columns=val_dataset.column_names
    )
    
    # 开始训练
    print("开始训练...")
    trainer.train(train_dataset, val_dataset)
    
    print("训练完成！")

if __name__ == "__main__":
    main()