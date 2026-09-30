import React, { useState } from 'react';
import { ShieldAlert, Bug, Cpu, AlertTriangle, CheckCircle2, CornerDownRight } from 'lucide-react';

export default function IssuesList({ issues }) {
  const [filterType, setFilterType] = useState('all');

  if (!issues || issues.length === 0) {
    return (
      <div className="bg-white border border-slate-200 rounded-xl p-8 text-center shadow-sm mb-6">
        <CheckCircle2 className="w-12 h-12 text-emerald-600 mx-auto mb-3" />
        <h3 className="text-lg font-bold text-slate-900 mb-1">Zero Issues Detected!</h3>
        <p className="text-sm text-slate-600">Your code passed all static security checks, AST analysis, and complexity rules.</p>
      </div>
    );
  }

  const getSeverityBadge = (severity) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return <span className="px-2.5 py-0.5 text-xs font-bold bg-red-50 text-red-700 border border-red-200 rounded uppercase">Critical</span>;
      case 'high':
        return <span className="px-2.5 py-0.5 text-xs font-bold bg-orange-50 text-orange-700 border border-orange-200 rounded uppercase">High</span>;
      case 'medium':
        return <span className="px-2.5 py-0.5 text-xs font-bold bg-amber-50 text-amber-700 border border-amber-200 rounded uppercase">Medium</span>;
      default:
        return <span className="px-2.5 py-0.5 text-xs font-bold bg-indigo-50 text-indigo-700 border border-indigo-200 rounded uppercase">Low</span>;
    }
  };

  const getIssueIcon = (type) => {
    switch (type.toLowerCase()) {
      case 'security':
        return <ShieldAlert className="w-5 h-5 text-red-600" />;
      case 'bug':
        return <Bug className="w-5 h-5 text-orange-600" />;
      case 'complexity':
        return <Cpu className="w-5 h-5 text-amber-600" />;
      default:
        return <AlertTriangle className="w-5 h-5 text-indigo-600" />;
    }
  };

  const filteredIssues = filterType === 'all'
    ? issues
    : issues.filter(i => i.type.toLowerCase() === filterType.toLowerCase());

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm mb-6">
      
      {/* Header & Category Filters */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-5 border-b border-slate-200 pb-4">
        <div className="flex items-center space-x-2">
          <ShieldAlert className="w-5 h-5 text-red-600" />
          <h3 className="text-lg font-bold text-slate-900">Security & Code Defects ({issues.length})</h3>
        </div>

        <div className="flex items-center space-x-1.5 bg-slate-100 p-1 rounded-lg border border-slate-200">
          <button
            onClick={() => setFilterType('all')}
            className={`px-3 py-1 text-xs font-medium rounded transition-all ${filterType === 'all' ? 'bg-indigo-600 text-white' : 'text-slate-600 hover:text-slate-900'}`}
          >
            All ({issues.length})
          </button>
          <button
            onClick={() => setFilterType('security')}
            className={`px-3 py-1 text-xs font-medium rounded transition-all ${filterType === 'security' ? 'bg-red-600 text-white' : 'text-slate-600 hover:text-slate-900'}`}
          >
            Security ({issues.filter(i => i.type === 'security').length})
          </button>
          <button
            onClick={() => setFilterType('complexity')}
            className={`px-3 py-1 text-xs font-medium rounded transition-all ${filterType === 'complexity' ? 'bg-amber-600 text-white' : 'text-slate-600 hover:text-slate-900'}`}
          >
            Complexity ({issues.filter(i => i.type === 'complexity').length})
          </button>
          <button
            onClick={() => setFilterType('smell')}
            className={`px-3 py-1 text-xs font-medium rounded transition-all ${filterType === 'smell' ? 'bg-indigo-600 text-white' : 'text-slate-600 hover:text-slate-900'}`}
          >
            Code Smells ({issues.filter(i => i.type === 'smell' || i.type === 'bug').length})
          </button>
        </div>
      </div>

      {/* Issues List */}
      <div className="space-y-3">
        {filteredIssues.map((issue, idx) => (
          <div 
            key={idx} 
            className="bg-slate-50 border border-slate-200 rounded-lg p-4 hover:border-slate-300 transition-all"
          >
            <div className="flex items-start justify-between gap-3 mb-2">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-white rounded-lg border border-slate-200 shadow-sm">
                  {getIssueIcon(issue.type)}
                </div>
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="font-bold text-slate-900 text-base">{issue.title}</span>
                    <span className="text-xs text-slate-600 font-mono bg-white px-2 py-0.5 rounded border border-slate-200">
                      Line {issue.line}
                    </span>
                    {issue.rule_id && (
                      <span className="text-xs font-mono text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-200">
                        {issue.rule_id}
                      </span>
                    )}
                    {issue.cwe && (
                      <span className="text-xs font-mono text-purple-700 bg-purple-50 px-2 py-0.5 rounded border border-purple-200">
                        {issue.cwe}
                      </span>
                    )}
                  </div>
                </div>
              </div>

              <div>{getSeverityBadge(issue.severity)}</div>
            </div>

            <p className="text-sm text-slate-700 ml-12 mb-3 leading-relaxed">
              {issue.description}
            </p>

            {issue.suggestion && (
              <div className="ml-12 bg-white border-l-4 border-indigo-600 p-3 rounded-r-lg text-xs text-slate-800 shadow-sm flex items-start gap-2">
                <CornerDownRight className="w-4 h-4 text-indigo-600 shrink-0 mt-0.5" />
                <div>
                  <span className="font-semibold text-indigo-700 block mb-0.5">Suggested Fix:</span>
                  <span>{issue.suggestion}</span>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

    </div>
  );
}
