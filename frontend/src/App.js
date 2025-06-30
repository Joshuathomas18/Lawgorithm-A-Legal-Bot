import React, { useState, useEffect } from 'react';
import './App.css';

// API Configuration
const API_BASE = 'http://localhost:8001/api/v1';
const CHATBOT_API = 'http://localhost:8001/api/v1/chatbot';

function App() {
  const [currentView, setCurrentView] = useState('dashboard');
  const [sessionId, setSessionId] = useState(null);
  const [conversationId, setConversationId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // Initialize session on load
  useEffect(() => {
    initializeSession();
  }, []);

  const initializeSession = async () => {
    try {
      const response = await fetch(`${API_BASE}/conversations/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: 'premium-user', initial_message: 'Platform initialization' })
      });
      const data = await response.json();
      setSessionId(data.session_id);
      setConversationId(data.conversation_id);
    } catch (error) {
      console.error('Session initialization failed:', error);
    }
  };

  // Navigation Component
  const Navigation = () => (
    <nav className="navbar">
      <div className="nav-brand">
        <div className="logo">
          <div className="logo-icon">⚖️</div>
          <span className="logo-text">LegalAI Pro</span>
        </div>
      </div>
      <div className="nav-links">
        <button 
          className={`nav-link ${currentView === 'dashboard' ? 'active' : ''}`}
          onClick={() => setCurrentView('dashboard')}
        >
          Dashboard
        </button>
        <button 
          className={`nav-link ${currentView === 'chat' ? 'active' : ''}`}
          onClick={() => setCurrentView('chat')}
        >
          AI Assistant
        </button>
        <button 
          className={`nav-link ${currentView === 'analyzer' ? 'active' : ''}`}
          onClick={() => setCurrentView('analyzer')}
        >
          Document Analyzer
        </button>
        <button 
          className={`nav-link ${currentView === 'generator' ? 'active' : ''}`}
          onClick={() => setCurrentView('generator')}
        >
          Legal Generator
        </button>
        <button 
          className={`nav-link ${currentView === 'research' ? 'active' : ''}`}
          onClick={() => setCurrentView('research')}
        >
          Legal Research
        </button>
      </div>
    </nav>
  );

  // Dashboard Component
  const Dashboard = () => (
    <div className="dashboard">
      <div className="hero-section">
        <h1 className="hero-title">AI-Powered Legal Intelligence Platform</h1>
        <p className="hero-subtitle">
          Advanced legal AI tools powered by cutting-edge machine learning and comprehensive Indian legal knowledge
        </p>
        <div className="hero-stats">
          <div className="stat">
            <div className="stat-number">440+</div>
            <div className="stat-label">Legal Documents</div>
          </div>
          <div className="stat">
            <div className="stat-number">50+</div>
            <div className="stat-label">Legal Areas</div>
          </div>
          <div className="stat">
            <div className="stat-number">99.9%</div>
            <div className="stat-label">Accuracy</div>
          </div>
        </div>
      </div>

      <div className="features-grid">
        <div className="feature-card" onClick={() => setCurrentView('chat')}>
          <div className="feature-icon">🤖</div>
          <h3>AI Legal Assistant</h3>
          <p>Get instant legal advice and guidance from our advanced AI trained on Indian legal system</p>
          <div className="feature-action">Start Chat →</div>
        </div>

        <div className="feature-card" onClick={() => setCurrentView('analyzer')}>
          <div className="feature-icon">📄</div>
          <h3>Document Analyzer</h3>
          <p>Upload legal documents and get AI-powered analysis, summaries, and risk assessments</p>
          <div className="feature-action">Analyze Now →</div>
        </div>

        <div className="feature-card" onClick={() => setCurrentView('generator')}>
          <div className="feature-icon">⚡</div>
          <h3>Legal Generator</h3>
          <p>Generate professional legal documents, contracts, and petitions in minutes</p>
          <div className="feature-action">Generate →</div>
        </div>

        <div className="feature-card" onClick={() => setCurrentView('research')}>
          <div className="feature-icon">🔍</div>
          <h3>Legal Research</h3>
          <p>Advanced legal research with case law analysis and precedent discovery</p>
          <div className="feature-action">Research →</div>
        </div>

        <div className="feature-card">
          <div className="feature-icon">📊</div>
          <h3>Case Predictor</h3>
          <p>AI-powered case outcome prediction based on historical data and legal patterns</p>
          <div className="feature-action">Predict →</div>
        </div>

        <div className="feature-card">
          <div className="feature-icon">💼</div>
          <h3>Lawyer Network</h3>
          <p>Connect with verified lawyers specializing in your legal domain</p>
          <div className="feature-action">Find Lawyers →</div>
        </div>
      </div>
    </div>
  );

  // AI Chat Component
  const AIChat = () => {
    const [messages, setMessages] = useState([
      { role: 'assistant', content: 'Hello! I\'m your AI Legal Assistant. I can help you with legal questions, document analysis, case guidance, and more. What can I help you with today?' }
    ]);
    const [input, setInput] = useState('');

    const sendMessage = async () => {
      if (!input.trim() || !sessionId || isLoading) return;

      const userMessage = input;
      setInput('');
      setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
      setIsLoading(true);

      try {
        const response = await fetch(`${CHATBOT_API}/message`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: userMessage,
            session_id: sessionId,
            conversation_id: conversationId
          })
        });

        const data = await response.json();
        setMessages(prev => [...prev, { role: 'assistant', content: data.assistant_response }]);
      } catch (error) {
        setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' }]);
      } finally {
        setIsLoading(false);
      }
    };

    return (
      <div className="ai-chat">
        <div className="chat-header">
          <h2>AI Legal Assistant</h2>
          <div className="status-indicator">
            <div className="status-dot active"></div>
            <span>AI Online</span>
          </div>
        </div>
        
        <div className="chat-messages">
          {messages.map((msg, idx) => (
            <div key={idx} className={`message ${msg.role}`}>
              <div className="message-avatar">
                {msg.role === 'user' ? '👤' : '🤖'}
              </div>
              <div className="message-content">
                <div className="message-text">{msg.content}</div>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="message assistant">
              <div className="message-avatar">🤖</div>
              <div className="message-content">
                <div className="typing-indicator">
                  <span></span><span></span><span></span>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="chat-input">
          <div className="input-wrapper">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Ask any legal question..."
              disabled={isLoading}
            />
            <button onClick={sendMessage} disabled={isLoading || !input.trim()}>
              Send
            </button>
          </div>
        </div>
      </div>
    );
  };

  // Document Analyzer Component
  const DocumentAnalyzer = () => {
    const [analysis, setAnalysis] = useState(null);
    const [uploading, setUploading] = useState(false);

    const analyzeDocument = async (text) => {
      setUploading(true);
      try {
        const response = await fetch(`${CHATBOT_API}/message`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: `Please analyze this legal document and provide: 1) Summary 2) Key legal points 3) Potential risks 4) Recommendations. Document: ${text}`,
            session_id: sessionId,
            conversation_id: conversationId
          })
        });

        const data = await response.json();
        setAnalysis(data.assistant_response);
      } catch (error) {
        setAnalysis('Analysis failed. Please try again.');
      } finally {
        setUploading(false);
      }
    };

    const handleFileUpload = (event) => {
      const file = event.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
          analyzeDocument(e.target.result);
        };
        reader.readAsText(file);
      }
    };

    return (
      <div className="document-analyzer">
        <div className="analyzer-header">
          <h2>AI Document Analyzer</h2>
          <p>Upload legal documents for instant AI analysis</p>
        </div>

        <div className="upload-section">
          <div className="upload-area">
            <input
              type="file"
              onChange={handleFileUpload}
              accept=".txt,.pdf,.doc,.docx"
              disabled={uploading}
              id="file-upload"
              hidden
            />
            <label htmlFor="file-upload" className="upload-button">
              {uploading ? 'Analyzing...' : 'Upload Document'}
            </label>
            <p>Supported formats: TXT, PDF, DOC, DOCX</p>
          </div>
        </div>

        {analysis && (
          <div className="analysis-result">
            <h3>Analysis Result</h3>
            <div className="analysis-content">
              <pre>{analysis}</pre>
            </div>
          </div>
        )}
      </div>
    );
  };

  // Legal Generator Component
  const LegalGenerator = () => {
    const [docType, setDocType] = useState('petition');
    const [formData, setFormData] = useState({});
    const [generatedDoc, setGeneratedDoc] = useState('');
    const [generating, setGenerating] = useState(false);

    const generateDocument = async () => {
      setGenerating(true);
      const prompt = `Generate a professional ${docType} with the following details: ${JSON.stringify(formData)}`;
      
      try {
        const response = await fetch(`${CHATBOT_API}/message`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: prompt,
            session_id: sessionId,
            conversation_id: conversationId
          })
        });

        const data = await response.json();
        setGeneratedDoc(data.assistant_response);
      } catch (error) {
        setGeneratedDoc('Generation failed. Please try again.');
      } finally {
        setGenerating(false);
      }
    };

    return (
      <div className="legal-generator">
        <div className="generator-header">
          <h2>Legal Document Generator</h2>
          <p>Generate professional legal documents instantly</p>
        </div>

        <div className="generator-form">
          <div className="form-group">
            <label>Document Type</label>
            <select value={docType} onChange={(e) => setDocType(e.target.value)}>
              <option value="petition">Criminal Petition</option>
              <option value="bail">Bail Application</option>
              <option value="contract">Contract</option>
              <option value="notice">Legal Notice</option>
            </select>
          </div>

          <div className="form-group">
            <label>Case Details</label>
            <textarea
              placeholder="Describe your case details..."
              onChange={(e) => setFormData({...formData, details: e.target.value})}
            />
          </div>

          <button onClick={generateDocument} disabled={generating} className="generate-btn">
            {generating ? 'Generating...' : 'Generate Document'}
          </button>
        </div>

        {generatedDoc && (
          <div className="generated-document">
            <h3>Generated Document</h3>
            <div className="document-content">
              <pre>{generatedDoc}</pre>
            </div>
            <div className="document-actions">
              <button>Download PDF</button>
              <button>Download DOCX</button>
              <button>Email Document</button>
            </div>
          </div>
        )}
      </div>
    );
  };

  // Legal Research Component
  const LegalResearch = () => {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState(null);
    const [researching, setResearching] = useState(false);

    const performResearch = async () => {
      if (!query.trim()) return;
      
      setResearching(true);
      try {
        const response = await fetch(`${CHATBOT_API}/message`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: `Perform comprehensive legal research on: ${query}. Include: 1) Relevant laws 2) Case precedents 3) Legal principles 4) Recent developments`,
            session_id: sessionId,
            conversation_id: conversationId
          })
        });

        const data = await response.json();
        setResults(data.assistant_response);
      } catch (error) {
        setResults('Research failed. Please try again.');
      } finally {
        setResearching(false);
      }
    };

    return (
      <div className="legal-research">
        <div className="research-header">
          <h2>AI Legal Research</h2>
          <p>Comprehensive legal research powered by AI</p>
        </div>

        <div className="research-input">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter your research query..."
            onKeyPress={(e) => e.key === 'Enter' && performResearch()}
          />
          <button onClick={performResearch} disabled={researching}>
            {researching ? 'Researching...' : 'Research'}
          </button>
        </div>

        {results && (
          <div className="research-results">
            <h3>Research Results</h3>
            <div className="results-content">
              <pre>{results}</pre>
            </div>
          </div>
        )}
      </div>
    );
  };

  // Render current view
  const renderCurrentView = () => {
    switch (currentView) {
      case 'dashboard': return <Dashboard />;
      case 'chat': return <AIChat />;
      case 'analyzer': return <DocumentAnalyzer />;
      case 'generator': return <LegalGenerator />;
      case 'research': return <LegalResearch />;
      default: return <Dashboard />;
    }
  };

  return (
    <div className="app">
      <Navigation />
      <main className="main-content">
        {renderCurrentView()}
      </main>
    </div>
  );
}

export default App;