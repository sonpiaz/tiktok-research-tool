import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pymongo import MongoClient
from collections import Counter
import re

class TikTokAnalyzer:
    def __init__(self, db_connection=None):
        """
        Khởi tạo TikTokAnalyzer
        
        Args:
            db_connection: Kết nối MongoDB hoặc None nếu không có kết nối
        """
        self.db = db_connection
        
    def load_data(self, data=None, limit=1000):
        """
        Tải dữ liệu từ cơ sở dữ liệu hoặc từ dữ liệu được truyền vào
        
        Args:
            data: Dữ liệu truyền vào (list of dict)
            limit: Số lượng bản ghi tối đa khi lấy từ database
            
        Returns:
            pandas.DataFrame: Dữ liệu dạng DataFrame
        """
        if data is not None:
            return pd.DataFrame(data)
            
        if self.db is not None:
            try:
                videos = list(self.db.find({}).limit(limit))
                # Chuyển _id ObjectId thành string để có thể serialize
                for video in videos:
                    if '_id' in video:
                        video['_id'] = str(video['_id'])
                return pd.DataFrame(videos)
            except Exception as e:
                print(f"Lỗi khi tải dữ liệu từ database: {str(e)}")
                
        return pd.DataFrame()
        
    def get_viral_videos(self, data=None, engagement_threshold=10000):
        """
        Lấy danh sách các video viral dựa trên ngưỡng tương tác
        
        Args:
            data: DataFrame hoặc None để tải từ database
            engagement_threshold: Ngưỡng tương tác để xác định video viral
            
        Returns:
            pandas.DataFrame: Danh sách video viral
        """
        df = data if data is not None else self.load_data()
        if df.empty:
            return df
            
        # Lọc video viral
        viral_videos = df[df['is_viral'] == True].copy()
        
        # Sắp xếp theo tỷ lệ tương tác giảm dần
        if 'engagement_rate' in viral_videos.columns:
            viral_videos = viral_videos.sort_values(by='engagement_rate', ascending=False)
            
        return viral_videos
        
    def get_trending_niches(self, data=None, top_n=5):
        """
        Lấy danh sách các niche đang trending dựa trên số lượng video viral
        
        Args:
            data: DataFrame hoặc None để tải từ database
            top_n: Số lượng niche hàng đầu để trả về
            
        Returns:
            list: Danh sách các niche phổ biến nhất
        """
        df = data if data is not None else self.load_data()
        if df.empty:
            return []
            
        # Lọc video viral
        viral_videos = df[df['is_viral'] == True]
        
        if viral_videos.empty:
            return []
            
        # Đếm số lượng video theo niche
        niche_counts = viral_videos['niche'].value_counts().to_dict()
        
        # Trả về top N niches
        top_niches = sorted(niche_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
        
        return [{"niche": niche, "count": count} for niche, count in top_niches]
        
    def get_trending_hashtags(self, data=None, top_n=10):
        """
        Lấy danh sách các hashtag đang trending
        
        Args:
            data: DataFrame hoặc None để tải từ database
            top_n: Số lượng hashtag hàng đầu để trả về
            
        Returns:
            list: Danh sách các hashtag phổ biến nhất
        """
        df = data if data is not None else self.load_data()
        if df.empty:
            return []
            
        # Tập hợp tất cả hashtag
        all_hashtags = []
        for hashtags_list in df['hashtags']:
            if isinstance(hashtags_list, list):
                all_hashtags.extend(hashtags_list)
                
        # Đếm số lần xuất hiện của mỗi hashtag
        hashtag_counts = Counter(all_hashtags)
        
        # Trả về top N hashtags
        top_hashtags = hashtag_counts.most_common(top_n)
        
        return [{"hashtag": tag, "count": count} for tag, count in top_hashtags]
        
    def get_trending_sounds(self, data=None, top_n=5):
        """
        Lấy danh sách các âm thanh đang trending
        
        Args:
            data: DataFrame hoặc None để tải từ database
            top_n: Số lượng âm thanh hàng đầu để trả về
            
        Returns:
            list: Danh sách các âm thanh phổ biến nhất
        """
        df = data if data is not None else self.load_data()
        if df.empty:
            return []
            
        # Đếm số lần xuất hiện của mỗi âm thanh
        sound_counts = df['sound'].value_counts().to_dict()
        
        # Loại bỏ âm thanh 'Unknown'
        if 'Unknown' in sound_counts:
            del sound_counts['Unknown']
            
        # Trả về top N sounds
        top_sounds = sorted(sound_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
        
        return [{"sound": sound, "count": count} for sound, count in top_sounds]
        
    def get_optimal_video_length(self, data=None):
        """
        Phân tích độ dài tối ưu của video dựa trên tỷ lệ tương tác
        
        Args:
            data: DataFrame hoặc None để tải từ database
            
        Returns:
            dict: Thông tin về độ dài video tối ưu
        """
        df = data if data is not None else self.load_data()
        if df.empty:
            return {"optimal_range": "Không đủ dữ liệu"}
            
        # Chỉ phân tích video có thông tin thời lượng hợp lệ
        valid_duration_df = df[df['duration'] != 'Unknown'].copy()
        
        if valid_duration_df.empty:
            return {"optimal_range": "Không đủ dữ liệu"}
            
        # Chuyển đổi thời lượng thành số giây
        def convert_duration_to_seconds(duration_str):
            try:
                if ':' in duration_str:
                    parts = duration_str.split(':')
                    if len(parts) == 2:
                        return int(parts[0]) * 60 + int(parts[1])
                    elif len(parts) == 3:
                        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
                return 0
            except:
                return 0
                
        valid_duration_df['duration_seconds'] = valid_duration_df['duration'].apply(convert_duration_to_seconds)
        
        # Phân nhóm video theo thời lượng
        duration_bins = [0, 15, 30, 60, 120, 180, 300, float('inf')]
        bin_labels = ['0-15s', '16-30s', '31-60s', '1-2m', '2-3m', '3-5m', '5m+']
        
        valid_duration_df['duration_group'] = pd.cut(
            valid_duration_df['duration_seconds'], 
            bins=duration_bins, 
            labels=bin_labels, 
            include_lowest=True
        )
        
        # Tính tỷ lệ tương tác trung bình theo nhóm thời lượng
        engagement_by_duration = valid_duration_df.groupby('duration_group')['engagement_rate'].mean().to_dict()
        
        # Tìm nhóm có tỷ lệ tương tác cao nhất
        if engagement_by_duration:
            optimal_duration = max(engagement_by_duration.items(), key=lambda x: x[1])
            return {
                "optimal_range": optimal_duration[0],
                "average_engagement": optimal_duration[1],
                "all_ranges": [
                    {"range": duration, "engagement": engagement}
                    for duration, engagement in engagement_by_duration.items()
                ]
            }
        
        return {"optimal_range": "Không đủ dữ liệu"}
        
    def get_dashboard_stats(self, data=None):
        """
        Lấy tất cả số liệu thống kê cho dashboard
        
        Returns:
            dict: Tất cả số liệu thống kê
        """
        df = data if data is not None else self.load_data()
        
        stats = {
            "total_videos": len(df) if not df.empty else 0,
            "viral_videos": len(df[df['is_viral'] == True]) if not df.empty else 0,
            "trending_niches": self.get_trending_niches(df),
            "trending_hashtags": self.get_trending_hashtags(df),
            "trending_sounds": self.get_trending_sounds(df),
            "optimal_video_length": self.get_optimal_video_length(df)
        }
        
        return stats 