#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能新闻搜索智能体
根据用户输入搜索相关新闻，并提供进一步的详细搜索功能
"""

import requests
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from urllib.parse import quote, urljoin
import time


class NewsAgent:
    """智能新闻搜索智能体"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.search_engines = {
            'bing': 'https://www.bing.com/news/search',
            'google': 'https://news.google.com/rss/search'
        }
    
    def search_news(self, query: str, limit: int = 10, days_back: int = 7) -> List[Dict]:
        """
        搜索新闻
        
        Args:
            query: 搜索关键词
            limit: 返回结果数量限制
            days_back: 搜索多少天内的新闻
            
        Returns:
            新闻列表，每个新闻包含标题、摘要、链接、发布时间等信息
        """
        news_results = []
        
        # 尝试多个搜索源
        try:
            # 使用 NewsAPI 风格的搜索
            news_results.extend(self._search_with_bing_news(query, limit // 2))
        except Exception as e:
            print(f"Bing News 搜索失败: {e}")
        
        try:
            # 使用其他新闻源
            news_results.extend(self._search_with_alternative_sources(query, limit // 2))
        except Exception as e:
            print(f"备用新闻源搜索失败: {e}")
        
        # 去重并按时间排序
        unique_news = self._deduplicate_news(news_results)
        sorted_news = sorted(unique_news, key=lambda x: x.get('published_at', ''), reverse=True)
        
        return sorted_news[:limit]
    
    def _search_with_bing_news(self, query: str, limit: int) -> List[Dict]:
        """使用 Bing 新闻搜索"""
        results = []
        
        # 模拟搜索结果（实际应用中应该调用真实的 API）
        sample_news = [
            {
                "title": f"关于'{query}'的最新发展报道",
                "summary": f"据最新消息，{query}相关事件有了新的进展。专家表示这一发展将对相关领域产生重要影响...",
                "url": f"https://example-news.com/news/{query.replace(' ', '-')}-latest-development",
                "published_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "source": "示例新闻网",
                "category": "综合新闻"
            },
            {
                "title": f"{query}市场分析：专家观点汇总",
                "summary": f"多位行业专家就{query}发表了看法，分析师认为未来发展趋势值得关注...",
                "url": f"https://example-finance.com/analysis/{query.replace(' ', '-')}-market-analysis",
                "published_at": (datetime.now() - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"),
                "source": "财经快报",
                "category": "财经"
            },
            {
                "title": f"{query}技术突破获得重大进展",
                "summary": f"科研团队在{query}领域取得重要突破，这项技术有望在未来几年内实现商业化应用...",
                "url": f"https://example-tech.com/breakthrough/{query.replace(' ', '-')}-tech-breakthrough",
                "published_at": (datetime.now() - timedelta(hours=4)).strftime("%Y-%m-%d %H:%M:%S"),
                "source": "科技日报",
                "category": "科技"
            }
        ]
        
        return sample_news[:limit]
    
    def _search_with_alternative_sources(self, query: str, limit: int) -> List[Dict]:
        """使用备用新闻源搜索"""
        results = []
        
        # 模拟更多新闻源的结果
        alternative_news = [
            {
                "title": f"{query}政策解读：影响与机遇并存",
                "summary": f"政府发布了关于{query}的新政策，业内人士分析认为这将带来新的机遇和挑战...",
                "url": f"https://example-policy.com/policy/{query.replace(' ', '-')}-policy-analysis",
                "published_at": (datetime.now() - timedelta(hours=6)).strftime("%Y-%m-%d %H:%M:%S"),
                "source": "政策解读网",
                "category": "政策"
            },
            {
                "title": f"{query}国际动态：全球视野下的新发展",
                "summary": f"国际社会对{query}相关发展表示关注，多国专家学者发表了不同观点...",
                "url": f"https://example-international.com/global/{query.replace(' ', '-')}-global-view",
                "published_at": (datetime.now() - timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S"),
                "source": "国际观察",
                "category": "国际"
            }
        ]
        
        return alternative_news[:limit]
    
    def _deduplicate_news(self, news_list: List[Dict]) -> List[Dict]:
        """去除重复新闻"""
        seen_titles = set()
        unique_news = []
        
        for news in news_list:
            title_key = news.get('title', '').lower().strip()
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_news.append(news)
        
        return unique_news
    
    def search_related_news(self, selected_news: Dict, limit: int = 8) -> List[Dict]:
        """
        根据选中的新闻搜索相关内容
        
        Args:
            selected_news: 用户选择的新闻
            limit: 返回结果数量限制
            
        Returns:
            相关新闻列表
        """
        # 从标题中提取关键词
        title = selected_news.get('title', '')
        keywords = self._extract_keywords(title)
        
        related_news = []
        
        for keyword in keywords[:3]:  # 使用前3个关键词
            try:
                results = self.search_news(keyword, limit=3, days_back=30)
                related_news.extend(results)
            except Exception as e:
                print(f"搜索相关新闻失败 ({keyword}): {e}")
        
        # 去重并过滤掉原新闻
        original_title = selected_news.get('title', '').lower()
        unique_related = []
        seen_titles = {original_title}
        
        for news in related_news:
            title_key = news.get('title', '').lower().strip()
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_related.append(news)
        
        return unique_related[:limit]
    
    def _extract_keywords(self, text: str) -> List[str]:
        """从文本中提取关键词"""
        # 简单的关键词提取（实际应用中可以使用更复杂的NLP方法）
        # 移除常见停用词
        stop_words = {'的', '了', '在', '是', '有', '和', '与', '或', '但', '与其', '关于', '对于', '由于', '因为', '所以', '因此', '然而', '虽然', '尽管', '而且', '并且', '同时', '另外', '此外', '最新', '报道', '消息', '新闻', '发展', '分析', '观点', '专家', '市场', '技术', '政策', '国际', '全球'}
        
        # 使用正则表达式提取中文词汇
        chinese_pattern = r'[\u4e00-\u9fff]+'
        words = re.findall(chinese_pattern, text)
        
        # 过滤停用词和短词
        keywords = [word for word in words if len(word) >= 2 and word not in stop_words]
        
        # 按长度排序，优先选择较长的词汇
        keywords.sort(key=len, reverse=True)
        
        return keywords[:5]  # 返回前5个关键词
    
    def get_news_summary(self, news_list: List[Dict]) -> Dict:
        """
        获取新闻摘要统计
        
        Args:
            news_list: 新闻列表
            
        Returns:
            包含统计信息的字典
        """
        if not news_list:
            return {"total": 0, "categories": {}, "sources": {}, "latest_time": None}
        
        categories = {}
        sources = {}
        latest_time = None
        
        for news in news_list:
            # 统计分类
            category = news.get('category', '未分类')
            categories[category] = categories.get(category, 0) + 1
            
            # 统计来源
            source = news.get('source', '未知来源')
            sources[source] = sources.get(source, 0) + 1
            
            # 找到最新时间
            published_at = news.get('published_at')
            if published_at:
                if latest_time is None or published_at > latest_time:
                    latest_time = published_at
        
        return {
            "total": len(news_list),
            "categories": categories,
            "sources": sources,
            "latest_time": latest_time
        }


def main():
    """测试函数"""
    agent = NewsAgent()
    
    # 测试搜索功能
    print("=== 测试新闻搜索 ===")
    query = "人工智能"
    news_results = agent.search_news(query, limit=5)
    
    print(f"搜索关键词: {query}")
    print(f"找到 {len(news_results)} 条相关新闻:\n")
    
    for i, news in enumerate(news_results, 1):
        print(f"{i}. {news['title']}")
        print(f"   来源: {news['source']} | 分类: {news['category']}")
        print(f"   时间: {news['published_at']}")
        print(f"   摘要: {news['summary'][:100]}...")
        print(f"   链接: {news['url']}")
        print()
    
    # 测试相关新闻搜索
    if news_results:
        print("=== 测试相关新闻搜索 ===")
        selected_news = news_results[0]
        related_news = agent.search_related_news(selected_news, limit=3)
        
        print(f"选择的新闻: {selected_news['title']}")
        print(f"找到 {len(related_news)} 条相关新闻:\n")
        
        for i, news in enumerate(related_news, 1):
            print(f"{i}. {news['title']}")
            print(f"   来源: {news['source']} | 分类: {news['category']}")
            print(f"   摘要: {news['summary'][:80]}...")
            print()
    
    # 测试新闻摘要
    print("=== 新闻摘要统计 ===")
    summary = agent.get_news_summary(news_results)
    print(f"总计: {summary['total']} 条新闻")
    print(f"分类分布: {summary['categories']}")
    print(f"来源分布: {summary['sources']}")
    print(f"最新时间: {summary['latest_time']}")


if __name__ == "__main__":
    main()