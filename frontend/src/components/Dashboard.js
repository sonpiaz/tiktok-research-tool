import React from 'react';
import { Pie, Bar } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title } from 'chart.js';

// Đăng ký các thành phần Chart.js
ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title);

const Dashboard = ({ data, isLoading, error, refreshData }) => {
  // Nếu đang tải dữ liệu
  if (isLoading) {
    return (
      <div className="text-center my-5">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Đang tải...</span>
        </div>
        <p className="mt-2">Đang tải dữ liệu dashboard...</p>
      </div>
    );
  }

  // Nếu có lỗi
  if (error) {
    return (
      <div className="alert alert-danger" role="alert">
        {error}
        <button 
          className="btn btn-outline-danger btn-sm ms-3"
          onClick={refreshData}
        >
          Thử lại
        </button>
      </div>
    );
  }

  // Nếu chưa có dữ liệu
  if (!data) {
    return (
      <div className="text-center my-5">
        <p>Chưa có dữ liệu phân tích. Hãy thu thập dữ liệu trước.</p>
        <button 
          className="btn btn-primary"
          onClick={refreshData}
        >
          Tải dữ liệu
        </button>
      </div>
    );
  }

  // Chuẩn bị dữ liệu cho biểu đồ niche
  const nicheChartData = {
    labels: data.trending_niches.map(item => item.niche),
    datasets: [
      {
        label: 'Số lượng video',
        data: data.trending_niches.map(item => item.count),
        backgroundColor: [
          'rgba(255, 99, 132, 0.6)',
          'rgba(54, 162, 235, 0.6)',
          'rgba(255, 206, 86, 0.6)',
          'rgba(75, 192, 192, 0.6)',
          'rgba(153, 102, 255, 0.6)',
        ],
        borderWidth: 1,
      },
    ],
  };

  // Chuẩn bị dữ liệu cho biểu đồ hashtag
  const hashtagChartData = {
    labels: data.trending_hashtags.map(item => item.hashtag),
    datasets: [
      {
        label: 'Số lượng xuất hiện',
        data: data.trending_hashtags.map(item => item.count),
        backgroundColor: 'rgba(54, 162, 235, 0.6)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1,
      },
    ],
  };

  return (
    <div className="dashboard mt-4">
      <div className="row">
        <div className="col-md-4">
          <div className="card h-100">
            <div className="card-header bg-primary text-white">
              <h5 className="mb-0">Tổng quan</h5>
            </div>
            <div className="card-body">
              <div className="d-flex justify-content-between align-items-center mb-3">
                <span className="fw-bold">Tổng số video đã phân tích:</span>
                <span className="badge bg-primary rounded-pill">{data.total_videos}</span>
              </div>
              <div className="d-flex justify-content-between align-items-center mb-3">
                <span className="fw-bold">Số video viral:</span>
                <span className="badge bg-danger rounded-pill">{data.viral_videos}</span>
              </div>
              <div className="mb-3">
                <span className="fw-bold">Thời lượng video tối ưu:</span>
                <p className="mt-2 alert alert-success">
                  {data.optimal_video_length.optimal_range || "Không đủ dữ liệu"}
                </p>
              </div>
              <button 
                className="btn btn-outline-primary btn-sm"
                onClick={refreshData}
              >
                Làm mới dữ liệu
              </button>
            </div>
          </div>
        </div>
        
        <div className="col-md-4">
          <div className="card h-100">
            <div className="card-header bg-success text-white">
              <h5 className="mb-0">Phân bố niche</h5>
            </div>
            <div className="card-body">
              {data.trending_niches.length > 0 ? (
                <Pie data={nicheChartData} />
              ) : (
                <p className="text-center">Chưa đủ dữ liệu để phân tích niche</p>
              )}
            </div>
          </div>
        </div>
        
        <div className="col-md-4">
          <div className="card h-100">
            <div className="card-header bg-info text-white">
              <h5 className="mb-0">Âm thanh phổ biến</h5>
            </div>
            <div className="card-body">
              {data.trending_sounds.length > 0 ? (
                <ul className="list-group">
                  {data.trending_sounds.map((sound, index) => (
                    <li key={index} className="list-group-item d-flex justify-content-between align-items-center">
                      {sound.sound.length > 25 ? sound.sound.substring(0, 25) + '...' : sound.sound}
                      <span className="badge bg-info rounded-pill">{sound.count}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-center">Chưa đủ dữ liệu về âm thanh</p>
              )}
            </div>
          </div>
        </div>
      </div>
      
      <div className="row mt-4">
        <div className="col-12">
          <div className="card">
            <div className="card-header bg-warning">
              <h5 className="mb-0">Hashtag phổ biến</h5>
            </div>
            <div className="card-body">
              {data.trending_hashtags.length > 0 ? (
                <Bar 
                  data={hashtagChartData} 
                  options={{
                    responsive: true,
                    plugins: {
                      legend: {
                        position: 'top',
                      },
                      title: {
                        display: true,
                        text: 'Top Hashtags',
                      },
                    },
                  }}
                />
              ) : (
                <p className="text-center">Chưa đủ dữ liệu về hashtag</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 