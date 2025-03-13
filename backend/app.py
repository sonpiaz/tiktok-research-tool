from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import time
import os
import json
from datetime import datetime
from pymongo import MongoClient
from models.data_model import TikTokAnalyzer
from scrapers.tiktok_scraper import TikTokScraper
import logging
import traceback
import glob
import csv

# Thiết lập logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Đường dẫn cho file logs và data
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Tạo thư mục nếu chưa tồn tại
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# Kết nối MongoDB
try:
    client = MongoClient('mongodb://localhost:27017/')
    db = client['tiktok_research']
    videos_collection = db['videos']
    print("Kết nối MongoDB thành công")
except Exception as e:
    print(f"Lỗi kết nối MongoDB: {str(e)}")
    videos_collection = None

# Khởi tạo analyzer
analyzer = TikTokAnalyzer(videos_collection)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "message": "TikTok Research Tool backend is running"})

@app.route('/api/scrape', methods=['POST'])
def start_scraping():
    data = request.json
    duration = data.get('duration', 60)  # Thời gian chạy mặc định 60 giây
    scroll_speed = data.get('scrollSpeed', 3)  # Tốc độ cuộn mặc định
    max_videos = data.get('maxVideos', None)  # Số lượng video tối đa cần thu thập
    use_proxy = data.get('useProxy', False)  # Có sử dụng proxy không
    save_to_file = data.get('saveToFile', False)  # Có lưu kết quả ra file không
    
    # Tạo filename dựa trên timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_filename = os.path.join(DATA_DIR, f"tiktok_data_{timestamp}.json")
    
    try:
        # Khởi tạo scraper với proxy nếu cần
        proxy_list = data.get('proxyList', [])
        scraper = TikTokScraper(use_proxy=use_proxy, proxy_list=proxy_list)
        
        # Setup trình duyệt
        setup_success = scraper.setup()
        if not setup_success:
            return jsonify({
                "status": "error",
                "message": "Không thể khởi tạo trình duyệt"
            }), 500
        
        # Thực hiện scraping
        results = scraper.scrape(
            duration=duration, 
            scroll_speed=scroll_speed,
            max_videos=max_videos
        )
        
        # Đóng trình duyệt
        scraper.teardown()
        
        # Lưu ra file nếu được yêu cầu
        if save_to_file and results:
            scraper.export_to_json(json_filename)
        
        # Lưu dữ liệu vào MongoDB nếu có kết nối
        saved_count = 0
        if videos_collection and results:
            for video in results:
                video['collected_at'] = datetime.now()
                result = videos_collection.update_one(
                    {'username': video['username'], 'description': video['description'][:100]},
                    {'$set': video},
                    upsert=True
                )
                if result.upserted_id or result.modified_count > 0:
                    saved_count += 1
        
        return jsonify({
            "status": "success",
            "message": f"Đã thu thập {len(results)} videos, lưu vào database {saved_count} videos",
            "data": results,
            "saved_to_file": json_filename if save_to_file and results else None
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/videos', methods=['GET'])
def get_videos():
    limit = int(request.args.get('limit', 100))
    
    if videos_collection:
        videos = list(videos_collection.find({}, {'_id': 0}).limit(limit))
        return jsonify({
            "status": "success",
            "count": len(videos),
            "data": videos
        })
    else:
        return jsonify({
            "status": "error",
            "message": "Database not connected"
        }), 500

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard_stats():
    """Lấy thông tin tổng quan cho dashboard"""
    try:
        stats = analyzer.get_dashboard_stats()
        return jsonify({
            "status": "success",
            "data": stats
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/viral-videos', methods=['GET'])
def get_viral_videos():
    """Lấy danh sách video viral"""
    limit = int(request.args.get('limit', 20))
    
    try:
        viral_df = analyzer.get_viral_videos()
        viral_videos = viral_df.head(limit).to_dict('records')
        
        return jsonify({
            "status": "success",
            "count": len(viral_videos),
            "data": viral_videos
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/trending-niches', methods=['GET'])
def get_trending_niches():
    """Lấy danh sách các niche đang trending"""
    try:
        trending_niches = analyzer.get_trending_niches()
        return jsonify({
            "status": "success",
            "data": trending_niches
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/trending-hashtags', methods=['GET'])
def get_trending_hashtags():
    """Lấy danh sách các hashtag đang trending"""
    try:
        trending_hashtags = analyzer.get_trending_hashtags()
        return jsonify({
            "status": "success",
            "data": trending_hashtags
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/optimal-duration', methods=['GET'])
def get_optimal_duration():
    """Lấy thông tin về thời lượng video tối ưu"""
    try:
        optimal_duration = analyzer.get_optimal_video_length()
        return jsonify({
            "status": "success",
            "data": optimal_duration
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/export-data', methods=['GET'])
def export_data():
    """Xuất dữ liệu dưới dạng JSON hoặc CSV"""
    format_type = request.args.get('format', 'json')
    limit = int(request.args.get('limit', 1000))
    
    if not videos_collection:
        return jsonify({
            "status": "error",
            "message": "Database not connected"
        }), 500
    
    try:
        videos = list(videos_collection.find({}, {'_id': 0}).limit(limit))
        
        if format_type == 'json':
            # Lưu ra file tạm thời
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(DATA_DIR, f"tiktok_export_{timestamp}.json")
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(videos, f, ensure_ascii=False, indent=4)
                
            return send_file(
                filename,
                mimetype='application/json',
                as_attachment=True,
                download_name=f"tiktok_export_{timestamp}.json"
            )
        elif format_type == 'csv':
            # Chuyển đổi sang CSV
            import pandas as pd
            import io
            
            df = pd.DataFrame(videos)
            csv_data = io.StringIO()
            df.to_csv(csv_data, index=False)
            
            return jsonify({
                "status": "success",
                "csv_data": csv_data.getvalue()
            })
        else:
            return jsonify({
                "status": "error",
                "message": f"Unsupported format: {format_type}"
            }), 400
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/files', methods=['GET'])
def get_saved_files():
    """Lấy danh sách các file đã lưu"""
    try:
        files = []
        for file in os.listdir(DATA_DIR):
            if file.endswith('.json'):
                file_path = os.path.join(DATA_DIR, file)
                files.append({
                    'filename': file,
                    'size': os.path.getsize(file_path),
                    'created_at': datetime.datetime.fromtimestamp(os.path.getctime(file_path)).isoformat()
                })
                
        # Sắp xếp theo thời gian tạo giảm dần (mới nhất lên đầu)
        files.sort(key=lambda x: x['created_at'], reverse=True)
        
        return jsonify({
            "status": "success",
            "files": files
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/files/download/<filename>', methods=['GET'])
def download_file(filename):
    """Tải xuống file đã lưu"""
    try:
        file_path = os.path.join(DATA_DIR, filename)
        if not os.path.exists(file_path):
            return jsonify({
                "status": "error",
                "message": "File not found"
            }), 404
            
        return send_file(
            file_path,
            mimetype='application/json',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/files/<filename>', methods=['DELETE'])
def delete_file(filename):
    """Xóa file đã lưu"""
    try:
        # Kiểm tra nếu file tồn tại
        file_path = os.path.join(DATA_DIR, filename)
        
        if not os.path.exists(file_path):
            return jsonify({
                'status': 'error',
                'message': 'File không tồn tại'
            }), 404
        
        # Xóa file
        os.remove(file_path)
        logger.info(f"Đã xóa file: {filename}")
        
        return jsonify({
            'status': 'success',
            'message': f'Đã xóa file {filename} thành công'
        })
    
    except Exception as e:
        logger.error(f"Lỗi khi xóa file {filename}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Lỗi: {str(e)}'
        }), 500

# API endpoint để xuất dữ liệu dưới dạng file
@app.route('/api/export', methods=['POST'])
def export_data():
    try:
        data = request.get_json()
        
        if not data or 'data' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Không có dữ liệu để xuất'
            }), 400
        
        export_format = data.get('format', 'json')  # Mặc định là json
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if export_format == 'json':
            # Xuất dữ liệu dưới dạng JSON
            filename = f'tiktok_export_{timestamp}.json'
            file_path = os.path.join(DATA_DIR, filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data['data'], f, ensure_ascii=False, indent=2, default=str)
        
        elif export_format == 'csv':
            # Xuất dữ liệu dưới dạng CSV
            filename = f'tiktok_export_{timestamp}.csv'
            file_path = os.path.join(DATA_DIR, filename)
            
            # Kiểm tra nếu có dữ liệu
            if len(data['data']) > 0:
                # Lấy header từ keys của object đầu tiên
                headers = data['data'][0].keys()
                
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=headers)
                    writer.writeheader()
                    
                    # Ghi dữ liệu
                    for row in data['data']:
                        # Xử lý các giá trị không phải chuỗi (như datetime, list, ...)
                        processed_row = {}
                        for key, value in row.items():
                            if isinstance(value, (list, dict)):
                                processed_row[key] = json.dumps(value, ensure_ascii=False)
                            else:
                                processed_row[key] = value
                        
                        writer.writerow(processed_row)
            else:
                # Tạo file CSV trống nếu không có dữ liệu
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    f.write('')
        
        else:
            return jsonify({
                'status': 'error',
                'message': f'Định dạng xuất {export_format} không được hỗ trợ'
            }), 400
        
        logger.info(f"Đã xuất dữ liệu thành công sang file {filename}")
        
        return jsonify({
            'status': 'success',
            'message': f'Đã xuất dữ liệu thành công',
            'filename': filename
        })
    
    except Exception as e:
        logger.error(f"Lỗi khi xuất dữ liệu: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'message': f'Lỗi: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 