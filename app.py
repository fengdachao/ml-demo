#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能新闻搜索智能体 - Web应用
"""

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
import json
from typing import Optional
from news_agent import NewsAgent
import os

app = FastAPI(title="智能新闻搜索智能体", description="根据用户输入搜索相关新闻并提供深度分析")

# 设置模板和静态文件
templates = Jinja2Templates(directory="templates")

# 如果static目录存在，则挂载静态文件
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# 创建新闻智能体实例
news_agent = NewsAgent()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """主页"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/search", response_class=JSONResponse)
async def search_news(query: str = Form(...), limit: int = Form(10)):
    """搜索新闻API"""
    try:
        if not query.strip():
            raise HTTPException(status_code=400, detail="搜索关键词不能为空")
        
        # 搜索新闻
        news_results = news_agent.search_news(query.strip(), limit=limit)
        
        # 获取摘要统计
        summary = news_agent.get_news_summary(news_results)
        
        return {
            "success": True,
            "query": query,
            "results": news_results,
            "summary": summary
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/related", response_class=JSONResponse)
async def search_related_news(
    title: str = Form(...), 
    summary: str = Form(""), 
    url: str = Form(""),
    limit: int = Form(8)
):
    """搜索相关新闻API"""
    try:
        if not title.strip():
            raise HTTPException(status_code=400, detail="新闻标题不能为空")
        
        # 构建选中的新闻对象
        selected_news = {
            "title": title.strip(),
            "summary": summary.strip(),
            "url": url.strip()
        }
        
        # 搜索相关新闻
        related_results = news_agent.search_related_news(selected_news, limit=limit)
        
        # 获取摘要统计
        summary_stats = news_agent.get_news_summary(related_results)
        
        return {
            "success": True,
            "selected_news": selected_news,
            "results": related_results,
            "summary": summary_stats
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "智能新闻搜索智能体"}

if __name__ == "__main__":
    # 确保模板目录存在
    os.makedirs("templates", exist_ok=True)
    os.makedirs("static", exist_ok=True)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)