#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
地理问答系统推理脚本
"""

import torch
from transformers import AutoTokenizer, AutoModelForQuestionAnswering
import json
import numpy as np
from typing import Dict, List, Tuple

class GeographyQA:
    def __init__(self, model_path: str = "./models"):
        """
        初始化地理问答系统
        
        Args:
            model_path: 训练好的模型路径
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"使用设备: {self.device}")
        
        # 加载模型和分词器
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForQuestionAnswering.from_pretrained(model_path)
        self.model.to(self.device)
        self.model.eval()
        
        # 加载地理知识库
        self.knowledge_base = self.load_knowledge_base()
        
        print("地理问答系统初始化完成")
    
    def load_knowledge_base(self) -> List[Dict]:
        """加载地理知识库"""
        try:
            with open("data/geography_qa_dataset.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print("警告: 未找到知识库文件，将使用内置知识")
            return []
    
    def find_relevant_context(self, question: str) -> str:
        """
        根据问题找到最相关的上下文
        
        Args:
            question: 用户问题
            
        Returns:
            最相关的上下文
        """
        if not self.knowledge_base:
            return "地理知识库未加载"
        
        # 简单的关键词匹配
        question_lower = question.lower()
        best_match = None
        best_score = 0
        
        for item in self.knowledge_base:
            score = 0
            # 检查问题中的关键词是否在答案中出现
            for word in question_lower.split():
                if word in item['answer'].lower():
                    score += 1
                if word in item['category'].lower():
                    score += 2
            
            if score > best_score:
                best_score = score
                best_match = item
        
        if best_match:
            return best_match['answer']
        else:
            return "未找到相关信息"
    
    def answer_question(self, question: str, context: str = None) -> Dict:
        """
        回答问题
        
        Args:
            question: 用户问题
            context: 上下文（如果为None，将自动查找）
            
        Returns:
            包含答案的字典
        """
        if context is None:
            context = self.find_relevant_context(question)
        
        # 编码输入
        inputs = self.tokenizer(
            question,
            context,
            return_tensors="pt",
            max_length=512,
            truncation=True,
            padding=True
        )
        
        # 将输入移到设备上
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # 进行推理
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        # 获取答案的起始和结束位置
        start_scores = outputs.start_logits
        end_scores = outputs.end_logits
        
        # 找到最佳答案位置
        start_index = torch.argmax(start_scores)
        end_index = torch.argmax(end_scores)
        
        # 确保结束位置在开始位置之后
        if end_index < start_index:
            end_index = start_index + 1
        
        # 解码答案
        answer_tokens = inputs["input_ids"][0][start_index:end_index + 1]
        answer = self.tokenizer.decode(answer_tokens, skip_special_tokens=True)
        
        # 如果模型答案为空，使用知识库匹配
        if not answer.strip():
            answer = self.find_best_answer_from_kb(question)
        
        return {
            "question": question,
            "answer": answer,
            "context": context,
            "confidence": self.calculate_confidence(start_scores, end_scores),
            "source": "AI模型"
        }
    
    def find_best_answer_from_kb(self, question: str) -> str:
        """从知识库中找到最佳答案"""
        if not self.knowledge_base:
            return "抱歉，我无法回答这个问题。"
        
        # 简单的关键词匹配
        question_lower = question.lower()
        best_match = None
        best_score = 0
        
        for item in self.knowledge_base:
            score = 0
            # 计算问题与知识库项的相似度
            for word in question_lower.split():
                if word in item['question'].lower():
                    score += 3
                if word in item['answer'].lower():
                    score += 1
                if word in item['category'].lower():
                    score += 2
            
            if score > best_score:
                best_score = score
                best_match = item
        
        if best_match and best_score > 0:
            return best_match['answer']
        else:
            return "抱歉，我在知识库中没有找到相关信息。"
    
    def calculate_confidence(self, start_scores: torch.Tensor, end_scores: torch.Tensor) -> float:
        """计算答案的置信度"""
        start_prob = torch.softmax(start_scores, dim=-1).max().item()
        end_prob = torch.softmax(end_scores, dim=-1).max().item()
        return (start_prob + end_prob) / 2
    
    def get_knowledge_categories(self) -> List[str]:
        """获取知识库中的分类"""
        if not self.knowledge_base:
            return []
        
        categories = set()
        for item in self.knowledge_base:
            categories.add(item['category'])
        
        return list(categories)
    
    def get_questions_by_category(self, category: str) -> List[str]:
        """根据分类获取问题列表"""
        if not self.knowledge_base:
            return []
        
        questions = []
        for item in self.knowledge_base:
            if item['category'] == category:
                questions.append(item['question'])
        
        return questions
    
    def add_knowledge(self, question: str, answer: str, category: str = "其他", difficulty: str = "中等"):
        """添加新的知识到知识库"""
        new_knowledge = {
            "question": question,
            "answer": answer,
            "category": category,
            "difficulty": difficulty
        }
        
        self.knowledge_base.append(new_knowledge)
        
        # 保存到文件
        try:
            with open("data/geography_qa_dataset.json", "w", encoding="utf-8") as f:
                json.dump(self.knowledge_base, f, ensure_ascii=False, indent=2)
            print("新知识已添加到知识库")
        except Exception as e:
            print(f"保存知识库失败: {e}")

def main():
    """测试函数"""
    # 初始化问答系统
    qa_system = GeographyQA()
    
    # 测试问题
    test_questions = [
        "中国的首都是哪个城市？",
        "长江有多长？",
        "珠穆朗玛峰在哪里？"
    ]
    
    print("=== 地理问答系统测试 ===\n")
    
    for question in test_questions:
        print(f"问题: {question}")
        result = qa_system.answer_question(question)
        print(f"答案: {result['answer']}")
        print(f"置信度: {result['confidence']:.3f}")
        print(f"来源: {result['source']}")
        print("-" * 50)

if __name__ == "__main__":
    main()