import React from 'react';
import { ShieldAlert, Sparkles, History, Code2 } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, onSelectSample }) {
  return (
    <header className="bg-white/90 backdrop-blur border-b border-slate-200 sticky top-0 z-50 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Logo & Title */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-600 flex items-center justify-center shadow-md shadow-indigo-600/20">
              <ShieldAlert className="w-6 h-6 text-white" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-lg text-slate-900 tracking-tight">CodeSentinel</span>
                <span className="px-2 py-0.5 text-xs font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200 rounded-full">
                  Light PRO
                </span>
              </div>
              <p className="text-xs text-slate-500">AI Code Review & Security Audit Platform</p>
            </div>
          </div>

          {/* Preset Sample Quick Load Buttons */}
          <div className="hidden lg:flex items-center space-x-2 bg-slate-100 p-1.5 rounded-lg border border-slate-200">
            <span className="text-xs text-slate-600 px-2 flex items-center gap-1 font-medium">
              <Sparkles className="w-3.5 h-3.5 text-amber-500" /> Samples:
            </span>
            <button
              onClick={() => onSelectSample('vulnerable')}
              className="px-2.5 py-1 text-xs font-medium bg-red-50 hover:bg-red-100 text-red-700 border border-red-200 rounded transition-all"
            >
              SQLi & Secrets
            </button>
            <button
              onClick={() => onSelectSample('complex')}
              className="px-2.5 py-1 text-xs font-medium bg-amber-50 hover:bg-amber-100 text-amber-700 border border-amber-200 rounded transition-all"
            >
              High Complexity
            </button>
            <button
              onClick={() => onSelectSample('jsbug')}
              className="px-2.5 py-1 text-xs font-medium bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200 rounded transition-all"
            >
              Async JS Bug
            </button>
          </div>

          {/* Navigation Tabs */}
          <nav className="flex items-center space-x-2">
            <button
              onClick={() => setActiveTab('editor')}
              className={`flex items-center space-x-2 px-3.5 py-2 rounded-lg text-sm font-medium transition-all ${
                activeTab === 'editor'
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/20'
                  : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
              }`}
            >
              <Code2 className="w-4 h-4" />
              <span>Analyzer</span>
            </button>

            <button
              onClick={() => setActiveTab('history')}
              className={`flex items-center space-x-2 px-3.5 py-2 rounded-lg text-sm font-medium transition-all ${
                activeTab === 'history'
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/20'
                  : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
              }`}
            >
              <History className="w-4 h-4" />
              <span>Audit History</span>
            </button>
          </nav>

        </div>
      </div>
    </header>
  );
}
