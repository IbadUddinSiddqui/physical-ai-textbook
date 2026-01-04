import React, { useState, useEffect, useRef } from 'react';
import './Chatbot.css';

const Chatbot = () => {
  const [messages, setMessages] = useState([
    { id: 1, text: "Hello! I'm your Physical AI & Humanoid Robotics textbook assistant. How can I help you today?", sender: 'bot' }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    // Add user message
    const userMessage = {
      id: Date.now(),
      text: inputValue,
      sender: 'user'
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Call the backend API
      // Using a fixed URL that matches the backend server
      // The backend expects the query as a query parameter in the URL
      const API_BASE_URL = 'http://localhost:8001';
      const response = await fetch(`${API_BASE_URL}/api/v1/chat?query=${encodeURIComponent(inputValue)}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // Add bot response
      const botMessage = {
        id: Date.now() + 1,
        text: data.response || "Sorry, I couldn't process your request.",
        sender: 'bot'
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Chatbot Error Details:', {
        message: error.message,
        stack: error.stack,
        name: error.name
      });

      let errorMessageText = "Sorry, I'm having trouble connecting to the textbook assistant. ";

      // Provide more specific error messages based on the error type
      if (error.message.includes('fetch') || error.message.includes('Failed to fetch')) {
        errorMessageText += "Could not connect to the API server. Please check if the backend server is running on http://localhost:8001.";
      } else if (error.message.includes('404') || error.message.includes('Not Found')) {
        errorMessageText += "The API endpoint was not found. Please verify the API URL is correct.";
      } else if (error.message.includes('401') || error.message.includes('403')) {
        errorMessageText += "Access to the API was denied. Please check API authentication.";
      } else if (error.message.includes('500')) {
        errorMessageText += "The API server encountered an error. Please check the server logs.";
      } else if (error.message.includes('NetworkError')) {
        errorMessageText += "There was a network error. Please check your internet connection.";
      } else {
        errorMessageText += `Error details: ${error.message}`;
      }

      const errorMessage = {
        id: Date.now() + 1,
        text: errorMessageText,
        sender: 'bot'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chatbot-container">
      <div className="chatbot-header">
        <h3>Physical AI Textbook Assistant</h3>
        <p>Ask me anything about Physical AI & Humanoid Robotics</p>
      </div>

      <div className="chatbot-messages">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`message ${message.sender}-message`}
          >
            <div className="message-text">{message.text}</div>
          </div>
        ))}
        {isLoading && (
          <div className="message bot-message">
            <div className="message-text">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form className="chatbot-input-form" onSubmit={handleSendMessage}>
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Ask a question about Physical AI or Humanoid Robotics..."
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading}>
          Send
        </button>
      </form>
    </div>
  );
};

export default Chatbot;