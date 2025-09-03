"""
地理问答数据集生成器
"""
import json
import random
from typing import List, Dict, Tuple

class GeographyQADataset:
    def __init__(self):
        self.qa_pairs = []
        self._generate_dataset()
    
    def _generate_dataset(self):
        """生成地理问答数据集"""
        
        # 中国省份和首府
        provinces_capitals = {
            "北京": "北京", "天津": "天津", "上海": "上海", "重庆": "重庆",
            "河北": "石家庄", "山西": "太原", "辽宁": "沈阳", "吉林": "长春",
            "黑龙江": "哈尔滨", "江苏": "南京", "浙江": "杭州", "安徽": "合肥",
            "福建": "福州", "江西": "南昌", "山东": "济南", "河南": "郑州",
            "湖北": "武汉", "湖南": "长沙", "广东": "广州", "海南": "海口",
            "四川": "成都", "贵州": "贵阳", "云南": "昆明", "陕西": "西安",
            "甘肃": "兰州", "青海": "西宁", "台湾": "台北", "内蒙古": "呼和浩特",
            "广西": "南宁", "西藏": "拉萨", "宁夏": "银川", "新疆": "乌鲁木齐"
        }
        
        # 主要河流
        rivers = {
            "长江": {"长度": "6300公里", "发源地": "青藏高原", "流向": "东海"},
            "黄河": {"长度": "5464公里", "发源地": "青藏高原", "流向": "渤海"},
            "珠江": {"长度": "2320公里", "发源地": "云贵高原", "流向": "南海"},
            "松花江": {"长度": "1900公里", "发源地": "长白山", "流向": "黑龙江"}
        }
        
        # 主要山脉
        mountains = {
            "喜马拉雅山": {"最高峰": "珠穆朗玛峰", "海拔": "8848.86米", "位置": "中国西藏与尼泊尔边界"},
            "昆仑山": {"最高峰": "公格尔峰", "海拔": "7649米", "位置": "新疆、青海、西藏"},
            "天山": {"最高峰": "托木尔峰", "海拔": "7443米", "位置": "新疆"},
            "秦岭": {"最高峰": "太白山", "海拔": "3771米", "位置": "陕西、甘肃、河南"}
        }
        
        # 生成省份首府问答
        for province, capital in provinces_capitals.items():
            self.qa_pairs.extend([
                {
                    "question": f"{province}省的省会是哪里？",
                    "answer": f"{province}省的省会是{capital}。",
                    "category": "省会城市"
                },
                {
                    "question": f"{capital}是哪个省的省会？",
                    "answer": f"{capital}是{province}省的省会。",
                    "category": "省会城市"
                }
            ])
        
        # 生成河流问答
        for river, info in rivers.items():
            self.qa_pairs.extend([
                {
                    "question": f"{river}有多长？",
                    "answer": f"{river}全长{info['长度']}。",
                    "category": "河流"
                },
                {
                    "question": f"{river}发源于哪里？",
                    "answer": f"{river}发源于{info['发源地']}。",
                    "category": "河流"
                },
                {
                    "question": f"{river}最终流向哪里？",
                    "answer": f"{river}最终流入{info['流向']}。",
                    "category": "河流"
                }
            ])
        
        # 生成山脉问答
        for mountain, info in mountains.items():
            self.qa_pairs.extend([
                {
                    "question": f"{mountain}的最高峰是什么？",
                    "answer": f"{mountain}的最高峰是{info['最高峰']}。",
                    "category": "山脉"
                },
                {
                    "question": f"{info['最高峰']}海拔多高？",
                    "answer": f"{info['最高峰']}海拔{info['海拔']}。",
                    "category": "山脉"
                },
                {
                    "question": f"{mountain}位于哪里？",
                    "answer": f"{mountain}位于{info['位置']}。",
                    "category": "山脉"
                }
            ])
        
        # 添加一些综合性问题
        comprehensive_qa = [
            {
                "question": "中国最长的河流是什么？",
                "answer": "中国最长的河流是长江，全长6300公里。",
                "category": "综合"
            },
            {
                "question": "世界最高峰在中国的哪个地区？",
                "answer": "世界最高峰珠穆朗玛峰位于中国西藏与尼泊尔的边界上。",
                "category": "综合"
            },
            {
                "question": "中国有多少个省级行政区？",
                "answer": "中国共有34个省级行政区，包括23个省、5个自治区、4个直辖市和2个特别行政区。",
                "category": "综合"
            }
        ]
        
        self.qa_pairs.extend(comprehensive_qa)
        
        # 随机打乱数据
        random.shuffle(self.qa_pairs)
    
    def get_train_test_split(self, test_ratio: float = 0.2) -> Tuple[List[Dict], List[Dict]]:
        """获取训练和测试数据集"""
        split_idx = int(len(self.qa_pairs) * (1 - test_ratio))
        train_data = self.qa_pairs[:split_idx]
        test_data = self.qa_pairs[split_idx:]
        return train_data, test_data
    
    def save_dataset(self, filepath: str):
        """保存数据集到文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.qa_pairs, f, ensure_ascii=False, indent=2)
    
    def load_dataset(self, filepath: str):
        """从文件加载数据集"""
        with open(filepath, 'r', encoding='utf-8') as f:
            self.qa_pairs = json.load(f)

if __name__ == "__main__":
    # 生成数据集
    dataset = GeographyQADataset()
    
    # 保存完整数据集
    dataset.save_dataset("/workspace/data/geography_qa.json")
    
    # 获取训练和测试数据
    train_data, test_data = dataset.get_train_test_split()
    
    # 保存训练和测试数据
    with open("/workspace/data/train_data.json", 'w', encoding='utf-8') as f:
        json.dump(train_data, f, ensure_ascii=False, indent=2)
    
    with open("/workspace/data/test_data.json", 'w', encoding='utf-8') as f:
        json.dump(test_data, f, ensure_ascii=False, indent=2)
    
    print(f"数据集生成完成！")
    print(f"总计问答对数: {len(dataset.qa_pairs)}")
    print(f"训练数据: {len(train_data)}")
    print(f"测试数据: {len(test_data)}")