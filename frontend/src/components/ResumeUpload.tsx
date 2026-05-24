import React, { useCallback, useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface Props {
  onUpload: (file: File, keywords?: string) => void;
  disabled?: boolean;
}

export default function ResumeUpload({ onUpload, disabled }: Props) {
  const [dragOver, setDragOver] = useState(false);
  const [keywords, setKeywords] = useState('');
  const [fileName, setFileName] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);
  const selectedFile = useRef<File | null>(null);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDragIn = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  }, []);

  const handleDragOut = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const files = e.dataTransfer.files;
    if (files?.[0]?.type === 'application/pdf') {
      selectedFile.current = files[0];
      setFileName(files[0].name);
    }
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) {
      selectedFile.current = f;
      setFileName(f.name);
    }
  };

  const handleSubmit = () => {
    if (selectedFile.current) {
      onUpload(selectedFile.current, keywords || undefined);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: 'easeOut' }}
      className="max-w-2xl mx-auto"
    >
      {/* Upload Zone */}
      <div
        className={`upload-zone ${dragOver ? 'drag-over' : ''}`}
        onDragEnter={handleDragIn}
        onDragLeave={handleDragOut}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileRef.current?.click()}
      >
        <input
          ref={fileRef}
          type="file"
          accept=".pdf"
          className="hidden"
          onChange={handleFileSelect}
          id="resume-upload-input"
        />

        <AnimatePresence mode="wait">
          {fileName ? (
            <motion.div
              key="selected"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="space-y-3"
            >
              <div className="w-16 h-16 mx-auto rounded-2xl bg-neon-500/10 flex items-center justify-center">
                <svg className="w-8 h-8 text-neon-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <p className="text-lg font-medium text-neon-400">{fileName}</p>
              <p className="text-sm text-slate-400">Click to change file</p>
            </motion.div>
          ) : (
            <motion.div
              key="empty"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="space-y-4"
            >
              <div className="w-20 h-20 mx-auto rounded-2xl bg-electric-500/10 flex items-center justify-center animate-float">
                <svg className="w-10 h-10 text-electric-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m3.75 9v6m3-3H9m1.5-12H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
                </svg>
              </div>
              <div>
                <p className="text-lg font-semibold text-slate-200">Drop your resume PDF here</p>
                <p className="text-sm text-slate-400 mt-1">or click to browse • PDF only, max 10MB</p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Target Keywords */}
      <div className="mt-6 space-y-3">
        <label htmlFor="keywords-input" className="block text-sm font-medium text-slate-300">
          Target Job Keywords <span className="text-slate-500">(optional)</span>
        </label>
        <input
          id="keywords-input"
          type="text"
          value={keywords}
          onChange={(e) => setKeywords(e.target.value)}
          placeholder="e.g., React, TypeScript, Node.js, AWS"
          className="w-full px-4 py-3 rounded-xl bg-navy-800/80 border border-white/[0.06] text-slate-200 placeholder-slate-500 focus:outline-none focus:border-electric-500/50 focus:ring-1 focus:ring-electric-500/20 transition-all"
        />
      </div>

      {/* Submit Button */}
      <motion.button
        id="analyze-button"
        onClick={handleSubmit}
        disabled={!fileName || disabled}
        className={`w-full mt-6 btn-primary text-lg py-4 ${
          !fileName || disabled ? 'opacity-40 cursor-not-allowed' : ''
        }`}
        whileHover={fileName && !disabled ? { scale: 1.02 } : {}}
        whileTap={fileName && !disabled ? { scale: 0.98 } : {}}
      >
        {disabled ? 'Analyzing...' : '✦ Analyze Resume'}
      </motion.button>
    </motion.div>
  );
}
