import React, { useEffect, useState } from 'react';
import { History, Trash2, Eye, FileCode2, RefreshCw } from 'lucide-react';

export default function HistoryTable({ onLoadReport }) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchHistory = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('/api/history');
      if (!res.ok) throw new Error('Failed to load audit history');
      const data = await res.json();
      setHistory(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleDelete = async (id, e) => {
    e.stopPropagation();
    if (!window.confirm('Delete this audit report from database history?')) return;
    try {
      const res = await fetch(`/api/history/${id}`, { method: 'DELETE' });
      if (res.ok) {
        setHistory(prev => prev.filter(item => item.id !== id));
      }
    } catch (err) {
      alert('Failed to delete report');
    }
  };

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm mb-6">
      
      <div className="flex items-center justify-between mb-5 border-b border-slate-200 pb-4">
        <div className="flex items-center space-x-2">
          <History className="w-5 h-5 text-indigo-600" />
          <h3 className="text-lg font-bold text-slate-900">Audit Report History</h3>
        </div>

        <button
          onClick={fetchHistory}
          className="bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs px-3 py-1.5 rounded flex items-center gap-1.5 transition-all"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {loading && (
        <div className="text-center py-8 text-slate-500 text-sm">
          Loading audit database records...
        </div>
      )}

      {error && (
        <div className="text-center py-6 text-red-700 text-sm bg-red-50 border border-red-200 rounded-lg">
          {error}
        </div>
      )}

      {!loading && history.length === 0 && (
        <div className="text-center py-12 text-slate-400">
          <FileCode2 className="w-12 h-12 mx-auto mb-2 opacity-40 text-slate-400" />
          <p className="text-base font-semibold text-slate-700">No past audits recorded yet.</p>
          <p className="text-xs">Run a code analysis on the main dashboard to save your first audit report.</p>
        </div>
      )}

      {!loading && history.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-200 text-slate-500 text-xs uppercase tracking-wider font-semibold bg-slate-50">
                <th className="py-3 px-4">File Name</th>
                <th className="py-3 px-4">Language</th>
                <th className="py-3 px-4">Quality Score</th>
                <th className="py-3 px-4">Security Score</th>
                <th className="py-3 px-4">Issues Found</th>
                <th className="py-3 px-4">Audit Date</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-sm">
              {history.map((item) => (
                <tr 
                  key={item.id} 
                  className="hover:bg-slate-50 transition-all cursor-pointer"
                  onClick={() => onLoadReport(item.id)}
                >
                  <td className="py-3.5 px-4 font-mono font-medium text-slate-900 flex items-center gap-2">
                    <FileCode2 className="w-4 h-4 text-indigo-600" />
                    <span>{item.filename}</span>
                  </td>
                  <td className="py-3.5 px-4 capitalize text-slate-700">{item.language}</td>
                  <td className="py-3.5 px-4">
                    <span className={`px-2 py-0.5 rounded text-xs font-bold ${
                      item.overall_score >= 80 ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' :
                      item.overall_score >= 50 ? 'bg-amber-50 text-amber-700 border border-amber-200' : 'bg-red-50 text-red-700 border border-red-200'
                    }`}>
                      {item.overall_score}%
                    </span>
                  </td>
                  <td className="py-3.5 px-4">
                    <span className={`px-2 py-0.5 rounded text-xs font-bold ${
                      item.security_score >= 80 ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' :
                      item.security_score >= 50 ? 'bg-amber-50 text-amber-700 border border-amber-200' : 'bg-red-50 text-red-700 border border-red-200'
                    }`}>
                      {item.security_score}%
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-slate-800 font-semibold">{item.issues_count}</td>
                  <td className="py-3.5 px-4 text-xs text-slate-500">
                    {new Date(item.created_at).toLocaleString()}
                  </td>
                  <td className="py-3.5 px-4 text-right space-x-2">
                    <button
                      onClick={(e) => { e.stopPropagation(); onLoadReport(item.id); }}
                      className="p-1.5 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200 rounded transition-all"
                      title="View Detailed Report"
                    >
                      <Eye className="w-4 h-4" />
                    </button>
                    <button
                      onClick={(e) => handleDelete(item.id, e)}
                      className="p-1.5 bg-red-50 hover:bg-red-100 text-red-700 border border-red-200 rounded transition-all"
                      title="Delete Record"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

    </div>
  );
}
