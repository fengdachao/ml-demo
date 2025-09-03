"""
简单地理问答系统
"""
import json
import re
from typing import Dict, List

class SimpleGeographyQA:
    """简单的基于规则的地理问答系统"""
    
    def __init__(self):
        self.qa_data = {}
        self.load_qa_data()
    
    def load_qa_data(self):
        """加载问答数据"""
        try:
            with open("/workspace/data/geography_qa.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # 构建问答字典
            for item in data:
                question = item['question'].lower().strip('？?')
                self.qa_data[question] = item['answer']
                
        except FileNotFoundError:
            print("问答数据文件未找到，请先生成数据集")
    
    def simple_tokenize(self, text: str) -> List[str]:
        """简单的中文分词"""
        # 简单的中文字符分词
        words = []
        current_word = ""
        
        for char in text:
            if '\u4e00' <= char <= '\u9fff':  # 中文字符
                if current_word and not ('\u4e00' <= current_word[-1] <= '\u9fff'):
                    words.append(current_word)
                    current_word = char
                else:
                    current_word += char
            else:
                if current_word:
                    if '\u4e00' <= current_word[-1] <= '\u9fff':
                        words.append(current_word)
                        current_word = char
                    else:
                        current_word += char
                else:
                    current_word += char
        
        if current_word:
            words.append(current_word)
        
        return [w.strip() for w in words if w.strip()]
    
    def answer(self, question: str) -> str:
        """回答问题"""
        question_clean = question.lower().strip('？?')
        
        # 直接匹配
        if question_clean in self.qa_data:
            return self.qa_data[question_clean]
        
        # 模糊匹配
        for q, a in self.qa_data.items():
            if self._similarity(question_clean, q) > 0.7:
                return a
        
        # 关键词匹配
        return self._keyword_match(question)
    
    def _similarity(self, s1: str, s2: str) -> float:
        """计算两个字符串的相似度"""
        words1 = set(self.simple_tokenize(s1))
        words2 = set(self.simple_tokenize(s2))
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _keyword_match(self, question: str) -> str:
        """基于关键词的匹配"""
        keywords = self.simple_tokenize(question)
        
        best_match = ""
        best_score = 0
        
        for q, a in self.qa_data.items():
            score = 0
            for keyword in keywords:
                if keyword in q:
                    score += 1
            
            if score > best_score:
                best_score = score
                best_match = a
        
        return best_match if best_match else "抱歉，我无法回答这个问题。请尝试问一些关于中国地理的问题，比如省会城市、河流、山脉等。"

if __name__ == "__main__":
    # 简单测试
    qa_system = SimpleGeographyQA()
    
    test_questions = [
        "北京是哪个省的省会？",
        "长江有多长？",
        "珠穆朗玛峰在哪里？"
    ]
    
    for question in test_questions:
        answer = qa_system.answer(question)
        print(f"问题: {question}")
        print(f"答案: {answer}")
        print("-" * 50)