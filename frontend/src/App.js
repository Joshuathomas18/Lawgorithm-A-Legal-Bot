import React, { useState, useRef, useEffect } from 'react';
import styled, { createGlobalStyle } from 'styled-components';

const API_BASE = 'http://localhost:8001/api/v1';
const CHATBOT_API = 'http://localhost:8001/api/v1/chatbot';

// Debug logging
console.log('Environment variables check:');
console.log('REACT_APP_BACKEND_URL:', process.env.REACT_APP_BACKEND_URL);
console.log('API_BASE:', API_BASE);
console.log('CHATBOT_API:', CHATBOT_API);

// Add debug alert to see if this runs in browser

const GlobalStyle = createGlobalStyle`
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&family=Poppins:wght@400;600;700&display=swap');
  body {
    background: #171712;
    margin: 0;
    font-family: 'Poppins', 'Inter', Arial, sans-serif;
    color: #fff;
  }
`;

const Container = styled.div`
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  background: #171712;
`;

const Header = styled.header`
  width: 100vw;
  max-width: 100vw;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 40px;
  height: 65px;
  background: transparent;
  position: relative;
`;

const LogoSection = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
`;

const LogoIcon = styled.div`
  width: 28px;
  height: 28px;
  background: linear-gradient(135deg, #fff 60%, #EDC70A 100%);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
`;

const LogoText = styled.div`
  font-family: 'Poppins', 'Inter', Arial, sans-serif;
  font-weight: 700;
  font-size: 22px;
  color: #fff;
  letter-spacing: 0.5px;
`;

const NavSection = styled.div`
  display: flex;
  align-items: center;
  gap: 24px;
`;

const NavLink = styled.div`
  font-family: 'Poppins', 'Inter', Arial, sans-serif;
  font-weight: 500;
  font-size: 15px;
  color: #fff;
  opacity: 0.85;
  cursor: pointer;
  transition: opacity 0.2s;
  &:hover { opacity: 1; }
`;

const InfoButton = styled.div`
  width: 36px;
  height: 36px;
  background: #23231a;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 700;
  color: #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.12);
  cursor: pointer;
  border: 1.5px solid #fff;
`;

const Divider = styled.div`
  width: 100vw;
  height: 1.5px;
  background: #fff;
  opacity: 0.12;
  margin-bottom: 32px;
`;

const Main = styled.main`
  flex: 1;
  width: 100vw;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
`;

const ChatBoxWrapper = styled.div`
  background: #23231a;
  border-radius: 24px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.18);
  width: 420px;
  max-width: 95vw;
  min-height: 420px;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  padding: 32px 28px 20px 28px;
  margin: 0 auto;
`;

const ChatTitle = styled.div`
  font-family: 'Poppins', 'Inter', Arial, sans-serif;
  font-size: 24px;
  font-weight: 700;
  text-align: center;
  margin-bottom: 8px;
`;

const ChatDesc = styled.div`
  font-size: 15px;
  font-weight: 400;
  text-align: center;
  color: #e6e6e6;
  margin-bottom: 18px;
`;

const ChatMessages = styled.div`
  flex: 1;
  min-height: 120px;
  max-height: 220px;
  overflow-y: auto;
  margin-bottom: 18px;
  padding-right: 4px;
`;

const Message = styled.div`
  background: ${props => props.user ? '#EDC70A' : '#383629'};
  color: ${props => props.user ? '#171712' : '#fff'};
  align-self: ${props => props.user ? 'flex-end' : 'flex-start'};
  border-radius: 16px;
  padding: 10px 16px;
  margin-bottom: 8px;
  max-width: 80%;
  font-size: 15px;
  font-family: 'Poppins', 'Inter', Arial, sans-serif;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
`;

const UploadRow = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
`;

const UploadLabel = styled.label`
  background: #383629;
  color: #fff;
  border-radius: 16px;
  padding: 6px 14px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
  &:hover { background: #2a2a1e; }
`;

const HiddenInput = styled.input`
  display: none;
`;

const ChatInputRow = styled.form`
  display: flex;
  align-items: center;
  background: #191914;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.18);
  padding: 0 12px;
  margin-top: 8px;
`;

const ChatInput = styled.input`
  flex: 1;
  border: none;
  background: transparent;
  color: #fff;
  font-size: 15px;
  font-family: 'Poppins', 'Inter', Arial, sans-serif;
  padding: 14px 0;
  outline: none;
  &::placeholder {
    color: #bdbdbd;
    font-style: italic;
    opacity: 0.8;
  }
`;

const SendButton = styled.button`
  background: #EDC70A;
  color: #171712;
  border: none;
  border-radius: 12px;
  font-weight: 700;
  font-size: 15px;
  padding: 8px 18px;
  margin-left: 8px;
  cursor: pointer;
  transition: background 0.2s;
  &:hover { background: #ffe066; }
`;

const SaveRow = styled.div`
  display: flex;
  flex-direction: row;
  gap: 16px;
  justify-content: center;
  margin-top: 24px;
`;

const SaveButton = styled.button`
  background: #383629;
  color: #fff;
  border: none;
  border-radius: 20px;
  font-family: 'Poppins', 'Inter', Arial, sans-serif;
  font-weight: 700;
  font-size: 15px;
  padding: 12px 28px;
  cursor: pointer;
  transition: background 0.2s;
  &:hover { background: #23231a; }
`;

function App() {
  const [messages, setMessages] = useState([
    { user: false, text: "I'm here to help you navigate the legal process. Let's start by understanding your case. What type of case are you dealing with?" }
  ]);
  const [input, setInput] = useState("");
  const [showSave, setShowSave] = useState(false);
  const [uploads, setUploads] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const [conversationId, setConversationId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [debugInfo, setDebugInfo] = useState('Initializing...');
  const fileInputRef = useRef();

  // Start conversation on mount
  useEffect(() => {
    const startConversation = async () => {
      try {
        setDebugInfo('Attempting to connect to backend...');
        console.log('Attempting API call to:', `${API_BASE}/conversations/start`);
        
        const res = await fetch(`${API_BASE}/conversations/start`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ user_id: 'frontend-user', initial_message: messages[0].text })
        });
        
        console.log('Response status:', res.status);
        const data = await res.json();
        console.log('Response data:', data);
        
        setSessionId(data.session_id);
        setConversationId(data.conversation_id);
        
        if (!data.session_id || !data.conversation_id) {
          setDebugInfo('❌ Failed to initialize conversation. Backend may be down.');
          alert('Failed to initialize conversation. Backend may be down or misconfigured.');
        } else {
          setDebugInfo('✅ Connected to backend successfully!');
        }
      } catch (err) {
        console.error('Connection error:', err);
        setDebugInfo('❌ Connection error: ' + err.toString());
        alert('Error connecting to backend: ' + err);
      }
    };
    startConversation();
    // eslint-disable-next-line
  }, []);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) {
      alert('Please enter a message.');
      return;
    }
    if (!conversationId || !sessionId) {
      alert('Conversation not initialized. Please refresh or check backend.');
      return;
    }
    const messageToSend = input;
    setMessages(prev => [...prev, { user: true, text: messageToSend }]);
    setInput("");
    setLoading(true);
    try {
      const res = await fetch(`${CHATBOT_API}/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          conversation_id: conversationId,
          session_id: sessionId,
          message: messageToSend
        })
      });
      const data = await res.json();
      if (data.assistant_response) {
        setMessages(prev => [...prev, { user: false, text: data.assistant_response }]);
        if (/happy|done|final/i.test(messageToSend)) {
          setTimeout(() => setShowSave(true), 500);
        }
      } else {
        setMessages(prev => [...prev, { user: false, text: 'Sorry, there was an error getting a response.' }]);
        console.error('Backend error:', data);
      }
    } catch (err) {
      setMessages(prev => [...prev, { user: false, text: 'Sorry, there was a network error.' }]);
      console.error('Network error:', err);
    }
    setLoading(false);
  };

  const handleUpload = (e) => {
    const files = Array.from(e.target.files);
    setUploads([...uploads, ...files]);
    files.forEach(file => {
      setMessages(msgs => [...msgs, { user: true, text: `Uploaded: ${file.name}` }]);
    });
  };

  return (
    <>
      <GlobalStyle />
      <Container>
        <Header>
          <LogoSection>
            <LogoIcon>
              <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="9" cy="9" r="8" fill="#fff" stroke="#EDC70A" strokeWidth="2" />
                <text x="9" y="13" textAnchor="middle" fontSize="10" fontWeight="bold" fill="#EDC70A">L</text>
              </svg>
            </LogoIcon>
            <LogoText>Lawgorithm</LogoText>
          </LogoSection>
          <NavSection>
            <NavLink>Terms & Conditions</NavLink>
            <InfoButton title="Info">i</InfoButton>
          </NavSection>
        </Header>
        <Divider />
        <Main>
          <ChatBoxWrapper>
            <ChatTitle>Welcome to Lawgorithm</ChatTitle>
            <ChatDesc>I'm here to help you navigate the legal process. Let's start by understanding your case. What type of case are you dealing with?</ChatDesc>
            <div style={{fontSize:'12px', color:'#EDC70A', marginBottom:'10px', padding:'8px', background:'#333', borderRadius:'8px'}}>
              Debug: {debugInfo} | Backend: http://localhost:8001/api | Session: {sessionId ? '✅' : '❌'}
            </div>
            <ChatMessages>
              {messages.map((msg, idx) => (
                <Message key={idx} user={msg.user}>{msg.text}</Message>
              ))}
              {loading && <Message user={false}>Thinking...</Message>}
            </ChatMessages>
            <UploadRow>
              <UploadLabel htmlFor="file-upload">+ Add Image/Doc
                <HiddenInput id="file-upload" type="file" multiple ref={fileInputRef} onChange={handleUpload} accept="image/*,.pdf,.doc,.docx,.txt" />
              </UploadLabel>
              {uploads.length > 0 && <span style={{fontSize:'13px',color:'#EDC70A'}}>{uploads.length} file(s) uploaded</span>}
            </UploadRow>
            <ChatInputRow onSubmit={handleSend}>
              <ChatInput
                type="text"
                placeholder="Enter your text here..."
                value={input}
                onChange={e => setInput(e.target.value)}
                disabled={loading}
              />
              <SendButton type="submit" disabled={loading || !input.trim()}>Send</SendButton>
            </ChatInputRow>
            {showSave && (
              <SaveRow>
                <SaveButton>Save as PDF</SaveButton>
                <SaveButton>Save as DOCX</SaveButton>
              </SaveRow>
            )}
          </ChatBoxWrapper>
        </Main>
      </Container>
    </>
  );
}

export default App;
