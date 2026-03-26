import React from 'react';
import { Play } from 'lucide-react';

interface RunButtonProps {
  filePath: string;
  fileContent: string;
  language: string;
  onRun: (command: string) => void;
}

export const RunButton: React.FC<RunButtonProps> = ({ filePath, fileContent, language, onRun }) => {
  const getRunCommand = () => {
    const fileName = filePath.split('/').pop();
    
    switch (language) {
      case 'python':
        return `python3 ${filePath}`;
      case 'javascript':
        return `node ${filePath}`;
      case 'typescript':
        return `ts-node ${filePath}`;
      case 'html':
        return `open ${filePath}`;
      case 'go':
        return `go run ${filePath}`;
      case 'rust':
        return `cargo run --bin ${fileName?.replace('.rs', '')}`;
      case 'cpp':
      case 'c':
        return `gcc ${filePath} -o out && ./out`;
      default:
        return null;
    }
  };

  const runCommand = getRunCommand();
  
  if (!runCommand) return null;

  return (
    <button
      onClick={() => onRun(runCommand)}
      className="flex items-center gap-2 px-3 py-1 bg-vs-blue hover:bg-vs-blue-light text-white text-sm rounded transition-colors"
      title={`Run ${language} file`}
    >
      <Play size={14} />
      <span>Run</span>
    </button>
  );
};