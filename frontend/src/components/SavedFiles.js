import React, { useState, useEffect } from 'react';
import axios from 'axios';

const SavedFiles = () => {
  const [files, setFiles] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [deleteSuccess, setDeleteSuccess] = useState(null);

  // Lấy danh sách file đã lưu khi component được mount
  useEffect(() => {
    fetchSavedFiles();
  }, []);

  // Hàm lấy danh sách file đã lưu
  const fetchSavedFiles = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await axios.get('http://localhost:5000/api/files');
      
      if (response.data.status === 'success') {
        setFiles(response.data.files || []);
      } else {
        setError(response.data.message || 'Không thể lấy danh sách file');
      }
    } catch (error) {
      setError('Lỗi kết nối đến server: ' + (error.message || 'Lỗi không xác định'));
    } finally {
      setIsLoading(false);
    }
  };

  // Hàm tải file
  const handleDownloadFile = async (filename) => {
    try {
      // Sử dụng axios với responseType là blob để tải file
      const response = await axios.get(`http://localhost:5000/api/files/download/${filename}`, {
        responseType: 'blob',
      });
      
      // Tạo URL từ blob và tải xuống
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      
      // Dọn dẹp sau khi tải xong
      window.URL.revokeObjectURL(url);
      document.body.removeChild(link);
    } catch (error) {
      setError('Không thể tải file: ' + (error.message || 'Lỗi không xác định'));
    }
  };

  // Hàm xóa file
  const handleDeleteFile = async (filename) => {
    if (!window.confirm(`Bạn có chắc chắn muốn xóa file "${filename}"?`)) {
      return;
    }
    
    try {
      const response = await axios.delete(`http://localhost:5000/api/files/${filename}`);
      
      if (response.data.status === 'success') {
        // Cập nhật lại danh sách file sau khi xóa
        setFiles(files.filter(file => file.filename !== filename));
        setDeleteSuccess(`Đã xóa file ${filename} thành công`);
        
        // Xóa thông báo thành công sau 3 giây
        setTimeout(() => {
          setDeleteSuccess(null);
        }, 3000);
      } else {
        setError(response.data.message || 'Không thể xóa file');
      }
    } catch (error) {
      setError('Lỗi khi xóa file: ' + (error.message || 'Lỗi không xác định'));
    }
  };

  // Định dạng kích thước file
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // Định dạng thời gian
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  return (
    <div className="card">
      <div className="card-header bg-secondary text-white d-flex justify-content-between align-items-center">
        <h5 className="mb-0">Kết quả thu thập đã lưu</h5>
        <button 
          className="btn btn-sm btn-outline-light" 
          onClick={fetchSavedFiles}
          disabled={isLoading}
        >
          <i className="bi bi-arrow-clockwise"></i> Làm mới
        </button>
      </div>
      <div className="card-body">
        {isLoading && (
          <div className="text-center my-3">
            <div className="spinner-border text-primary" role="status">
              <span className="visually-hidden">Đang tải...</span>
            </div>
            <p className="mt-2">Đang tải danh sách file...</p>
          </div>
        )}
        
        {error && (
          <div className="alert alert-danger" role="alert">
            {error}
          </div>
        )}
        
        {deleteSuccess && (
          <div className="alert alert-success" role="alert">
            {deleteSuccess}
          </div>
        )}
        
        {!isLoading && !error && files.length === 0 && (
          <div className="alert alert-info" role="alert">
            Chưa có file kết quả nào được lưu.
          </div>
        )}
        
        {!isLoading && files.length > 0 && (
          <div className="table-responsive">
            <table className="table table-hover">
              <thead>
                <tr>
                  <th>Tên file</th>
                  <th>Kích thước</th>
                  <th>Ngày tạo</th>
                  <th>Thao tác</th>
                </tr>
              </thead>
              <tbody>
                {files.map((file, index) => (
                  <tr key={index}>
                    <td>{file.filename}</td>
                    <td>{formatFileSize(file.size)}</td>
                    <td>{formatDate(file.created_at)}</td>
                    <td>
                      <div className="btn-group" role="group">
                        <button 
                          className="btn btn-sm btn-outline-primary" 
                          onClick={() => handleDownloadFile(file.filename)}
                        >
                          <i className="bi bi-download"></i> Tải xuống
                        </button>
                        <button 
                          className="btn btn-sm btn-outline-danger" 
                          onClick={() => handleDeleteFile(file.filename)}
                        >
                          <i className="bi bi-trash"></i> Xóa
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default SavedFiles; 