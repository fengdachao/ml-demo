"""
地理问答系统Web应用
"""
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sys
import os

# 添加项目根目录到Python路径
sys.path.append('/workspace')

from models.simple_qa import SimpleGeographyQA

app = Flask(__name__, 
           template_folder='/workspace/templates',
           static_folder='/workspace/static')
CORS(app)

# 初始化问答系统
qa_system = SimpleGeographyQA()

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/ask', methods=['POST'])
def ask_question():
    """处理问题请求"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({
                'success': False,
                'error': '请输入问题'
            })
        
        # 获取答案
        answer = qa_system.answer(question)
        
        return jsonify({
            'success': True,
            'question': question,
            'answer': answer
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'处理问题时出错: {str(e)}'
        })

@app.route('/api/health')
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'message': '地理问答系统运行正常'
    })

@app.route('/api/stats')
def get_stats():
    """获取系统统计信息"""
    try:
        qa_count = len(qa_system.qa_data)
        return jsonify({
            'success': True,
            'stats': {
                'total_qa_pairs': qa_count,
                'categories': ['省会城市', '河流', '山脉', '综合']
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    # 确保数据文件存在
    if not os.path.exists('/workspace/data/geography_qa.json'):
        print("正在生成地理问答数据集...")
        from data.geography_qa_dataset import GeographyQADataset
        dataset = GeographyQADataset()
        dataset.save_dataset('/workspace/data/geography_qa.json')
        print("数据集生成完成！")
    
    app.run(host='0.0.0.0', port=5000, debug=True)