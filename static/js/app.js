// 智能新闻搜索智能体 - JavaScript 功能

class NewsSearchApp {
    constructor() {
        this.currentNews = null;
        this.searchHistory = this.loadSearchHistory();
        this.init();
    }

    init() {
        this.bindEvents();
        this.displaySearchHistory();
    }

    bindEvents() {
        // 搜索表单提交
        document.getElementById('searchForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.performSearch();
        });

        // 清除结果按钮
        document.getElementById('clearResults').addEventListener('click', () => {
            this.clearResults();
        });

        // 清除相关新闻按钮
        document.getElementById('clearRelated').addEventListener('click', () => {
            this.clearRelatedNews();
        });

        // 查找相关新闻按钮（模态框中）
        document.getElementById('findRelatedBtn').addEventListener('click', () => {
            if (this.currentNews) {
                this.searchRelatedNews(this.currentNews);
                bootstrap.Modal.getInstance(document.getElementById('newsModal')).hide();
            }
        });

        // 回车键搜索
        document.getElementById('searchQuery').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.performSearch();
            }
        });
    }

    async performSearch() {
        const query = document.getElementById('searchQuery').value.trim();
        const limit = document.getElementById('limitSelect').value;

        if (!query) {
            this.showAlert('请输入搜索关键词', 'danger');
            return;
        }

        // 显示加载动画
        this.showLoading(true);
        this.clearResults();

        try {
            const formData = new FormData();
            formData.append('query', query);
            formData.append('limit', limit);

            const response = await fetch('/search', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                this.displaySearchResults(data.results, data.summary, query);
                this.addToSearchHistory(query);
            } else {
                this.showAlert(`搜索失败: ${data.error}`, 'danger');
            }
        } catch (error) {
            console.error('搜索错误:', error);
            this.showAlert('搜索请求失败，请稍后重试', 'danger');
        } finally {
            this.showLoading(false);
        }
    }

    async searchRelatedNews(newsItem) {
        // 显示加载动画
        this.showLoading(true);
        this.clearRelatedNews();

        try {
            const formData = new FormData();
            formData.append('title', newsItem.title);
            formData.append('summary', newsItem.summary || '');
            formData.append('url', newsItem.url || '');
            formData.append('limit', '8');

            const response = await fetch('/related', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                this.displayRelatedResults(data.results, newsItem);
            } else {
                this.showAlert(`搜索相关新闻失败: ${data.error}`, 'danger');
            }
        } catch (error) {
            console.error('搜索相关新闻错误:', error);
            this.showAlert('搜索相关新闻请求失败，请稍后重试', 'danger');
        } finally {
            this.showLoading(false);
        }
    }

    displaySearchResults(results, summary, query) {
        // 显示摘要统计
        this.displaySummary(summary);

        // 显示搜索结果
        const resultsContainer = document.getElementById('searchResults');
        const newsList = document.getElementById('newsList');

        if (results.length === 0) {
            newsList.innerHTML = `
                <div class="col-12 text-center py-5">
                    <i class="bi bi-search text-muted" style="font-size: 4rem;"></i>
                    <h5 class="text-muted mt-3">未找到相关新闻</h5>
                    <p class="text-muted">请尝试其他关键词或检查拼写</p>
                </div>
            `;
        } else {
            newsList.innerHTML = results.map((news, index) => this.createNewsCard(news, index)).join('');
            
            // 添加新闻卡片点击事件
            this.bindNewsCardEvents();
        }

        resultsContainer.classList.remove('d-none');
        resultsContainer.scrollIntoView({ behavior: 'smooth' });
    }

    displayRelatedResults(results, selectedNews) {
        const relatedContainer = document.getElementById('relatedResults');
        const relatedList = document.getElementById('relatedNewsList');
        const selectedTitle = document.getElementById('selectedNewsTitle');

        // 设置选中的新闻标题
        selectedTitle.textContent = this.truncateText(selectedNews.title, 30);

        if (results.length === 0) {
            relatedList.innerHTML = `
                <div class="col-12 text-center py-4">
                    <i class="bi bi-link-45deg text-muted" style="font-size: 3rem;"></i>
                    <h6 class="text-muted mt-2">暂无相关新闻</h6>
                    <p class="text-muted small">尝试搜索其他关键词</p>
                </div>
            `;
        } else {
            relatedList.innerHTML = results.map((news, index) => this.createNewsCard(news, index, true)).join('');
            
            // 添加相关新闻卡片点击事件
            this.bindNewsCardEvents();
        }

        relatedContainer.classList.remove('d-none');
        relatedContainer.scrollIntoView({ behavior: 'smooth' });
    }

    displaySummary(summary) {
        document.getElementById('totalCount').textContent = summary.total;
        document.getElementById('categoryCount').textContent = Object.keys(summary.categories).length;
        document.getElementById('sourceCount').textContent = Object.keys(summary.sources).length;
        
        const latestTime = summary.latest_time ? 
            this.formatDateTime(summary.latest_time) : '-';
        document.getElementById('latestTime').textContent = latestTime;

        document.getElementById('resultSummary').classList.remove('d-none');
    }

    createNewsCard(news, index, isRelated = false) {
        const categoryColors = {
            '综合新闻': 'primary',
            '财经': 'success',
            '科技': 'info',
            '政策': 'warning',
            '国际': 'danger',
            '默认': 'secondary'
        };

        const categoryColor = categoryColors[news.category] || categoryColors['默认'];
        const cardId = isRelated ? `related-news-${index}` : `news-${index}`;

        return `
            <div class="col-md-6 col-lg-4 mb-4">
                <div class="news-card fade-in-up" data-news='${JSON.stringify(news)}' data-card-id="${cardId}">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <span class="badge bg-${categoryColor} badge-category">${news.category}</span>
                            <small class="text-muted">${this.formatDateTime(news.published_at)}</small>
                        </div>
                        
                        <h6 class="news-title">${this.escapeHtml(news.title)}</h6>
                        
                        <p class="news-summary">${this.escapeHtml(news.summary)}</p>
                        
                        <div class="news-meta">
                            <div class="d-flex justify-content-between align-items-center">
                                <small class="text-muted">
                                    <i class="bi bi-building me-1"></i>
                                    ${this.escapeHtml(news.source)}
                                </small>
                                <div class="btn-group" role="group">
                                    <button type="button" class="btn btn-outline-primary btn-sm view-details-btn">
                                        <i class="bi bi-eye me-1"></i>详情
                                    </button>
                                    <button type="button" class="btn btn-outline-success btn-sm find-related-btn">
                                        <i class="bi bi-search me-1"></i>相关
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    bindNewsCardEvents() {
        // 查看详情按钮
        document.querySelectorAll('.view-details-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const card = e.target.closest('.news-card');
                const newsData = JSON.parse(card.getAttribute('data-news'));
                this.showNewsDetails(newsData);
            });
        });

        // 查找相关新闻按钮
        document.querySelectorAll('.find-related-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const card = e.target.closest('.news-card');
                const newsData = JSON.parse(card.getAttribute('data-news'));
                this.searchRelatedNews(newsData);
            });
        });

        // 新闻卡片点击事件
        document.querySelectorAll('.news-card').forEach(card => {
            card.addEventListener('click', () => {
                const newsData = JSON.parse(card.getAttribute('data-news'));
                this.showNewsDetails(newsData);
            });
        });
    }

    showNewsDetails(news) {
        this.currentNews = news;
        
        const modalTitle = document.getElementById('newsModalTitle');
        const modalContent = document.getElementById('newsModalContent');

        modalTitle.textContent = news.title;
        
        modalContent.innerHTML = `
            <div class="row">
                <div class="col-md-12">
                    <div class="mb-3">
                        <span class="badge bg-primary me-2">${news.category}</span>
                        <span class="badge bg-secondary">${news.source}</span>
                        <span class="text-muted ms-2">
                            <i class="bi bi-clock me-1"></i>
                            ${this.formatDateTime(news.published_at)}
                        </span>
                    </div>
                    
                    <h5 class="mb-3">${this.escapeHtml(news.title)}</h5>
                    
                    <p class="lead text-muted mb-4">${this.escapeHtml(news.summary)}</p>
                    
                    <div class="border-top pt-3">
                        <p class="mb-2">
                            <strong>新闻链接：</strong>
                            <a href="${news.url}" target="_blank" class="news-link">
                                ${news.url}
                                <i class="bi bi-box-arrow-up-right ms-1"></i>
                            </a>
                        </p>
                    </div>
                </div>
            </div>
        `;

        const modal = new bootstrap.Modal(document.getElementById('newsModal'));
        modal.show();
    }

    showLoading(show) {
        const spinner = document.getElementById('loadingSpinner');
        if (show) {
            spinner.classList.remove('d-none');
        } else {
            spinner.classList.add('d-none');
        }
    }

    clearResults() {
        document.getElementById('searchResults').classList.add('d-none');
        document.getElementById('resultSummary').classList.add('d-none');
        document.getElementById('newsList').innerHTML = '';
    }

    clearRelatedNews() {
        document.getElementById('relatedResults').classList.add('d-none');
        document.getElementById('relatedNewsList').innerHTML = '';
    }

    showAlert(message, type = 'info') {
        const alertContainer = document.createElement('div');
        alertContainer.className = `alert alert-${type} alert-dismissible fade show`;
        alertContainer.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        // 插入到搜索框下方
        const searchForm = document.getElementById('searchForm');
        searchForm.parentNode.insertBefore(alertContainer, searchForm.nextSibling);

        // 3秒后自动消失
        setTimeout(() => {
            if (alertContainer.parentNode) {
                alertContainer.remove();
            }
        }, 3000);
    }

    // 搜索历史相关功能
    addToSearchHistory(query) {
        if (!this.searchHistory.includes(query)) {
            this.searchHistory.unshift(query);
            this.searchHistory = this.searchHistory.slice(0, 10); // 只保留最近10个
            this.saveSearchHistory();
            this.displaySearchHistory();
        }
    }

    loadSearchHistory() {
        try {
            const history = localStorage.getItem('newsSearchHistory');
            return history ? JSON.parse(history) : [];
        } catch {
            return [];
        }
    }

    saveSearchHistory() {
        try {
            localStorage.setItem('newsSearchHistory', JSON.stringify(this.searchHistory));
        } catch (error) {
            console.warn('无法保存搜索历史:', error);
        }
    }

    displaySearchHistory() {
        if (this.searchHistory.length === 0) return;

        const searchInput = document.getElementById('searchQuery');
        let historyContainer = document.getElementById('searchHistoryContainer');
        
        if (!historyContainer) {
            historyContainer = document.createElement('div');
            historyContainer.id = 'searchHistoryContainer';
            historyContainer.className = 'search-history mt-2';
            searchInput.parentNode.appendChild(historyContainer);
        }

        historyContainer.innerHTML = `
            <small class="text-muted me-2">搜索历史：</small>
            ${this.searchHistory.map(query => 
                `<span class="badge bg-light text-dark history-item" data-query="${this.escapeHtml(query)}">${this.escapeHtml(query)}</span>`
            ).join('')}
        `;

        // 添加历史项点击事件
        historyContainer.querySelectorAll('.history-item').forEach(item => {
            item.addEventListener('click', () => {
                searchInput.value = item.getAttribute('data-query');
                this.performSearch();
            });
        });
    }

    // 工具函数
    formatDateTime(dateString) {
        if (!dateString) return '-';
        try {
            const date = new Date(dateString);
            const now = new Date();
            const diffMs = now - date;
            const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
            const diffDays = Math.floor(diffHours / 24);

            if (diffDays > 0) {
                return `${diffDays}天前`;
            } else if (diffHours > 0) {
                return `${diffHours}小时前`;
            } else {
                return '刚刚';
            }
        } catch {
            return dateString;
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    truncateText(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }
}

// 应用初始化
document.addEventListener('DOMContentLoaded', () => {
    new NewsSearchApp();
    
    // 添加一些 UI 增强效果
    setTimeout(() => {
        document.querySelectorAll('.card').forEach((card, index) => {
            card.style.animationDelay = `${index * 0.1}s`;
            card.classList.add('fade-in-up');
        });
    }, 100);
});