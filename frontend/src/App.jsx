import React, { useState } from 'react';
import Navbar from './components/Navbar';
import MetricsCard from './components/MetricsCard';
import CodeEditor from './components/CodeEditor';
import IssuesList from './components/IssuesList';
import DiffViewer from './components/DiffViewer';
import HistoryTable from './components/HistoryTable';
import ReportExporter from './components/ReportExporter';
import { AlertCircle, ShieldCheck, Cpu, Sparkles, Lock, Terminal } from 'lucide-react';

const SAMPLES = {
  vulnerable: {
    filename: "vulnerable_login.py",
    language: "python",
    code: `import os
import sqlite3
import hashlib

API_KEY = "sk-proj-998877665544332211"
JWT_SECRET = "supersecret12345"

def login_user(username, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    # SQL Injection Vulnerability (CWE-89)
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    cursor.execute(query)
    user = cursor.fetchone()
    
    # Weak MD5 Hashing (CWE-327)
    hashed_pass = hashlib.md5(password.encode()).hexdigest()
    return user

def run_diagnostics(host_ip):
    # Command Injection Vulnerability (CWE-78)
    os.system(f"ping -c 1 {host_ip}")

def parse_user_config(user_input):
    try:
        # Unsafe Eval Execution (CWE-95)
        config = eval(user_input)
        return config
    except:
        # Bare Except Block swallowing errors
        pass`
  },
  complex: {
    filename: "transaction_processor.py",
    language: "python",
    code: `def process_financial_transactions(data, user_role, region, tax_code, is_vip, currency_rate, debug_mode=False, retry_attempts=3):
    result = []
    if data is not None:
        if isinstance(data, list):
            for item in data:
                if item.get("status") == "ACTIVE":
                    if user_role == "ADMIN" or user_role == "FINANCE_MANAGER":
                        if region == "US":
                            if tax_code == "STATE_TEXAS":
                                item["amount"] = item["amount"] * 1.0825
                            elif tax_code == "STATE_CALIFORNIA":
                                item["amount"] = item["amount"] * 1.0925
                            else:
                                item["amount"] = item["amount"] * 1.05
                        elif region == "EU":
                            if tax_code == "VAT_STD":
                                item["amount"] = item["amount"] * 1.20
                            else:
                                item["amount"] = item["amount"] * 1.15
                        else:
                            item["amount"] = item["amount"] * 1.10
                        if is_vip:
                            item["amount"] = item["amount"] * 0.90
                        item["converted_amount"] = item["amount"] * currency_rate
                        result.append(item)
                    elif user_role == "AUDITOR":
                        if debug_mode:
                            print(f"Auditing item: {item}")
                        result.append(item)
                    else:
                        print("Unauthorized user role!")
    return result`
  },
  jsbug: {
    filename: "authSession.js",
    language: "javascript",
    code: `const crypto = require('crypto');

function generateUserSession(userId) {
    // Insecure random token generator (Math.random)
    const token = Math.random().toString(36).substring(2);
    const authSecret = "jwt_secret_key_abcdef123456";
    return { userId, token, secret: authSecret };
}

async function fetchUserData(userId) {
    let userData = null;
    // Missing await on async operation causing race condition
    setTimeout(() => {
        userData = { id: userId, name: "Alice" };
    }, 1000);
    return userData;
}

module.exports = { generateUserSession, fetchUserData };`
  }
};

export default function App() {
  const [activeTab, setActiveTab] = useState('editor');
  const [code, setCode] = useState(SAMPLES.vulnerable.code);
  const [filename, setFilename] = useState(SAMPLES.vulnerable.filename);
  const [language, setLanguage] = useState(SAMPLES.vulnerable.language);
  const [llmProvider, setLlmProvider] = useState('auto');
  
  const [analysisResult, setAnalysisResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSelectSample = (sampleKey) => {
    const sample = SAMPLES[sampleKey];
    if (sample) {
      setCode(sample.code);
      setFilename(sample.filename);
      setLanguage(sample.language);
      setAnalysisResult(null);
      setError(null);
      setActiveTab('editor');
    }
  };

  const handleRunAnalysis = async () => {
    if (!code || !code.trim()) {
      setError('Please enter or upload source code first.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/analyze/text', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code,
          filename,
          language,
          llm_provider: llmProvider
        })
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || 'Code analysis request failed.');
      }

      const data = await response.json();
      setAnalysisResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleLoadHistoryReport = async (reportId) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`/api/history/${reportId}`);
      if (!response.ok) throw new Error('Failed to load past audit report detail.');
      const data = await response.json();
      setAnalysisResult(data);
      setCode(data.code_content || code);
      setFilename(data.filename);
      setLanguage(data.language);
      setActiveTab('editor');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col selection:bg-indigo-500 selection:text-white">
      <Navbar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab} 
        onSelectSample={handleSelectSample} 
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Hero Section Banner */}
        <div className="text-center py-6 mb-8 relative">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-50 border border-indigo-200 text-indigo-700 text-xs font-semibold mb-4">
            <Sparkles className="w-3.5 h-3.5 text-amber-500" />
            <span>AST Static Analysis + Generative Security AI Radar</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight mb-3">
            Automated Code Review & Bug Detection
          </h1>
          <p className="max-w-2xl mx-auto text-slate-600 text-sm sm:text-base leading-relaxed">
            Scan your source code for OWASP Top 10 security vulnerabilities, cyclomatic complexity bottlenecks, syntax errors, and generate ready-to-merge refactored code.
          </p>
        </div>

        {/* Error Alert Box */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-xl p-4 flex items-center gap-3 text-red-700 text-sm">
            <AlertCircle className="w-5 h-5 shrink-0 text-red-600" />
            <span>{error}</span>
          </div>
        )}

        {activeTab === 'editor' ? (
          <>
            <CodeEditor
              code={code}
              setCode={setCode}
              filename={filename}
              setFilename={setFilename}
              language={language}
              setLanguage={setLanguage}
              llmProvider={llmProvider}
              setLlmProvider={setLlmProvider}
              onAnalyze={handleRunAnalysis}
              loading={loading}
            />

            {analysisResult && (
              <>
                <ReportExporter reportData={analysisResult} />
                <MetricsCard metrics={analysisResult.metrics} />
                <IssuesList issues={analysisResult.issues} />
                <DiffViewer
                  originalCode={code}
                  refactoredCode={analysisResult.refactored_code}
                  explanation={analysisResult.explanation}
                />
              </>
            )}

            {/* Platform Features Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12 pt-8 border-t border-slate-200">
              <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-all">
                <div className="w-10 h-10 rounded-lg bg-indigo-50 border border-indigo-200 text-indigo-600 flex items-center justify-center mb-4">
                  <Cpu className="w-5 h-5" />
                </div>
                <h3 className="text-base font-bold text-slate-900 mb-2">AST Structural Visitor</h3>
                <p className="text-xs text-slate-600 leading-relaxed">
                  Extracts functions, class count, docstrings, swallowed exceptions, parameter bloat, and Abstract Syntax Tree anomalies.
                </p>
              </div>

              <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-all">
                <div className="w-10 h-10 rounded-lg bg-red-50 border border-red-200 text-red-600 flex items-center justify-center mb-4">
                  <Lock className="w-5 h-5" />
                </div>
                <h3 className="text-base font-bold text-slate-900 mb-2">OWASP Security Scanner</h3>
                <p className="text-xs text-slate-600 leading-relaxed">
                  Identifies SQL Injection (CWE-89), Hardcoded Credentials (CWE-798), Dynamic `eval()` Execution, and Command Execution.
                </p>
              </div>

              <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-all">
                <div className="w-10 h-10 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-600 flex items-center justify-center mb-4">
                  <Terminal className="w-5 h-5" />
                </div>
                <h3 className="text-base font-bold text-slate-900 mb-2">Side-by-Side Diff Generator</h3>
                <p className="text-xs text-slate-600 leading-relaxed">
                  Generates clean, production-grade replacement code with side-by-side visual diff comparison and copy functionality.
                </p>
              </div>
            </div>
          </>
        ) : (
          <HistoryTable onLoadReport={handleLoadHistoryReport} />
        )}

      </main>

      <footer className="bg-white border-t border-slate-200 py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center space-x-2">
            <ShieldCheck className="w-4 h-4 text-indigo-600" />
            <span className="font-semibold text-slate-700">CodeSentinel AI — Light Theme Production Code Review Suite</span>
          </div>
          <p>© 2026 CodeSentinel | Built with Python, FastAPI, React, AST & Generative AI</p>
        </div>
      </footer>
    </div>
  );
}
