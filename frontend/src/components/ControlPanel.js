import React, { useState } from 'react';
import axios from 'axios';

const ControlPanel = ({ setResults, setIsLoading, setError }) => {
  // Các tham số scraping
  const [duration, setDuration] = useState(60);
  const [scrollSpeed, setScrollSpeed] = useState(3);
  const [maxVideos, setMaxVideos] = useState(50);
  const [saveToFile, setSaveToFile] = useState(true);
  const [useProxy, setUseProxy] = useState(false);
  const [proxyList, setProxyList] = useState('');
  const [savedFilePath, setSavedFilePath] = useState(null);
  
  // Trạng thái giao diện
  const [advancedOptions, setAdvancedOptions] = useState(false);

  const handleStartScraping = async () => {
    setIsLoading(true);
    setError(null);
    setSavedFilePath(null);
    
    try {
      // Chuẩn bị dữ liệu gửi đi
      const requestData = {
        duration, 
        scrollSpeed,
        maxVideos: maxVideos > 0 ? maxVideos : null,
        saveToFile,
        useProxy
      };
      
      // Thêm proxy list nếu có
      if (useProxy && proxyList.trim()) {
        requestData.proxyList = proxyList.split('\n').filter(line => line.trim());
      }
      
      const response = await axios.post('http://localhost:5000/api/scrape', requestData);
      
      if (response.data.status === 'success') {
        setResults(response.data.data);
        if (response.data.saved_to_file) {
          setSavedFilePath(response.data.saved_to_file);
        }
      } else {
        setError(response.data.message || 'Đã xảy ra lỗi khi thu thập dữ liệu');
      }
    } catch (error) {
      setError(error.message || 'Không thể kết nối đến server');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="card">
      <div className="card-header bg-primary text-white">
        <h5 className="mb-0">Bảng điều khiển</h5>
      </div>
      <div className="card-body">
        <div className="mb-3">
          <label htmlFor="duration" className="form-label">Thời gian chạy (giây)</label>
          <input 
            type="number" 
            className="form-control" 
            id="duration"
            value={duration}
            onChange={e => setDuration(parseInt(e.target.value) || 0)}
            min="10"
            max="3600"
          />
        </div>
        
        <div className="mb-3">
          <label htmlFor="maxVideos" className="form-label">Số lượng video tối đa</label>
          <input 
            type="number" 
            className="form-control" 
            id="maxVideos"
            value={maxVideos}
            onChange={e => setMaxVideos(parseInt(e.target.value) || 0)}
            min="0"
            max="1000"
          />
          <small className="text-muted">Để 0 nếu không giới hạn số lượng</small>
        </div>
        
        <div className="mb-3">
          <label htmlFor="scrollSpeed" className="form-label">Tốc độ cuộn (1-5)</label>
          <input 
            type="range" 
            className="form-range" 
            id="scrollSpeed"
            value={scrollSpeed}
            onChange={e => setScrollSpeed(parseInt(e.target.value))}
            min="1"
            max="5"
          />
          <div className="d-flex justify-content-between">
            <small>Chậm</small>
            <small>Nhanh</small>
          </div>
        </div>
        
        <div className="mb-3 form-check">
          <input 
            type="checkbox" 
            className="form-check-input" 
            id="saveToFile"
            checked={saveToFile}
            onChange={e => setSaveToFile(e.target.checked)}
          />
          <label className="form-check-label" htmlFor="saveToFile">
            Lưu kết quả ra file
          </label>
        </div>
        
        <div className="mb-3">
          <button 
            className="btn btn-link p-0" 
            onClick={() => setAdvancedOptions(!advancedOptions)}
          >
            {advancedOptions ? 'Ẩn tùy chọn nâng cao' : 'Hiển thị tùy chọn nâng cao'}
          </button>
        </div>
        
        {advancedOptions && (
          <div className="advanced-options border rounded p-3 mb-3 bg-light">
            <div className="mb-3 form-check">
              <input 
                type="checkbox" 
                className="form-check-input" 
                id="useProxy"
                checked={useProxy}
                onChange={e => setUseProxy(e.target.checked)}
              />
              <label className="form-check-label" htmlFor="useProxy">
                Sử dụng proxy
              </label>
            </div>
            
            {useProxy && (
              <div className="mb-3">
                <label htmlFor="proxyList" className="form-label">Danh sách proxy (mỗi dòng một proxy)</label>
                <textarea 
                  className="form-control" 
                  id="proxyList"
                  rows="3"
                  value={proxyList}
                  onChange={e => setProxyList(e.target.value)}
                  placeholder="http://user:pass@host:port"
                />
                <small className="text-muted">Ví dụ: http://username:password@proxy.example.com:8080</small>
              </div>
            )}
          </div>
        )}
        
        {savedFilePath && (
          <div className="alert alert-success mb-3">
            <small>Đã lưu dữ liệu vào file: {savedFilePath}</small>
          </div>
        )}
        
        <button 
          className="btn btn-primary w-100" 
          onClick={handleStartScraping}
          disabled={isLoading}
        >
          {isLoading ? 'Đang thu thập dữ liệu...' : 'Bắt đầu thu thập dữ liệu'}
        </button>
      </div>
    </div>
  );
};

export default ControlPanel; 