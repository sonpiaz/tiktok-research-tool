from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Tạo thư mục để lưu dữ liệu
if not os.path.exists('data'):
    os.makedirs('data')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/scrape', methods=['POST'])
def scrape():
    try:
        # Nhận các tham số từ request
        data = request.json
        username = data.get('username', '')
        hashtag = data.get('hashtag', '')
        duration = data.get('duration', 60)
        max_videos = data.get('maxVideos', 10)
        scroll_speed = data.get('scrollSpeed', 'medium')
        save_to_file = data.get('saveToFile', False)
        
        # Giả lập quá trình thu thập dữ liệu
        # Trong một ứng dụng thực, đây là nơi bạn sẽ sử dụng TikTokScraper
        
        # Tạo dữ liệu mẫu để trả về
        results = []
        for i in range(min(5, max_videos)):
            results.append({
                'id': f'video_{i}',
                'author': f'user_{username if username else "sample"}',
                'desc': f'Video description #{hashtag if hashtag else "sample"}',
                'likes': 1000 + i * 100,
                'comments': 50 + i * 10,
                'shares': 20 + i * 5,
                'collected_at': datetime.now().isoformat()
            })
        
        # Lưu kết quả vào file nếu được yêu cầu
        if save_to_file:
            filename = f"data/tiktok_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
                
            return jsonify({
                'success': True,
                'message': 'Data collected and saved successfully',
                'results': results,
                'saved_file': filename
            })
        
        return jsonify({
            'success': True,
            'message': 'Data collected successfully',
            'results': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@app.route('/api/files', methods=['GET'])
def get_files():
    try:
        files = []
        for filename in os.listdir('data'):
            if filename.endswith('.json'):
                file_path = os.path.join('data', filename)
                file_size = os.path.getsize(file_path)
                files.append({
                    'name': filename,
                    'size': file_size,
                    'date': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                })
        
        return jsonify({
            'success': True,
            'files': files
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@app.route('/api/file/<filename>', methods=['GET'])
def get_file(filename):
    try:
        file_path = os.path.join('data', filename)
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        return jsonify({
            'success': True,
            'data': data
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
