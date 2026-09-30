import React, { useState } from 'react';
import { Sparkles, Copy, Check, FileCheck } from 'lucide-react';
import * as diff from 'diff';

export default function DiffViewer({ originalCode, refactoredCode, explanation }) {
  const [copied, setCopied] = useState(false);
  const [viewMode, setViewMode] = useState('diff'); // diff or raw

  if (!refactoredCode) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(refactoredCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const diffResult = diff.diffLines(originalCode || '', refactoredCode || '');

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm mb-6">
      
      {/* Header Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-5 border-b border-slate-200 pb-4">
        <div className="flex items-center space-x-2">
          <Sparkles className="w-5 h-5 text-indigo-600" />
          <h3 className="text-lg font-bold text-slate-900">AI Refactored Code & Fix Suggestions</h3>
        </div>

        <div className="flex items-center space-x-3">
          <div className="flex items-center bg-slate-100 p-1 rounded-lg border border-slate-200">
            <button
              onClick={() => setViewMode('diff')}
              className={`px-3 py-1 text-xs font-medium rounded transition-all ${viewMode === 'diff' ? 'bg-indigo-600 text-white' : 'text-slate-600 hover:text-slate-900'}`}
            >
              Side-by-Side Diff
            </button>
            <button
              onClick={() => setViewMode('raw')}
              className={`px-3 py-1 text-xs font-medium rounded transition-all ${viewMode === 'raw' ? 'bg-indigo-600 text-white' : 'text-slate-600 hover:text-slate-900'}`}
            >
              Fixed Code Only
            </button>
          </div>

          <button
            onClick={handleCopy}
            className="bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-300 px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all"
          >
            {copied ? <Check className="w-4 h-4 text-emerald-600" /> : <Copy className="w-4 h-4" />}
            <span>{copied ? 'Copied!' : 'Copy Fixed Code'}</span>
          </button>
        </div>
      </div>

      {/* AI Explanation Box */}
      {explanation && (
        <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 mb-5">
          <h4 className="text-xs font-bold text-slate-600 uppercase tracking-wider mb-2 flex items-center gap-1.5">
            <FileCheck className="w-4 h-4 text-indigo-600" /> Executive Fix Rationale
          </h4>
          <div className="text-sm text-slate-800 leading-relaxed space-y-2 whitespace-pre-wrap font-sans">
            {explanation}
          </div>
        </div>
      )}

      {/* Code Comparison View */}
      {viewMode === 'diff' ? (
        <div className="bg-slate-900 border border-slate-800 rounded-lg overflow-x-auto code-font text-xs p-4 leading-relaxed max-h-[500px] overflow-y-auto">
          {diffResult.map((part, index) => {
            const color = part.added
              ? 'bg-emerald-500/20 text-emerald-300 border-l-4 border-emerald-500 font-semibold'
              : part.removed
              ? 'bg-red-500/20 text-red-300 border-l-4 border-red-500 opacity-80'
              : 'text-slate-300';
            const prefix = part.added ? '+ ' : part.removed ? '- ' : '  ';
            
            return (
              <div key={index} className={`px-2 py-0.5 whitespace-pre-wrap ${color}`}>
                {part.value.split('\n').map((line, lIdx) => (
                  line ? <div key={lIdx}>{prefix}{line}</div> : null
                ))}
              </div>
            );
          })}
        </div>
      ) : (
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-4 code-font text-xs text-emerald-300 leading-relaxed overflow-x-auto max-h-[500px] overflow-y-auto whitespace-pre">
          {refactoredCode}
        </div>
      )}

    </div>
  );
}
