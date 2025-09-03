#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
地理问答系统Web界面
基于Streamlit构建
"""

import streamlit as st
import json
import pandas as pd
from qa_model import GeographyQA
import os
import time

# 页面配置
st.set_page_config(
    page_title="地理问答系统",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    .question-box {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 1rem 0;
    }
    .answer-box {
        background-color: #e8f5e8;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #28a745;
        margin: 1rem 0;
    }
    .confidence-badge {
        background-color: #ffc107;
        color: #212529;
        padding: 0.25rem 0.5rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .category-chip {
        background-color: #17a2b8;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        margin: 0.2rem;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_qa_system():
    """加载问答系统（缓存）"""
    try:
        if os.path.exists("./models"):
            return GeographyQA("./models")
        else:
            st.warning("未找到训练好的模型，将使用知识库匹配模式")
            return GeographyQA()
    except Exception as e:
        st.error(f"加载模型失败: {e}")
        return None

def main():
    """主函数"""
    # 标题
    st.markdown('<h1 class="main-header">🌍 地理问答系统</h1>', unsafe_allow_html=True)
    
    # 侧边栏
    with st.sidebar:
        st.markdown("### 📚 系统信息")
        st.info("这是一个基于AI的地理问答系统，可以回答关于中国和世界地理的问题。")
        
        st.markdown("### 🎯 功能特性")
        st.markdown("- 🤖 AI智能问答")
        st.markdown("- 📖 知识库管理")
        st.markdown("- 📊 分类浏览")
        st.markdown("- 🔍 问题搜索")
        
        st.markdown("### 📈 系统状态")
        if os.path.exists("./models"):
            st.success("✅ 模型已加载")
        else:
            st.warning("⚠️ 模型未训练")
        
        # 知识库统计
        try:
            with open("data/geography_qa_dataset.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                st.metric("知识库条目", len(data))
                
                # 分类统计
                categories = {}
                for item in data:
                    cat = item.get('category', '其他')
                    categories[cat] = categories.get(cat, 0) + 1
                
                st.markdown("### 📂 分类统计")
                for cat, count in categories.items():
                    st.markdown(f"- {cat}: {count}条")
        except:
            st.warning("无法加载知识库统计")
    
    # 主界面
    tab1, tab2, tab3, tab4 = st.tabs(["🤖 智能问答", "📚 知识库", "🔍 问题搜索", "⚙️ 系统管理"])
    
    with tab1:
        st.markdown('<h2 class="sub-header">智能问答</h2>', unsafe_allow_html=True)
        
        # 问答界面
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # 问题输入
            question = st.text_input(
                "请输入您的地理问题：",
                placeholder="例如：中国的首都是哪个城市？",
                key="question_input"
            )
            
            if st.button("🚀 提交问题", type="primary", use_container_width=True):
                if question.strip():
                    with st.spinner("正在思考中..."):
                        # 加载问答系统
                        qa_system = load_qa_system()
                        
                        if qa_system:
                            try:
                                # 获取答案
                                result = qa_system.answer_question(question)
                                
                                # 显示答案
                                st.markdown('<div class="answer-box">', unsafe_allow_html=True)
                                st.markdown(f"**问题：** {result['question']}")
                                st.markdown(f"**答案：** {result['answer']}")
                                
                                # 置信度
                                confidence = result.get('confidence', 0)
                                if confidence > 0:
                                    st.markdown(f"**置信度：** <span class='confidence-badge'>{confidence:.2f}</span>", unsafe_allow_html=True)
                                
                                st.markdown(f"**来源：** {result.get('source', '未知')}")
                                st.markdown('</div>', unsafe_allow_html=True)
                                
                                # 保存到会话状态
                                if 'chat_history' not in st.session_state:
                                    st.session_state.chat_history = []
                                
                                st.session_state.chat_history.append({
                                    'question': question,
                                    'answer': result['answer'],
                                    'timestamp': time.strftime("%H:%M:%S")
                                })
                                
                            except Exception as e:
                                st.error(f"回答问题失败: {e}")
                        else:
                            st.error("问答系统未正确加载")
                else:
                    st.warning("请输入问题")
        
        with col2:
            st.markdown("### 💡 问题示例")
            examples = [
                "中国的首都是哪个城市？",
                "长江有多长？",
                "珠穆朗玛峰在哪里？",
                "撒哈拉沙漠位于哪个大洲？",
                "黄河发源于哪里？"
            ]
            
            for example in examples:
                if st.button(example, key=f"example_{example}"):
                    st.session_state.question_input = example
                    st.rerun()
        
        # 聊天历史
        if 'chat_history' in st.session_state and st.session_state.chat_history:
            st.markdown("### 💬 对话历史")
            for i, chat in enumerate(reversed(st.session_state.chat_history[-5:])):  # 显示最近5条
                with st.expander(f"Q: {chat['question'][:30]}... ({chat['timestamp']})"):
                    st.markdown(f"**问题：** {chat['question']}")
                    st.markdown(f"**答案：** {chat['answer']}")
    
    with tab2:
        st.markdown('<h2 class="sub-header">知识库管理</h2>', unsafe_allow_html=True)
        
        try:
            with open("data/geography_qa_dataset.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # 分类筛选
            categories = list(set([item.get('category', '其他') for item in data]))
            selected_category = st.selectbox("选择分类：", ['全部'] + categories)
            
            # 难度筛选
            difficulties = list(set([item.get('difficulty', '未知') for item in data]))
            selected_difficulty = st.selectbox("选择难度：", ['全部'] + difficulties)
            
            # 筛选数据
            filtered_data = data
            if selected_category != '全部':
                filtered_data = [item for item in filtered_data if item.get('category') == selected_category]
            if selected_difficulty != '全部':
                filtered_data = [item for item in filtered_data if item.get('difficulty') == selected_difficulty]
            
            # 显示数据
            if filtered_data:
                df = pd.DataFrame(filtered_data)
                st.dataframe(df, use_container_width=True)
                
                # 统计信息
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("总条目数", len(filtered_data))
                with col2:
                    st.metric("分类数", len(set([item.get('category') for item in filtered_data])))
                with col3:
                    st.metric("难度等级", len(set([item.get('difficulty') for item in filtered_data])))
            else:
                st.info("没有找到符合条件的数据")
                
        except Exception as e:
            st.error(f"加载知识库失败: {e}")
    
    with tab3:
        st.markdown('<h2 class="sub-header">问题搜索</h2>', unsafe_allow_html=True)
        
        search_query = st.text_input("搜索关键词：", placeholder="输入关键词搜索相关问题")
        
        if search_query:
            try:
                with open("data/geography_qa_dataset.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # 搜索匹配
                search_results = []
                for item in data:
                    if (search_query.lower() in item['question'].lower() or 
                        search_query.lower() in item['answer'].lower() or
                        search_query.lower() in item.get('category', '').lower()):
                        search_results.append(item)
                
                if search_results:
                    st.success(f"找到 {len(search_results)} 个相关结果")
                    
                    for i, result in enumerate(search_results):
                        with st.expander(f"{i+1}. {result['question']}"):
                            st.markdown(f"**问题：** {result['question']}")
                            st.markdown(f"**答案：** {result['answer']}")
                            st.markdown(f"**分类：** <span class='category-chip'>{result.get('category', '其他')}</span>", unsafe_allow_html=True)
                            st.markdown(f"**难度：** {result.get('difficulty', '未知')}")
                else:
                    st.info("没有找到相关结果")
                    
            except Exception as e:
                st.error(f"搜索失败: {e}")
    
    with tab4:
        st.markdown('<h2 class="sub-header">系统管理</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 系统信息")
            st.info(f"Python版本: {st.get_option('server.enableCORS')}")
            st.info(f"Streamlit版本: {st.__version__}")
            
            # 模型信息
            if os.path.exists("./models"):
                st.success("✅ 模型文件存在")
                model_files = os.listdir("./models")
                st.markdown("**模型文件：**")
                for file in model_files[:5]:  # 显示前5个文件
                    st.markdown(f"- {file}")
                if len(model_files) > 5:
                    st.markdown(f"- ... 还有 {len(model_files) - 5} 个文件")
            else:
                st.warning("⚠️ 模型文件不存在")
        
        with col2:
            st.markdown("### 🔧 系统操作")
            
            if st.button("🔄 重新加载模型", type="secondary"):
                st.cache_resource.clear()
                st.success("缓存已清除，请刷新页面")
            
            if st.button("🗑️ 清除聊天历史", type="secondary"):
                if 'chat_history' in st.session_state:
                    del st.session_state.chat_history
                st.success("聊天历史已清除")
            
            # 添加新知识
            st.markdown("### ➕ 添加新知识")
            with st.form("add_knowledge"):
                new_question = st.text_input("问题：")
                new_answer = st.text_area("答案：")
                new_category = st.selectbox("分类：", ["中国地理", "世界地理", "其他"])
                new_difficulty = st.selectbox("难度：", ["简单", "中等", "困难"])
                
                if st.form_submit_button("添加知识"):
                    if new_question and new_answer:
                        try:
                            qa_system = load_qa_system()
                            if qa_system:
                                qa_system.add_knowledge(new_question, new_answer, new_category, new_difficulty)
                                st.success("知识添加成功！")
                                st.rerun()
                            else:
                                st.error("问答系统未加载")
                        except Exception as e:
                            st.error(f"添加失败: {e}")
                    else:
                        st.warning("请填写问题和答案")

if __name__ == "__main__":
    main()