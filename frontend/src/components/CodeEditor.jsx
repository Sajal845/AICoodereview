import React, { useState } from 'react';
import { Play, Upload, FileCode2, Sparkles, Loader2 } from 'lucide-react';

export default function CodeEditor({ code, setCode, filename, setFilename, language, setLanguage, llmProvider, setLlmProvider, onAnalyze, loading }) {
  const [dragActive, setDragActive] = useState(false);

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setFilename(file.name);
      const ext = file.name.split('.').pop().toLowerCase();
      const langMap = {
        py: 'python', js: 'javascript', ts: 'typescript',
        cpp: 'cpp', c: 'c', java: 'java', go: 'go', rs: 'rust', html: 'html', css: 'css'
      };
      if (langMap[ext]) setLanguage(langMap[ext]);
      
      const reader = new FileReader();
      reader.onload = (event) => setCode(event.target.result);
      reader.readAsText(file);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      setFilename(file.name);
      const reader = new FileReader();
      reader.onload = (event) => setCode(event.target.result);
      reader.readAsText(file);
    }
  };

  return (
    <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden mb-6">
      
      {/* Editor Controls Bar */}
      <div className="bg-slate-50 px-4 py-3 border-b border-slate-200 flex flex-wrap items-center justify-between gap-3">
        
        <div className="flex items-center space-x-3">
          <FileCode2 className="w-5 h-5 text-indigo-600" />
          <input
            type="text"
            value={filename}
            onChange={(e) => setFilename(e.target.value)}
            className="bg-white text-sm text-slate-900 px-3 py-1.5 rounded border border-slate-300 focus:outline-none focus:border-indigo-600 w-44 font-mono"
            placeholder="filename.py"
          />
          
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="bg-white text-sm text-slate-700 px-3 py-1.5 rounded border border-slate-300 focus:outline-none focus:border-indigo-600 capitalize"
          >
            <option value="python">Python</option>
            <option value="javascript">JavaScript</option>
            <option value="typescript">TypeScript</option>
            <option value="cpp">C++</option>
            <option value="java">Java</option>
            <option value="go">Go</option>
            <option value="rust">Rust</option>
          </select>
        </div>

        <div className="flex items-center space-x-3">
          {/* LLM Engine Selection */}
          <div className="flex items-center space-x-1.5 bg-white px-2.5 py-1 rounded border border-slate-300">
            <Sparkles className="w-3.5 h-3.5 text-amber-500" />
            <span className="text-xs text-slate-500 font-medium">Model:</span>
            <select
              value={llmProvider}
              onChange={(e) => setLlmProvider(e.target.value)}
              className="bg-transparent text-xs text-slate-800 focus:outline-none font-medium cursor-pointer"
            >
              <option value="auto">Auto / Smart Engine</option>
              <option value="openai">OpenAI (GPT-4o)</option>
              <option value="gemini">Google Gemini</option>
              <option value="ollama">Local Ollama</option>
              <option value="fallback">Heuristic Rules</option>
            </select>
          </div>

          {/* Upload Button */}
          <label className="cursor-pointer bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-medium px-3 py-1.5 rounded border border-slate-300 flex items-center gap-1.5 transition-all">
            <Upload className="w-3.5 h-3.5" />
            <span>Upload File</span>
            <input type="file" onChange={handleFileUpload} className="hidden" />
          </label>

          {/* Analyze Trigger */}
          <button
            onClick={onAnalyze}
            disabled={loading || !code.trim()}
            className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-sm px-4 py-1.5 rounded-lg shadow-sm flex items-center gap-2 transition-all disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin text-white" />
                <span>Analyzing Code...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-white" />
                <span>Run AI Review</span>
              </>
            )}
          </button>
        </div>

      </div>

      {/* Code Text Area */}
      <div 
        className={`relative ${dragActive ? 'border-2 border-dashed border-indigo-500 bg-indigo-50' : ''}`}
        onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
        onDragLeave={() => setDragActive(false)}
        onDrop={handleDrop}
      >
        <textarea
          value={code}
          onChange={(e) => setCode(e.target.value)}
          placeholder="// Paste or drag-and-drop source code here for AST, security vulnerability, and AI analysis..."
          rows={14}
          spellCheck="false"
          className="w-full bg-slate-50 text-slate-900 p-4 code-font text-sm leading-relaxed border-none focus:outline-none resize-y"
        />
        
        {/* Lines counter */}
        <div className="absolute bottom-3 right-4 text-xs text-slate-400 font-mono pointer-events-none">
          {code.split('\n').length} lines | {code.length} chars
        </div>
      </div>

    </div>
  );
}
