import React from 'react';
import { ShieldCheck, ShieldAlert, Cpu, Activity, CheckCircle2, AlertTriangle } from 'lucide-react';

export default function MetricsCard({ metrics }) {
  if (!metrics) return null;

  const getRiskBadge = (level) => {
    switch (level) {
      case 'LOW RISK':
        return <span className="px-3 py-1 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-full font-bold text-xs flex items-center gap-1.5"><CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" /> LOW RISK</span>;
      case 'MODERATE RISK':
        return <span className="px-3 py-1 bg-amber-50 text-amber-700 border border-amber-200 rounded-full font-bold text-xs flex items-center gap-1.5"><AlertTriangle className="w-3.5 h-3.5 text-amber-600" /> MODERATE RISK</span>;
      case 'HIGH RISK':
        return <span className="px-3 py-1 bg-orange-50 text-orange-700 border border-orange-200 rounded-full font-bold text-xs flex items-center gap-1.5"><ShieldAlert className="w-3.5 h-3.5 text-orange-600" /> HIGH RISK</span>;
      default:
        return <span className="px-3 py-1 bg-red-50 text-red-700 border border-red-200 rounded-full font-bold text-xs flex items-center gap-1.5 animate-pulse"><ShieldAlert className="w-3.5 h-3.5 text-red-600" /> CRITICAL RISK</span>;
    }
  };

  const getScoreColor = (score) => {
    if (score >= 85) return 'text-emerald-700 border-emerald-200 bg-emerald-50';
    if (score >= 60) return 'text-amber-700 border-amber-200 bg-amber-50';
    if (score >= 40) return 'text-orange-700 border-orange-200 bg-orange-50';
    return 'text-red-700 border-red-200 bg-red-50';
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      
      {/* Overall Score */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm relative overflow-hidden">
        <div className="flex justify-between items-start mb-2">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Overall Quality</span>
          {getRiskBadge(metrics.risk_level)}
        </div>
        <div className="flex items-baseline space-x-2">
          <span className="text-3xl font-extrabold text-slate-900">{metrics.overall_score}</span>
          <span className="text-sm font-medium text-slate-400">/ 100</span>
        </div>
        <div className="w-full bg-slate-100 h-2 rounded-full mt-3 overflow-hidden">
          <div 
            className="h-full bg-indigo-600 rounded-full transition-all duration-500"
            style={{ width: `${metrics.overall_score}%` }}
          />
        </div>
      </div>

      {/* Security Score */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
        <div className="flex justify-between items-center mb-2">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4 text-emerald-600" /> Security Score
          </span>
          <span className={`px-2 py-0.5 text-xs font-bold border rounded-md ${getScoreColor(metrics.security_score)}`}>
            {metrics.security_score}%
          </span>
        </div>
        <div className="text-2xl font-bold text-slate-900 mb-2">
          {metrics.security_score >= 80 ? 'Robust' : metrics.security_score >= 50 ? 'Vulnerable' : 'Critical Flaws'}
        </div>
        <p className="text-xs text-slate-500">OWASP & static vulnerability index</p>
      </div>

      {/* Cyclomatic Complexity */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
        <div className="flex justify-between items-center mb-2">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
            <Cpu className="w-4 h-4 text-indigo-600" /> Complexity V(G)
          </span>
          <span className="text-xs font-mono font-bold text-indigo-700 bg-indigo-50 border border-indigo-200 px-2 py-0.5 rounded">
            Grade {metrics.cyclomatic_complexity <= 5 ? 'A' : metrics.cyclomatic_complexity <= 10 ? 'B' : 'F'}
          </span>
        </div>
        <div className="text-2xl font-bold text-slate-900 mb-1">
          {metrics.cyclomatic_complexity} <span className="text-xs text-slate-500 font-normal">decision paths</span>
        </div>
        <p className="text-xs text-slate-500">Higher values indicate hard-to-test code</p>
      </div>

      {/* Maintainability Index & LOC */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
        <div className="flex justify-between items-center mb-2">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
            <Activity className="w-4 h-4 text-purple-600" /> Maintainability
          </span>
          <span className="text-xs font-bold text-purple-700 bg-purple-50 border border-purple-200 px-2 py-0.5 rounded">
            {metrics.maintainability_index} MI
          </span>
        </div>
        <div className="grid grid-cols-2 gap-2 text-xs text-slate-700 mt-2 border-t border-slate-100 pt-2">
          <div><span className="text-slate-400">LOC:</span> {metrics.code_lines} / {metrics.total_lines}</div>
          <div><span className="text-slate-400">Funcs:</span> {metrics.functions_count}</div>
          <div><span className="text-slate-400">Comments:</span> {metrics.comment_lines}</div>
          <div><span className="text-slate-400">Classes:</span> {metrics.classes_count}</div>
        </div>
      </div>

    </div>
  );
}
