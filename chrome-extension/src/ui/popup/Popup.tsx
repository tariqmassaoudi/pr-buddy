import React, { useState, useEffect } from 'react';
import './Popup.css';
import { LANGGRAPH_API_URL } from '../../api/config/constants';

// Types for our assistant data
interface Assistant {
  assistant_id: string;
  name: string;
  graph_id: string;
}

interface ConnectionStatus {
  connected: boolean;
  assistants: Assistant[];
  loading: boolean;
  error: string | null;
}

const Popup: React.FC = () => {
  const [prId, setPrId] = useState<string | null>(null);
  const [status, setStatus] = useState<ConnectionStatus>({
    connected: false,
    assistants: [],
    loading: true,
    error: null
  });

  // Check LangGraph connection and available assistants
  const checkLangGraphStatus = async () => {
    setStatus(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      const response = await fetch(`${LANGGRAPH_API_URL}/assistants/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
      });
      
      if (!response.ok) {
        throw new Error(`Connection error: ${response.status}`);
      }
      
      const assistants = await response.json();
      
      setStatus({
        connected: true,
        assistants: assistants,
        loading: false,
        error: null
      });
    } catch (error) {
      console.error('Error connecting to LangGraph:', error);
      setStatus({
        connected: false,
        assistants: [],
        loading: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      });
    }
  };

  useEffect(() => {
    // Check LangGraph status on load
    checkLangGraphStatus();
    
    // Listen for messages from content script
    const messageListener = (message: any) => {
      if (message.action === 'prIdExtracted' && message.prId) {
        setPrId(message.prId);
      }
    };

    // Add listener
    chrome.runtime.onMessage.addListener(messageListener);
    
    // On mount, query any existing PR ID from active tab
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const activeTab = tabs[0];
      if (activeTab?.url && activeTab.url.includes('dev.azure.com') && activeTab.url.includes('/pullrequest/')) {
        const match = activeTab.url.match(/\/pullrequest\/(\d+)/);
        if (match && match[1]) {
          setPrId(match[1]);
        }
      }
    });

    // Cleanup
    return () => {
      chrome.runtime.onMessage.removeListener(messageListener);
    };
  }, []);

  // Get status icon and color based on connection state
  const getStatusInfo = () => {
    if (status.loading) {
      return { icon: '⟳', color: '#f5a623', text: 'Checking connection...' };
    } else if (status.connected) {
      return { icon: '✓', color: '#4caf50', text: 'Connected to LangGraph' };
    } else {
      return { icon: '✗', color: '#e53935', text: 'Not connected to LangGraph' };
    }
  };

  const statusInfo = getStatusInfo();

  return (
    <div className="popup-container">
      <header>
        <div className="logo">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" />
            <path d="M8 14s1.5 2 4 2 4-2 4-2" />
            <line x1="9" y1="9" x2="9.01" y2="9" />
            <line x1="15" y1="9" x2="15.01" y2="9" />
          </svg>
        </div>
        <h1>PR Buddy</h1>
      </header>

      <div className="content">
        {/* Connection Status Card */}
        <div className="connection-card">
          <div className={`status-indicator ${status.loading ? 'loading' : status.connected ? 'connected' : 'disconnected'}`}>
            <span className="status-icon" style={{ color: statusInfo.color }}>
              {statusInfo.icon}
            </span>
            <span className="status-text">{statusInfo.text}</span>
          </div>
          
          {status.error && (
            <div className="error-message">
              {status.error}
            </div>
          )}
          
          <button 
            className={`refresh-button ${status.loading ? 'loading' : ''}`}
            onClick={checkLangGraphStatus}
            disabled={status.loading}
          >
            {status.loading ? 'Checking...' : 'Check Connection'}
          </button>
        </div>
        
        {/* Assistants List when connected */}
        {status.connected && status.assistants.length > 0 && (
          <div className="assistants-container">
            <h2>Available Assistants</h2>
            <div className="assistants-list">
              {status.assistants.map(assistant => (
                <div key={assistant.assistant_id} className="assistant-item">
                  <div className="assistant-name">
                    {assistant.name}
                  </div>
                  <div className="assistant-id">
                    ID: {assistant.assistant_id.substring(0, 8)}...
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        
        {/* PR Info when on a PR page */}
        {prId && (
          <div className="pr-info">
            <div className="tip">
              <span className="tip-icon">💡</span>
              <p>PR #{prId} detected. Use the buttons in Azure DevOps to write or review this PR with AI</p>
            </div>
          </div>
        )}
        
        {/* No PR message when not on a PR page */}
        {!prId && (
          <div className="no-pr">
            <p>No Azure DevOps PR detected</p>
            <p className="sub-text">Navigate to an Azure DevOps PR page to use the extension</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Popup;
