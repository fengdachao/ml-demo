// 地理问答系统前端JavaScript

// 全局变量
let isAsking = false;

// DOM加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    // 绑定事件
    bindEvents();
    
    // 获取并显示统计信息
    loadStats();
});

// 绑定事件
function bindEvents() {
    // 统计按钮点击事件
    document.getElementById('statsBtn').addEventListener('click', showStats);
    
    // 输入框获得焦点时清除错误
    document.getElementById('questionInput').addEventListener('focus', clearError);
}

// 处理键盘按键
function handleKeyPress(event) {
    if (event.key === 'Enter' && !isAsking) {
        askQuestion();
    }
}

// 设置示例问题
function setQuestion(question) {
    document.getElementById('questionInput').value = question;
    document.getElementById('questionInput').focus();
}

// 提问
async function askQuestion() {
    if (isAsking) return;
    
    const questionInput = document.getElementById('questionInput');
    const question = questionInput.value.trim();
    
    if (!question) {
        showError('请输入问题');
        questionInput.focus();
        return;
    }
    
    // 开始提问
    startAsking();
    
    try {
        const response = await fetch('/api/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question: question })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAnswer(data.question, data.answer);
        } else {
            showError(data.error || '处理问题时出错');
        }
        
    } catch (error) {
        console.error('Error:', error);
        showError('网络错误，请稍后重试');
    } finally {
        stopAsking();
    }
}

// 开始提问状态
function startAsking() {
    isAsking = true;
    
    // 隐藏之前的结果
    hideAnswer();
    hideError();
    
    // 显示加载指示器
    showLoading();
    
    // 禁用按钮
    const askButton = document.getElementById('askButton');
    askButton.disabled = true;
    askButton.innerHTML = '<i class="bi bi-hourglass-split me-1"></i>思考中...';
}

// 停止提问状态
function stopAsking() {
    isAsking = false;
    
    // 隐藏加载指示器
    hideLoading();
    
    // 恢复按钮
    const askButton = document.getElementById('askButton');
    askButton.disabled = false;
    askButton.innerHTML = '<i class="bi bi-search me-1"></i>提问';
}

// 显示加载指示器
function showLoading() {
    document.getElementById('loadingIndicator').style.display = 'block';
}

// 隐藏加载指示器
function hideLoading() {
    document.getElementById('loadingIndicator').style.display = 'none';
}

// 显示答案
function showAnswer(question, answer) {
    document.getElementById('displayQuestion').textContent = question;
    document.getElementById('displayAnswer').textContent = answer;
    document.getElementById('answerArea').style.display = 'block';
    
    // 滚动到答案区域
    document.getElementById('answerArea').scrollIntoView({ 
        behavior: 'smooth',
        block: 'center'
    });
}

// 隐藏答案
function hideAnswer() {
    document.getElementById('answerArea').style.display = 'none';
}

// 显示错误
function showError(message) {
    document.getElementById('errorMessage').textContent = message;
    document.getElementById('errorArea').style.display = 'block';
    
    // 3秒后自动隐藏错误
    setTimeout(hideError, 3000);
}

// 隐藏错误
function hideError() {
    document.getElementById('errorArea').style.display = 'none';
}

// 清除错误
function clearError() {
    hideError();
}

// 显示统计信息
async function showStats() {
    const modal = new bootstrap.Modal(document.getElementById('statsModal'));
    modal.show();
    
    // 重新加载统计信息
    await loadStats();
}

// 加载统计信息
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        if (data.success) {
            const statsContent = document.getElementById('statsContent');
            statsContent.innerHTML = `
                <div class="row text-center">
                    <div class="col-md-6 mb-3">
                        <div class="card bg-primary text-white">
                            <div class="card-body">
                                <i class="bi bi-question-circle-fill fs-1 mb-2"></i>
                                <h3>${data.stats.total_qa_pairs}</h3>
                                <p class="mb-0">问答对总数</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6 mb-3">
                        <div class="card bg-success text-white">
                            <div class="card-body">
                                <i class="bi bi-tags-fill fs-1 mb-2"></i>
                                <h3>${data.stats.categories.length}</h3>
                                <p class="mb-0">知识类别</p>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="mt-3">
                    <h6>支持的知识类别：</h6>
                    <div class="d-flex flex-wrap gap-2">
                        ${data.stats.categories.map(category => 
                            `<span class="badge bg-secondary">${category}</span>`
                        ).join('')}
                    </div>
                </div>
                <div class="mt-3">
                    <small class="text-muted">
                        系统基于人工智能技术，持续学习和优化中...
                    </small>
                </div>
            `;
        } else {
            document.getElementById('statsContent').innerHTML = `
                <div class="alert alert-warning">
                    <i class="bi bi-exclamation-triangle me-2"></i>
                    无法加载统计信息
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading stats:', error);
        document.getElementById('statsContent').innerHTML = `
            <div class="alert alert-danger">
                <i class="bi bi-exclamation-triangle me-2"></i>
                加载统计信息时出错
            </div>
        `;
    }
}

// 页面可见性变化时的处理
document.addEventListener('visibilitychange', function() {
    if (document.visibilityState === 'visible') {
        // 页面重新可见时，刷新统计信息
        loadStats();
    }
});

// 错误处理
window.addEventListener('error', function(event) {
    console.error('Global error:', event.error);
});

// 未处理的Promise拒绝
window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
});