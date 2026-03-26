import { useState, useEffect, useRef } from 'react';
import { ActivityBar } from './components/Layout/ActivityBar';
import { Sidebar } from './components/Layout/Sidebar';
import { TabBar } from './components/Layout/TabBar';
import { StatusBar } from './components/Layout/StatusBar';
import { EditorGroup } from './components/Editor/EditorGroup';
import { Terminal, type TerminalHandle } from './components/Terminal/Terminal';
import { api } from './services/api';
import { wsService } from './services/websocket';

function App() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [activeView, setActiveView] = useState('explorer');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const terminalRef = useRef<TerminalHandle>(null);

  useEffect(() => {
    initSession();
    
    return () => {
      if (sessionId) {
        wsService.disconnect();
      }
    };
  }, []);

  const initSession = async () => {
    try {
      console.log('Creating session...');
      const session = await api.createSession();
      console.log('Session created:', session);
      
      setSessionId(session.session_id);
      
      console.log('Connecting WebSocket for session:', session.session_id);
      wsService.connect(session.session_id);
      
    } catch (error) {
      console.error('Failed to create session:', error);
      setError('Failed to initialize session. Make sure backend is running on port 8000');
    } finally {
      setLoading(false);
    }
  };

  const handleRunCommand = (command: string) => {
    console.log('Run command:', command);
    if (terminalRef.current) {
      terminalRef.current.executeCode(command);
    }
  };

  if (loading) {
    return (
      <div className="h-screen bg-vs-black flex items-center justify-center">
        <div className="text-vs-blue text-xl animate-pulse">
          Loading IDE...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="h-screen bg-vs-black flex items-center justify-center">
        <div className="text-red-500 text-xl text-center">
          <p>{error}</p>
          <p className="text-sm mt-4 text-vs-text">
            Make sure backend is running: <code className="bg-vs-gray px-2 py-1 rounded">uvicorn app.main:app --reload --port 8000</code>
          </p>
        </div>
      </div>
    );
  }

  if (!sessionId) {
    return (
      <div className="h-screen bg-vs-black flex items-center justify-center">
        <div className="text-red-500 text-xl">
          Failed to create session
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col bg-vs-black">
      <div className="flex-1 flex overflow-hidden">
        <ActivityBar activeView={activeView} onViewChange={setActiveView} />
        <Sidebar activeView={activeView} sessionId={sessionId} />
        <div className="flex-1 flex flex-col overflow-hidden">
          <TabBar />
          <EditorGroup 
            sessionId={sessionId} 
            onRunCommand={handleRunCommand}
            terminalRef={terminalRef}
          />
        </div>
      </div>
      <Terminal ref={terminalRef} sessionId={sessionId} />
      <StatusBar sessionId={sessionId} />
    </div>
  );
}

export default App;