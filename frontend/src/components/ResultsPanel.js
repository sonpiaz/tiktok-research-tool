import React, { useState } from 'react';
import axios from 'axios';

const ResultsPanel = ({ results, isLoading, error }) => {
  const [filterViral, setFilterViral] = useState(false);
  const [selectedNiche, setSelectedNiche] = useState('all');
  const [exportLoading, setExportLoading] = useState(false);
  const [exportError, setExportError] = useState(null);
  const [exportSuccess, setExportSuccess] = useState(null);
  
  // Lọc dữ liệu dựa trên điều kiện
  const filteredResults = results.filter(video => {
    // Lọc theo viral
    if (filterViral && !video.is_viral) {
      return false;
    }
    
    // Lọc theo niche
    if (selectedNiche !== 'all' && video.niche !== selectedNiche) {
      return false;
    }
    
    return true;
  });
  
  // Lấy danh sách các niche duy nhất trong dữ liệu
  const uniqueNiches = ['all', ...new Set(results.map(video => video.niche).filter(Boolean))];
  
  // Xuất dữ liệu dưới dạng CSV
  const exportAsCSV = () => {
    if (results.length === 0) return;
    
    // Tạo header cho CSV
    const headers = Object.keys(results[0]).join(',');
    
    // Tạo các dòng dữ liệu
    const dataRows = results.map(video => 
      Object.values(video).map(value => 
        typeof value === 'string' ? `"${value.replace(/"/g, '""')}"` : value
      ).join(',')
    ).join('\n');
    
    // Tạo nội dung CSV
    const csvContent = `${headers}\n${dataRows}`;
    
    // Tạo Blob và download
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `tiktok_data_${new Date().toISOString().slice(0, 10)}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Gửi dữ liệu lên server để lưu
  const saveToFile = async (format) => {
    if (results.length === 0) return;
    
    setExportLoading(true);
    setExportError(null);
    setExportSuccess(null);
    
    try {
      const response = await axios.post('http://localhost:5000/api/export', {
        data: results,
        format: format
      });
      
      if (response.data.status === 'success') {
        setExportSuccess(`Đã lưu dữ liệu vào ${response.data.filename}`);
        
        // Xóa thông báo thành công sau 3 giây
        setTimeout(() => {
          setExportSuccess(null);
        }, 3000);
      } else {
        setExportError(response.data.message || 'Lỗi không xác định khi lưu file');
      }
    } catch (error) {
      setExportError('Không thể kết nối đến server: ' + (error.message || 'lỗi không xác định'));
    } finally {
      setExportLoading(false);
    }
  };

  return (
    <div className="card">
      <div className="card-header bg-info text-white">
        <h5 className="mb-0">Kết quả thu thập</h5>
      </div>
      <div className="card-body">
        {isLoading && (
          <div className="text-center my-5">
            <div className="spinner-border text-primary" role="status">
              <span className="visually-hidden">Đang tải...</span>
            </div>
            <p className="mt-2">Đang thu thập dữ liệu TikTok...</p>
          </div>
        )}
        
        {error && (
          <div className="alert alert-danger" role="alert">
            {error}
          </div>
        )}
        
        {!isLoading && !error && results.length === 0 && (
          <div className="text-center my-5">
            <p>Chưa có dữ liệu. Hãy bắt đầu thu thập bằng cách nhấn nút "Bắt đầu thu thập dữ liệu".</p>
          </div>
        )}
        
        {exportError && (
          <div className="alert alert-danger" role="alert">
            {exportError}
          </div>
        )}
        
        {exportSuccess && (
          <div className="alert alert-success" role="alert">
            {exportSuccess}
          </div>
        )}
        
        {!isLoading && !error && results.length > 0 && (
          <>
            <div className="d-flex justify-content-between align-items-center mb-3">
              <p>Đã thu thập {results.length} videos. Hiển thị {filteredResults.length} videos.</p>
              
              <div className="d-flex gap-2">
                <div className="dropdown">
                  <button 
                    className="btn btn-outline-primary btn-sm dropdown-toggle" 
                    type="button" 
                    id="exportDropdown" 
                    data-bs-toggle="dropdown" 
                    aria-expanded="false"
                    disabled={exportLoading}
                  >
                    {exportLoading ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
                        Đang xuất...
                      </>
                    ) : (
                      <>
                        <i className="bi bi-download me-1"></i> Xuất dữ liệu
                      </>
                    )}
                  </button>
                  <ul className="dropdown-menu" aria-labelledby="exportDropdown">
                    <li>
                      <button 
                        className="dropdown-item" 
                        onClick={exportAsCSV}
                      >
                        <i className="bi bi-filetype-csv me-1"></i> Tải xuống CSV
                      </button>
                    </li>
                    <li>
                      <button 
                        className="dropdown-item" 
                        onClick={() => saveToFile('json')}
                      >
                        <i className="bi bi-filetype-json me-1"></i> Lưu JSON
                      </button>
                    </li>
                    <li>
                      <button 
                        className="dropdown-item" 
                        onClick={() => saveToFile('csv')}
                      >
                        <i className="bi bi-filetype-csv me-1"></i> Lưu CSV
                      </button>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
            
            <div className="row mb-3">
              <div className="col-md-6">
                <div className="form-check form-switch">
                  <input
                    className="form-check-input"
                    type="checkbox"
                    id="filterViralSwitch"
                    checked={filterViral}
                    onChange={e => setFilterViral(e.target.checked)}
                  />
                  <label className="form-check-label" htmlFor="filterViralSwitch">
                    Chỉ hiển thị video viral
                  </label>
                </div>
              </div>
              
              <div className="col-md-6">
                <select 
                  className="form-select"
                  value={selectedNiche}
                  onChange={e => setSelectedNiche(e.target.value)}
                >
                  {uniqueNiches.map((niche, index) => (
                    <option key={index} value={niche}>
                      {niche === 'all' ? 'Tất cả niche' : niche}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            
            <div className="table-responsive">
              <table className="table table-striped table-hover">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Tiêu đề</th>
                    <th>Tác giả</th>
                    <th>Lượt xem</th>
                    <th>Thích</th>
                    <th>Bình luận</th>
                    <th>Niche</th>
                    <th>Hashtags</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredResults.map((video, index) => (
                    <tr key={index}>
                      <td>{index + 1}</td>
                      <td>
                        <a href={video.video_url} target="_blank" rel="noreferrer">
                          {video.title && video.title.length > 30
                            ? video.title.substring(0, 30) + '...'
                            : video.title || 'Không có tiêu đề'}
                        </a>
                      </td>
                      <td>{video.author || '-'}</td>
                      <td>{video.views?.toLocaleString() || '-'}</td>
                      <td>{video.likes?.toLocaleString() || '-'}</td>
                      <td>{video.comments?.toLocaleString() || '-'}</td>
                      <td>{video.niche || '-'}</td>
                      <td>
                        {video.hashtags && video.hashtags.length > 0
                          ? video.hashtags.slice(0, 3).join(', ') + (video.hashtags.length > 3 ? '...' : '')
                          : '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default ResultsPanel; 