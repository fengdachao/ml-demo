#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能新闻搜索智能体 - 功能演示脚本
"""

import requests
import json
import time
from news_agent import NewsAgent

def demo_cli():
    """命令行演示"""
    print("🤖 智能新闻搜索智能体 - 功能演示")
    print("=" * 50)
    
    agent = NewsAgent()
    
    # 演示搜索功能
    test_queries = ["人工智能", "新能源", "区块链", "5G技术"]
    
    for query in test_queries:
        print(f"\n🔍 搜索关键词: {query}")
        print("-" * 30)
        
        try:
            # 搜索新闻
            results = agent.search_news(query, limit=3)
            
            if results:
                print(f"✅ 找到 {len(results)} 条相关新闻:")
                for i, news in enumerate(results, 1):
                    print(f"\n{i}. {news['title']}")
                    print(f"   📰 来源: {news['source']}")
                    print(f"   📅 时间: {news['published_at']}")
                    print(f"   🏷️  分类: {news['category']}")
                    print(f"   📝 摘要: {news['summary'][:60]}...")
                
                # 演示相关新闻搜索
                if len(results) > 0:
                    print(f"\n🔗 搜索与第1条新闻相关的内容...")
                    related = agent.search_related_news(results[0], limit=2)
                    
                    if related:
                        print(f"✅ 找到 {len(related)} 条相关新闻:")
                        for i, news in enumerate(related, 1):
                            print(f"  {i}. {news['title'][:40]}...")
                    else:
                        print("❌ 未找到相关新闻")
            else:
                print("❌ 未找到相关新闻")
                
        except Exception as e:
            print(f"❌ 搜索失败: {e}")
        
        time.sleep(1)  # 避免过快请求

def demo_web_api():
    """Web API演示"""
    print("\n🌐 Web API功能演示")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # 检查健康状态
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Web服务运行正常")
            print(f"   服务状态: {response.json()}")
        else:
            print("❌ Web服务状态异常")
            return
    except requests.exceptions.RequestException:
        print("❌ 无法连接到Web服务")
        print("   请先运行: ./start.sh 或 python3 app.py")
        return
    
    # 测试搜索API
    print(f"\n🔍 测试搜索API...")
    try:
        search_data = {
            'query': '人工智能',
            'limit': '3'
        }
        
        response = requests.post(f"{base_url}/search", data=search_data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print("✅ 搜索API工作正常")
                print(f"   查询: {result['query']}")
                print(f"   结果数量: {result['summary']['total']}")
                print(f"   分类: {list(result['summary']['categories'].keys())}")
            else:
                print(f"❌ 搜索失败: {result.get('error', '未知错误')}")
        else:
            print(f"❌ API调用失败: HTTP {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")

def main():
    """主函数"""
    print("🎯 选择演示模式:")
    print("1. 命令行演示 (离线)")
    print("2. Web API演示 (需要先启动服务)")
    print("3. 完整演示")
    
    choice = input("\n请输入选择 (1/2/3): ").strip()
    
    if choice == "1":
        demo_cli()
    elif choice == "2":
        demo_web_api()
    elif choice == "3":
        demo_cli()
        demo_web_api()
    else:
        print("❌ 无效选择")
        
    print("\n🎉 演示完成!")
    print("💡 要使用完整功能，请运行:")
    print("   ./start.sh")
    print("   然后在浏览器中访问: http://localhost:8000")

if __name__ == "__main__":
    main()