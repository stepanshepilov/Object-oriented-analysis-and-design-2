import React from 'react';
import { FILE_ICONS, LANGUAGE_EXTENSIONS } from '../../utils/constants';

interface FileIconProps {
  fileName: string;
}

export const FileIcon: React.FC<FileIconProps> = ({ fileName }) => {
  const ext = fileName.substring(fileName.lastIndexOf('.'));
  const language = LANGUAGE_EXTENSIONS[ext] || 'default';
  const icon = FILE_ICONS[language] || FILE_ICONS.default;
  
  return <span className="text-sm">{icon}</span>;
};