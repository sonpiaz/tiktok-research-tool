from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
import time
import json
import os
import re
from datetime import datetime
from fake_useragent import UserAgent
from retry import retry
from tqdm import tqdm
import logging

# Thiết lập logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("tiktok_scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("TikTokScraper")

class TikTokScraper:
    def __init__(self, use_proxy=False, proxy_list=None):
        """
        Khởi tạo TikTok Scraper
        
        Args:
            use_proxy (bool): Có sử dụng proxy không
            proxy_list (list): Danh sách proxy (optional)
        """
        self.driver = None
        self.results = []
        self.use_proxy = use_proxy
        self.proxy_list = proxy_list
        self.user_agent = UserAgent()
        
    def setup(self):
        """Thiết lập trình duyệt Chrome với Selenium"""
        logger.info("Đang thiết lập trình duyệt...")
        chrome_options = Options()
        
        # Thêm random user agent để tránh bị phát hiện
        random_user_agent = self.user_agent.random
        logger.info(f"Sử dụng User-Agent: {random_user_agent}")
        chrome_options.add_argument(f"--user-agent={random_user_agent}")
        
        # Các tùy chọn khác
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-extensions")
        
        # Thêm proxy nếu được yêu cầu
        if self.use_proxy and self.proxy_list:
            proxy = self.get_random_proxy()
            if proxy:
                logger.info(f"Sử dụng proxy: {proxy}")
                chrome_options.add_argument(f'--proxy-server={proxy}')
        
        # Tạo driver
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.maximize_window()
            self.driver.set_page_load_timeout(30)  # Timeout 30 giây
            logger.info("Thiết lập trình duyệt thành công")
            return True
        except Exception as e:
            logger.error(f"Lỗi khi thiết lập trình duyệt: {str(e)}")
            return False
    
    def get_random_proxy(self):
        """Lấy proxy ngẫu nhiên từ danh sách"""
        if not self.proxy_list:
            return None
        
        import random
        return random.choice(self.proxy_list)
    
    @retry(TimeoutException, tries=3, delay=2)
    def navigate_to_tiktok(self):
        """Điều hướng đến TikTok For You Page"""
        logger.info("Đang mở trang TikTok...")
        try:
            self.driver.get("https://www.tiktok.com/foryou")
            
            # Chờ trang tải xong
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='DivVideoWrapper']"))
            )
            logger.info("Đã mở trang TikTok thành công")
            return True
        except TimeoutException:
            logger.error("Timeout khi tải trang TikTok")
            raise
        except Exception as e:
            logger.error(f"Lỗi khi mở trang TikTok: {str(e)}")
            return False
    
    def scrape(self, duration=60, scroll_speed=3, max_videos=None):
        """
        Thực hiện scraping TikTok
        
        Args:
            duration (int): Thời gian scraping (giây)
            scroll_speed (int): Tốc độ cuộn (1-5, 5 là nhanh nhất)
            max_videos (int): Số lượng video tối đa cần thu thập
            
        Returns:
            list: Danh sách các video đã scrape được
        """
        if not self.driver:
            raise Exception("Trình duyệt chưa được thiết lập. Hãy gọi setup() trước.")
        
        # Điều hướng đến TikTok
        if not self.navigate_to_tiktok():
            return []
            
        logger.info(f"Bắt đầu cuộn và thu thập dữ liệu trong {duration} giây...")
        start_time = time.time()
        end_time = start_time + duration
        
        # Khởi tạo progress bar
        if max_videos:
            pbar = tqdm(total=max_videos, desc="Thu thập video")
        else:
            pbar = tqdm(desc="Thu thập video")
        
        # Dictionary để lưu video đã thu thập để tránh trùng lặp
        seen_videos = {}
        
        try:
            # Xử lý bất kỳ hộp thoại consent nào
            self._handle_consent_popup()
            
            while time.time() < end_time:
                if max_videos and len(self.results) >= max_videos:
                    logger.info(f"Đã đạt số lượng video tối đa ({max_videos})")
                    break
                    
                # Lấy dữ liệu video hiện tại
                try:
                    current_video = self._extract_video_data()
                    if current_video:
                        # Sử dụng username + description làm key để tránh trùng lặp
                        video_key = f"{current_video.get('username')}-{current_video.get('description')[:50]}"
                        
                        if video_key not in seen_videos:
                            seen_videos[video_key] = True
                            self.results.append(current_video)
                            pbar.update(1)
                            logger.info(f"Đã thu thập video: {current_video.get('username')} - {current_video.get('description')[:30]}...")
                except Exception as e:
                    logger.error(f"Lỗi khi thu thập dữ liệu video: {str(e)}")
                
                # Cuộn đến video tiếp theo
                self._scroll_to_next_video()
                
                # Đợi dựa trên tốc độ cuộn
                wait_time = 6 - scroll_speed  # 5->1s, 1->5s
                time.sleep(wait_time)
        except KeyboardInterrupt:
            logger.info("Đã dừng scraping do người dùng huỷ")
        except Exception as e:
            logger.error(f"Lỗi không xác định khi scraping: {str(e)}")
        finally:
            pbar.close()
        
        logger.info(f"Hoàn thành. Đã thu thập {len(self.results)} videos.")
        return self.results
    
    def _handle_consent_popup(self):
        """Xử lý bất kỳ popup consent nào"""
        try:
            # Tìm và click nút "Accept" hoặc "Agree" trong popup
            accept_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'Agree') or contains(text(), 'Got it')]")
            if accept_buttons:
                accept_buttons[0].click()
                logger.info("Đã xử lý popup consent")
                time.sleep(1)
        except Exception as e:
            logger.warn(f"Không tìm thấy hoặc không thể click popup consent: {str(e)}")
    
    def _scroll_to_next_video(self):
        """Cuộn đến video tiếp theo"""
        try:
            # Cuộn xuống để xem video tiếp theo
            self.driver.execute_script("window.scrollBy(0, window.innerHeight);")
            return True
        except Exception as e:
            logger.error(f"Lỗi khi cuộn xuống: {str(e)}")
            return False
    
    @retry(exceptions=(StaleElementReferenceException, NoSuchElementException), tries=3, delay=1)
    def _extract_video_data(self):
        """Trích xuất dữ liệu từ video hiện tại"""
        try:
            # Tìm phần tử video hiện tại
            video_container = self.driver.find_element(By.CSS_SELECTOR, "div[class*='DivVideoWrapper']")
            
            # Trích xuất thông tin cơ bản
            username_elem = self.driver.find_element(By.CSS_SELECTOR, "span[class*='SpanUniqueId']")
            description_elem = self.driver.find_element(By.CSS_SELECTOR, "div[class*='DivContainer'] > span")
            
            # Tìm các số liệu tương tác (likes, comments, shares)
            like_elem = self.driver.find_elements(By.CSS_SELECTOR, "strong[data-e2e='like-count']")
            comment_elem = self.driver.find_elements(By.CSS_SELECTOR, "strong[data-e2e='comment-count']")
            share_elem = self.driver.find_elements(By.CSS_SELECTOR, "strong[data-e2e='share-count']")
            
            # Thử lấy thông tin thời lượng video
            try:
                duration_elem = self.driver.find_element(By.CSS_SELECTOR, "div[class*='DivVideoDuration']")
                duration = duration_elem.text
            except (NoSuchElementException, StaleElementReferenceException):
                duration = "Unknown"
                
            # Thử lấy thông tin âm thanh
            try:
                sound_elem = self.driver.find_element(By.CSS_SELECTOR, "div[class*='DivMusicText']")
                sound = sound_elem.text
            except (NoSuchElementException, StaleElementReferenceException):
                sound = "Unknown"
            
            # Trích xuất giá trị
            username = username_elem.text if username_elem else "Unknown"
            description = description_elem.text if description_elem else ""
            
            likes = like_elem[0].text if like_elem else "0"
            comments = comment_elem[0].text if comment_elem else "0"
            shares = share_elem[0].text if share_elem else "0"
            
            # Trích xuất hashtags từ mô tả
            hashtags = re.findall(r'#(\w+)', description)
            
            # Ước tính niche dựa trên hashtag và mô tả
            niche = self._estimate_niche(description, hashtags)
            
            # Kiểm tra xem video có viral không
            is_viral = self._check_if_viral(likes, comments, shares)
            
            # Chuyển đổi các số liệu từ dạng K, M thành số nguyên
            likes_count = self._convert_to_number(likes)
            comments_count = self._convert_to_number(comments)
            shares_count = self._convert_to_number(shares)
            
            # Lưu dữ liệu video
            video_data = {
                "username": username,
                "description": description,
                "likes": likes,
                "comments": comments,
                "shares": shares,
                "likes_count": likes_count,
                "comments_count": comments_count,
                "shares_count": shares_count,
                "duration": duration,
                "sound": sound,
                "hashtags": hashtags,
                "niche": niche,
                "is_viral": is_viral,
                "engagement_rate": self._calculate_engagement(likes_count, comments_count, shares_count),
                "timestamp": time.time(),
                "collected_at": datetime.now().isoformat()
            }
            
            return video_data
            
        except (StaleElementReferenceException, NoSuchElementException) as e:
            logger.error(f"Element đã bị thay đổi hoặc không tồn tại: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Lỗi khi trích xuất dữ liệu video: {str(e)}")
            return None
    
    def _convert_to_number(self, value_str):
        """Chuyển đổi các giá trị dạng 1.5K, 2M thành số nguyên"""
        if not value_str or value_str == "Unknown":
            return 0
            
        try:
            value_str = value_str.strip()
            if 'K' in value_str or 'k' in value_str:
                return int(float(value_str.replace('K', '').replace('k', '')) * 1000)
            elif 'M' in value_str or 'm' in value_str:
                return int(float(value_str.replace('M', '').replace('m', '')) * 1000000)
            elif 'B' in value_str or 'b' in value_str:
                return int(float(value_str.replace('B', '').replace('b', '')) * 1000000000)
            else:
                # Xóa bỏ các ký tự không phải số
                cleaned_str = ''.join(c for c in value_str if c.isdigit() or c == '.')
                return int(float(cleaned_str)) if cleaned_str else 0
        except Exception as e:
            logger.warning(f"Không thể chuyển đổi {value_str} thành số: {str(e)}")
            return 0
    
    def _calculate_engagement(self, likes, comments, shares):
        """Tính toán tỷ lệ tương tác"""
        total = likes + comments + shares
        if total == 0:
            return 0
        return total
        
    def _check_if_viral(self, likes, comments, shares):
        """
        Kiểm tra xem video có viral không dựa trên số liệu tương tác
        - Viral: Video có tỷ lệ tương tác cao
        """
        likes_count = self._convert_to_number(likes)
        comments_count = self._convert_to_number(comments)
        shares_count = self._convert_to_number(shares)
        
        # Ngưỡng đơn giản để xác định video viral
        return (likes_count >= 10000) or (comments_count >= 1000) or (shares_count >= 1000)
    
    def _estimate_niche(self, description, hashtags):
        """
        Ước tính niche của video dựa trên mô tả và hashtag
        """
        text = description.lower() + ' ' + ' '.join(hashtags).lower()
        
        # Danh sách từ khóa cho các niche phổ biến
        niche_keywords = {
            'beauty': ['makeup', 'skincare', 'beauty', 'cosmetic', 'hair', 'nail', 'skin', 'lipstick', 'eyeliner', 'mỹ phẩm', 'làm đẹp', 'trang điểm'],
            'fashion': ['fashion', 'outfit', 'style', 'clothing', 'dress', 'shoes', 'accessory', 'accessories', 'thời trang', 'phụ kiện', 'giày dép', 'trang phục'],
            'food': ['food', 'recipe', 'cooking', 'chef', 'baking', 'meal', 'cuisine', 'delicious', 'tasty', 'yummy', 'ăn uống', 'món ăn', 'nấu ăn', 'công thức', 'đồ ăn'],
            'fitness': ['workout', 'fitness', 'gym', 'exercise', 'training', 'muscle', 'weight', 'health', 'healthy', 'tập gym', 'thể dục', 'thể hình', 'sức khỏe'],
            'travel': ['travel', 'trip', 'vacation', 'tourist', 'tourism', 'destination', 'journey', 'adventure', 'du lịch', 'phượt', 'khám phá', 'chuyến đi'],
            'gaming': ['game', 'gaming', 'gamer', 'play', 'playstation', 'xbox', 'nintendo', 'steam', 'esport', 'chơi game', 'trò chơi', 'game thủ'],
            'tech': ['tech', 'technology', 'gadget', 'computer', 'smartphone', 'device', 'application', 'software', 'hardware', 'công nghệ', 'máy tính', 'thiết bị'],
            'education': ['learn', 'education', 'school', 'student', 'teacher', 'knowledge', 'science', 'study', 'học tập', 'giáo dục', 'kiến thức', 'học sinh', 'sinh viên'],
            'comedy': ['funny', 'comedy', 'joke', 'humor', 'laugh', 'lol', 'hilarious', 'meme', 'hài hước', 'cười', 'hài', 'vui nhộn'],
            'dance': ['dance', 'choreography', 'dancing', 'dancer', 'challenge', 'nhảy', 'vũ đạo', 'dancer', 'thử thách'],
            'music': ['music', 'song', 'singer', 'rap', 'artist', 'band', 'concert', 'playlist', 'album', 'âm nhạc', 'bài hát', 'ca sĩ', 'nghệ sĩ', 'hòa nhạc'],
            'ai': ['ai', 'artificial intelligence', 'ml', 'machine learning', 'neural', 'gpt', 'chatgpt', 'openai', 'deep learning', 'trí tuệ nhân tạo', 'học máy'],
            'lifestyle': ['lifestyle', 'life', 'daily', 'routine', 'minimalism', 'sustainable', 'self-care', 'cuộc sống', 'hàng ngày', 'thói quen']
        }
        
        # Tính điểm cho mỗi niche
        niche_scores = {niche: 0 for niche in niche_keywords}
        for niche, keywords in niche_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    niche_scores[niche] += 1
        
        # Lấy niche có điểm cao nhất
        if max(niche_scores.values()) > 0:
            return max(niche_scores, key=niche_scores.get)
        else:
            return "other"
    
    def get_collected_data(self):
        """Lấy dữ liệu đã thu thập"""
        return self.results
    
    def export_to_json(self, filename="tiktok_data.json"):
        """Xuất dữ liệu ra file JSON"""
        if not self.results:
            logger.warning("Không có dữ liệu để xuất")
            return False
            
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, ensure_ascii=False, indent=4)
            logger.info(f"Đã xuất dữ liệu ra {filename}")
            return True
        except Exception as e:
            logger.error(f"Lỗi khi xuất dữ liệu ra JSON: {str(e)}")
            return False
            
    def teardown(self):
        """Dọn dẹp và đóng trình duyệt"""
        if self.driver:
            logger.info("Đóng trình duyệt...")
            self.driver.quit()
            self.driver = None 