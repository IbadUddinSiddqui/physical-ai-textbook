import React, { useState, useEffect } from 'react';
import OriginalLayout from '@theme-original/Layout';
import Chatbot from '@site/src/components/Chatbot';

export default function Layout(props) {
  const [showChatbot, setShowChatbot] = useState(false);

  // Toggle chatbot visibility
  const toggleChatbot = () => {
    setShowChatbot(!showChatbot);
  };

  return (
    <>
      <OriginalLayout {...props}>
        {props.children}
      </OriginalLayout>

      {/* Floating Action Button for Chatbot */}
      <div className="chatbot-fab" style={{
        position: 'fixed',
        bottom: '20px',
        right: '20px',
        zIndex: 10000
      }}>
        {!showChatbot ? (
          <button
            onClick={toggleChatbot}
            style={{
              backgroundColor: '#2563eb',
              color: 'white',
              border: 'none',
              borderRadius: '50%',
              width: '60px',
              height: '60px',
              fontSize: '24px',
              cursor: 'pointer',
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
            aria-label="Open chatbot"
          >
            💬
          </button>
        ) : (
          <div style={{
            width: '400px',
            height: '500px',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
            borderRadius: '8px',
            overflow: 'hidden',
            position: 'relative'
          }}>
            <div style={{
              position: 'absolute',
              top: 0,
              right: 0,
              zIndex: 10001
            }}>
              <button
                onClick={toggleChatbot}
                style={{
                  background: 'none',
                  border: 'none',
                  fontSize: '24px',
                  cursor: 'pointer',
                  color: '#666',
                  padding: '5px',
                  borderRadius: '50%',
                  width: '30px',
                  height: '30px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
                aria-label="Close chatbot"
              >
                ×
              </button>
            </div>
            <Chatbot />
          </div>
        )}
      </div>
    </>
  );
}