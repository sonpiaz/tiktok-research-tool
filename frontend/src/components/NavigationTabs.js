import React from 'react';

const NavigationTabs = ({ activeTab, setActiveTab }) => {
  return (
    <ul className="nav nav-tabs">
      <li className="nav-item">
        <button 
          className={`nav-link ${activeTab === 'scraper' ? 'active' : ''}`}
          onClick={() => setActiveTab('scraper')}
        >
          Data Collection
        </button>
      </li>
      <li className="nav-item">
        <button 
          className={`nav-link ${activeTab === 'saved-files' ? 'active' : ''}`}
          onClick={() => setActiveTab('saved-files')}
        >
          Saved Files
        </button>
      </li>
      <li className="nav-item">
        <button 
          className={`nav-link ${activeTab === 'dashboard' ? 'active' : ''}`}
          onClick={() => setActiveTab('dashboard')}
        >
          Dashboard
        </button>
      </li>
    </ul>
  );
};

export default NavigationTabs; 