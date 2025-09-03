"""
地理问答模型训练
"""
import json
from typing import List, Dict, Tuple
import os

try:
    import torch
    from torch.utils.data import Dataset, DataLoader
    from transformers import (
        AutoTokenizer, 
        AutoModelForQuestionAnswering, 
        TrainingArguments, 
        Trainer,
        pipeline
    )
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    print("PyTorch未安装，仅使用简单问答功能")

try:
    import jieba
    HAS_JIEBA = True
except ImportError:
    HAS_JIEBA = False
    print("jieba未安装，使用简单分词")

try:
    import opencc
    HAS_OPENCC = True
except ImportError:
    HAS_OPENCC = False
    print("opencc未安装，跳过繁简转换")

if HAS_TORCH:
    class GeographyQADataset(Dataset):
        def __init__(self, data_path: str, tokenizer, max_length: int = 512):
            self.tokenizer = tokenizer
            self.max_length = max_length
            if HAS_OPENCC:
                self.converter = opencc.OpenCC('t2s')  # 繁体转简体
            else:
                self.converter = None
            
            with open(data_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            
            self.processed_data = self._preprocess_data()
    
    def _preprocess_data(self):
        """预处理数据，将问答对转换为适合模型的格式"""
        processed = []
        
        for item in self.data:
            question = self.converter.convert(item['question'])
            answer = self.converter.convert(item['answer'])
            
            # 对于问答任务，我们将答案作为context，问题作为question
            context = answer
            
            processed.append({
                'question': question,
                'context': context,
                'answer': answer,
                'start_position': 0,  # 答案在context中的开始位置
                'end_position': len(answer) - 1  # 答案在context中的结束位置
            })
        
        return processed
    
    def __len__(self):
        return len(self.processed_data)
    
    def __getitem__(self, idx):
        item = self.processed_data[idx]
        
        # 编码问题和上下文
        encoding = self.tokenizer(
            item['question'],
            item['context'],
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'start_positions': torch.tensor(item['start_position'], dtype=torch.long),
            'end_positions': torch.tensor(item['end_position'], dtype=torch.long)
        }

class GeographyQAModel:
    def __init__(self, model_name: str = "hfl/chinese-bert-wwm-ext"):
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForQuestionAnswering.from_pretrained(model_name)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        
    def train(self, train_data_path: str, val_data_path: str, output_dir: str = "/workspace/models/trained_model"):
        """训练模型"""
        
        # 创建数据集
        train_dataset = GeographyQADataset(train_data_path, self.tokenizer)
        val_dataset = GeographyQADataset(val_data_path, self.tokenizer)
        
        # 设置训练参数
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=3,
            per_device_train_batch_size=8,
            per_device_eval_batch_size=8,
            warmup_steps=500,
            weight_decay=0.01,
            logging_dir=f'{output_dir}/logs',
            logging_steps=10,
            evaluation_strategy="steps",
            eval_steps=500,
            save_strategy="steps",
            save_steps=500,
            load_best_model_at_end=True,
        )
        
        # 创建训练器
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            tokenizer=self.tokenizer,
        )
        
        # 开始训练
        print("开始训练模型...")
        trainer.train()
        
        # 保存模型
        trainer.save_model()
        self.tokenizer.save_pretrained(output_dir)
        print(f"模型已保存到: {output_dir}")
    
    def load_model(self, model_path: str):
        """加载训练好的模型"""
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForQuestionAnswering.from_pretrained(model_path)
        self.model.to(self.device)
        print(f"模型已从 {model_path} 加载")
    
    def answer_question(self, question: str, context: str = None) -> str:
        """回答问题"""
        if context is None:
            # 如果没有提供上下文，使用简单的关键词匹配从训练数据中找到相关上下文
            context = self._find_relevant_context(question)
        
        # 创建问答pipeline
        qa_pipeline = pipeline(
            "question-answering",
            model=self.model,
            tokenizer=self.tokenizer,
            device=0 if torch.cuda.is_available() else -1
        )
        
        result = qa_pipeline(question=question, context=context)
        return result['answer']
    
    def _find_relevant_context(self, question: str) -> str:
        """根据问题找到相关的上下文"""
        # 这里可以实现更复杂的检索逻辑
        # 简单起见，返回一个通用的地理知识上下文
        return """中国是一个地域辽阔的国家，拥有34个省级行政区，包括23个省、5个自治区、4个直辖市和2个特别行政区。
        中国的主要河流有长江、黄河、珠江等，主要山脉有喜马拉雅山、昆仑山、天山等。
        各省都有自己的省会城市，比如北京是首都，上海是直辖市，广东省的省会是广州，四川省的省会是成都。"""

class SimpleGeographyQA:
    """简单的基于规则的地理问答系统，用于快速演示"""
    
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
        words1 = set(jieba.cut(s1))
        words2 = set(jieba.cut(s2))
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _keyword_match(self, question: str) -> str:
        """基于关键词的匹配"""
        keywords = list(jieba.cut(question))
        
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
        
        return best_match if best_match else "抱歉，我无法回答这个问题。请尝试问一些关于中国地理的问题。"

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