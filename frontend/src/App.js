import React, { useState, useEffect } from 'react';
import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';

// Components
import Header from './components/Header';
import ControlPanel from './components/ControlPanel';
import ResultsPanel from './components/ResultsPanel';
import Dashboard from './components/Dashboard';
import NavigationTabs from './components/NavigationTabs';
import SavedFiles from './components/SavedFiles';

function App() {
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('scraper');
  const [dashboardData, setDashboardData] = useState(null);
  const [isDashboardLoading, setIsDashboardLoading] = useState(false);

  // Lấy dữ liệu dashboard khi chuyển tab
  useEffect(() => {
    if (activeTab === 'dashboard') {
      fetchDashboardData();
    }
  }, [activeTab]);

  const fetchDashboardData = async () => {
    setIsDashboardLoading(true);
    
    try {
      const response = await fetch('http://localhost:5000/api/dashboard');
      const data = await response.json();
      
      if (data.status === 'success') {
        setDashboardData(data.data);
      } else {
        setError(data.message || 'Lỗi khi tải dữ liệu dashboard');
      }
    } catch (error) {
      setError('Không thể kết nối đến server để lấy dữ liệu dashboard');
    } finally {
      setIsDashboardLoading(false);
    }
  };

  return (
    <div className="App">
      <Header />
      <div className="container my-4">
        <NavigationTabs activeTab={activeTab} setActiveTab={setActiveTab} />
        
        {activeTab === 'scraper' && (
          <div className="row mt-4">
            <div className="col-md-4">
              <ControlPanel 
                setResults={setResults} 
                setIsLoading={setIsLoading} 
                setError={setError}
              />
            </div>
            <div className="col-md-8">
              <ResultsPanel 
                results={results} 
                isLoading={isLoading} 
                error={error}
              />
            </div>
          </div>
        )}
        
        {activeTab === 'saved-files' && (
          <div className="mt-4">
            <SavedFiles />
          </div>
        )}
        
        {activeTab === 'dashboard' && (
          <Dashboard 
            data={dashboardData}
            isLoading={isDashboardLoading}
            error={error}
            refreshData={fetchDashboardData}
          />
        )}
      </div>
    </div>
  );
}

export default App; 