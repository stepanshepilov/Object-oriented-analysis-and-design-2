import React, { useEffect, useRef, useState, forwardRef, useImperativeHandle } from 'react';
import { TerminalService } from '../../services/terminal';
import { X, Minimize2, Plus } from 'lucide-react';

export interface TerminalHandle {
  executeCode: (command: string) => void;
}

interface TerminalProps {
  sessionId: string;
}

export const Terminal = forwardRef<TerminalHandle, TerminalProps>(({ sessionId }, ref) => {
  const [terminals, setTerminals] = useState<Map<string, TerminalService>>(new Map());
  const [activeTerminal, setActiveTerminal] = useState<string>('');
  const [output, setOutput] = useState<Map<string, string[]>>(new Map());
  const inputRef = useRef<HTMLInputElement>(null);
  const outputRef = useRef<HTMLDivElement>(null);

  // Функция для выполнения кода в активном терминале
  const executeCode = (command: string) => {
    const terminal = terminals.get(activeTerminal);
    if (terminal && command) {
      terminal.executeCommand(command);
      setOutput(prev => {
        const newOutput = new Map(prev);
        const currentOutput = newOutput.get(activeTerminal) || [];
        newOutput.set(activeTerminal, [...currentOutput, `$ ${command}\n`]);
        return newOutput;
      });
    }
  };

  // Экспортируем функцию executeCode через ref
  useImperativeHandle(ref, () => ({
    executeCode
  }));

  useEffect(() => {
    if (sessionId) {
      createNewTerminal();
    }
    
    return () => {
      terminals.forEach(term => term.disconnect());
    };
  }, [sessionId]);

  useEffect(() => {
    if (outputRef.current) {
      outputRef.current.scrollTop = outputRef.current.scrollHeight;
    }
  }, [output]);

  const createNewTerminal = () => {
    const terminalId = `term_${Date.now()}`;
    const terminal = new TerminalService();
    terminal.connect(sessionId, terminalId);
    
    terminal.onOutput((data) => {
      setOutput(prev => {
        const newOutput = new Map(prev);
        const currentOutput = newOutput.get(terminalId) || [];
        newOutput.set(terminalId, [...currentOutput, data]);
        return newOutput;
      });
    });
    
    setTerminals(prev => new Map(prev).set(terminalId, terminal));
    setActiveTerminal(terminalId);
    setOutput(prev => new Map(prev).set(terminalId, []));
  };

  const handleCommand = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && inputRef.current) {
      const command = inputRef.current.value;
      if (command.trim()) {
        executeCode(command);
      }
      inputRef.current.value = '';
    }
  };

  const closeTerminal = (terminalId: string) => {
    const terminal = terminals.get(terminalId);
    if (terminal) {
      terminal.disconnect();
    }
    setTerminals(prev => {
      const newTerminals = new Map(prev);
      newTerminals.delete(terminalId);
      return newTerminals;
    });
    setOutput(prev => {
      const newOutput = new Map(prev);
      newOutput.delete(terminalId);
      return newOutput;
    });
    
    if (activeTerminal === terminalId && terminals.size > 1) {
      const firstTerminal = Array.from(terminals.keys())[0];
      setActiveTerminal(firstTerminal);
    }
  };

  return (
    <div className="h-64 bg-vs-black border-t border-vs-gray flex flex-col">
      <div className="h-8 bg-vs-gray-dark flex items-center px-2 gap-2">
        {Array.from(terminals.entries()).map(([id]) => (
          <button
            key={id}
            onClick={() => setActiveTerminal(id)}
            className={`px-3 py-1 text-xs rounded flex items-center gap-2 ${
              activeTerminal === id
                ? 'bg-vs-blue text-white'
                : 'text-vs-text hover:bg-vs-gray'
            }`}
          >
            <span>Terminal {id.slice(-4)}</span>
            <X
              size={12}
              onClick={(e) => {
                e.stopPropagation();
                closeTerminal(id);
              }}
              className="hover:text-red-400"
            />
          </button>
        ))}
        <button
          onClick={createNewTerminal}
          className="p-1 hover:bg-vs-gray rounded"
        >
          <Plus size={14} className="text-vs-text" />
        </button>
        <div className="flex-1" />
        <button className="p-1 hover:bg-vs-gray rounded">
          <Minimize2 size={14} className="text-vs-text" />
        </button>
      </div>
      
      <div
        ref={outputRef}
        className="flex-1 overflow-y-auto p-2 font-mono text-xs"
        style={{ fontFamily: 'Fira Code, monospace' }}
      >
        {output.get(activeTerminal)?.map((line, i) => (
          <div key={i} className="text-vs-text whitespace-pre-wrap">
            {line}
          </div>
        ))}
        <div className="flex items-center gap-2 mt-1">
          <span className="text-vs-blue">$</span>
          <input
            ref={inputRef}
            type="text"
            onKeyDown={handleCommand}
            className="flex-1 bg-transparent outline-none text-vs-text font-mono text-xs"
            placeholder="Type command..."
            autoFocus
          />
        </div>
      </div>
    </div>
  );
});

Terminal.displayName = 'Terminal';