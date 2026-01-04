import React, { useState, useEffect } from 'react';
import Layout from '@theme/Layout';
import Chatbot from '@site/src/components/Chatbot';

export default function LayoutWrapper(props) {
  const [showChatbot, setShowChatbot] = useState(false);

  // Show chatbot button on all pages
  useEffect(() => {
    // Add any initialization logic here if needed
  }, []);

  return (
    <Layout {...props}>
      {props.children}
      <div className="chatbot-fab" style={{
        position: 'fixed',
        bottom: '20px',
        right: '20px',
        zIndex: 1000
      }}>
        {!showChatbot ? (
          <button
            onClick={() => setShowChatbot(true)}
            style={{
              backgroundColor: '#2563eb',
              color: 'white',
              border: 'none',
              borderRadius: '50%',
              width: '60px',
              height: '60px',
              fontSize: '24px',
              cursor: 'pointer',
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)'
            }}
          >
            💬
          </button>
        ) : (
          <div style={{
            width: '400px',
            height: '500px',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
            borderRadius: '8px',
            overflow: 'hidden'
          }}>
            <Chatbot />
            <button
              onClick={() => setShowChatbot(false)}
              style={{
                position: 'absolute',
                top: '10px',
                right: '10px',
                background: 'none',
                border: 'none',
                fontSize: '20px',
                cursor: 'pointer',
                color: '#666'
              }}
            >
              ×
            </button>
          </div>
        )}
      </div>
    </Layout>
  );
}