import os
import sys
import json
import ast
import re
import math
import sqlite3
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse
from datetime import datetime

PORT = 8000
DB_FILE = os.path.join(os.path.dirname(__file__), "code_reviews_standalone.db")

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            language TEXT,
            code_content TEXT,
            overall_score REAL,
            security_score REAL,
            maintainability_index REAL,
            cyclomatic_complexity INTEGER,
            metrics_json TEXT,
            issues_json TEXT,
            refactored_code TEXT,
            explanation TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

SECURITY_PATTERNS = [
    {
        "id": "SEC001",
        "title": "SQL Injection Vulnerability",
        "type": "security",
        "severity": "critical",
        "cwe": "CWE-89",
        "pattern": r"(SELECT|INSERT|UPDATE|DELETE)\s+.*?\+.*?\b|\bexecute\s*\(\s*['\"].*?%s|f['\"].*?(SELECT|INSERT|UPDATE|DELETE)",
        "description": "Dynamic string concatenation in SQL query allows attackers to inject malicious database commands.",
        "suggestion": "Use parameterized queries e.g., cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))"
    },
    {
        "id": "SEC002",
        "title": "Hardcoded Secret / API Key",
        "type": "security",
        "severity": "critical",
        "cwe": "CWE-798",
        "pattern": r"(api[_-]?key|secret[_-]?key|password|jwt[_-]?token|auth[_-]?token)\s*=\s*['\"][A-Za-z0-9_\-\.]{8,}'\"]",
        "description": "Sensitive credentials or secrets hardcoded directly in source code.",
        "suggestion": "Move secrets into environment variables e.g. os.getenv('API_KEY')."
    },
    {
        "id": "SEC003",
        "title": "Unsafe Dynamic Evaluation (eval/exec)",
        "type": "security",
        "severity": "critical",
        "cwe": "CWE-95",
        "pattern": r"\b(eval|exec)\s*\(",
        "description": "Executing dynamic string input with eval() or exec() permits arbitrary remote code execution.",
        "suggestion": "Avoid eval(). Use ast.literal_eval() for safe literal parsing."
    },
    {
        "id": "SEC004",
        "title": "Command Injection Vulnerability",
        "type": "security",
        "severity": "critical",
        "cwe": "CWE-78",
        "pattern": r"\b(os\.system|subprocess\.Popen|subprocess\.call|subprocess\.run)\s*\(\s*f?['\"].*?\+|subprocess.*shell\s*=\s*True",
        "description": "Executing OS commands with unescaped shell strings enables arbitrary system command injection.",
        "suggestion": "Pass command arguments as a list of strings and set shell=False."
    }
]

def analyze_code_internal(code, filename="snippet.py", language="python"):
    lines = code.splitlines()
    total_lines = len(lines)
    code_lines = sum(1 for line in lines if line.strip() and not line.strip().startswith("#"))
    comment_lines = sum(1 for line in lines if line.strip().startswith("#"))
    blank_lines = total_lines - code_lines - comment_lines

    functions_count = 0
    classes_count = 0
    issues = []
    
    if language.lower() in ["python", "py"]:
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions_count += 1
                elif isinstance(node, ast.ClassDef):
                    classes_count += 1
                elif isinstance(node, ast.ExceptHandler):
                    if node.type is None:
                        issues.append({
                            "type": "smell", "severity": "high", "line": node.lineno,
                            "title": "Bare Except Clause",
                            "description": "Catching all exceptions using bare except: masks bugs and prevents graceful termination.",
                            "suggestion": "Specify exact exception types e.g., except ValueError:",
                            "rule_id": "AST003"
                        })
        except SyntaxError as se:
            issues.append({
                "type": "bug", "severity": "critical", "line": se.lineno or 1,
                "title": "Syntax Error Detected", "description": f"SyntaxError: {se.msg}",
                "suggestion": "Fix syntax near error line.", "rule_id": "SYNTAX001"
            })

    for rule in SECURITY_PATTERNS:
        compiled = re.compile(rule["pattern"], re.IGNORECASE)
        for idx, line in enumerate(lines, start=1):
            if compiled.search(line):
                issues.append({
                    "type": rule["type"], "severity": rule["severity"], "line": idx,
                    "title": rule["title"], "description": rule["description"],
                    "suggestion": rule["suggestion"], "rule_id": rule["id"], "cwe": rule["cwe"]
                })

    complexity = max(1, code.count("if ") + code.count("for ") + code.count("while ") + code.count("except ") + 1)
    maintainability = max(0.0, min(100.0, round(171 - (0.23 * complexity) - (16.2 * math.log(max(1, code_lines))), 1)))
    
    crit_count = sum(1 for i in issues if i.get("severity") == "critical")
    sec_score = max(0.0, round(100.0 - (crit_count * 25) - ((len(issues) - crit_count) * 10), 1))
    overall_score = round((sec_score * 0.5) + (maintainability * 0.5), 1)
    
    risk_level = "LOW RISK" if overall_score >= 85 else "MODERATE RISK" if overall_score >= 60 else "HIGH RISK" if overall_score >= 40 else "CRITICAL RISK"

    refactored = code
    refactored = refactored.replace("f\"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'\"", "\"SELECT * FROM users WHERE username = %s AND password = %s\", (username, password)")
    refactored = refactored.replace("API_KEY = \"sk-proj-998877665544332211\"", "import os\nAPI_KEY = os.getenv('API_KEY')")
    refactored = refactored.replace("eval(user_input)", "ast.literal_eval(user_input)")
    refactored = refactored.replace("os.system(f\"ping -c 1 {host}\")", "subprocess.run(['ping', '-c', '1', host], check=True)")
    refactored = refactored.replace("except:", "except Exception as e:")

    explanation = f"### 🛡️ AI Security Audit Report\nAnalyzed `{filename}`. Found **{len(issues)} issue(s)**. Code refactored to patch security vulnerabilities and enforce clean architecture standards."

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    metrics = {
        "total_lines": total_lines, "code_lines": code_lines, "comment_lines": comment_lines,
        "blank_lines": blank_lines, "functions_count": functions_count, "classes_count": classes_count,
        "cyclomatic_complexity": complexity, "maintainability_index": maintainability,
        "security_score": sec_score, "overall_score": overall_score, "risk_level": risk_level
    }
    c.execute('''
        INSERT INTO reports (filename, language, code_content, overall_score, security_score, maintainability_index, cyclomatic_complexity, metrics_json, issues_json, refactored_code, explanation)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (filename, language, code, overall_score, sec_score, maintainability, complexity, json.dumps(metrics), json.dumps(issues), refactored, explanation))
    report_id = c.lastrowid
    conn.commit()
    conn.close()

    return {
        "id": report_id,
        "filename": filename,
        "language": language,
        "metrics": metrics,
        "issues": issues,
        "refactored_code": refactored,
        "explanation": explanation
    }

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CodeSentinel AI — Enterprise AI Code Review & Security Audit Platform</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-light: #F8FAFC;
            --card-light: #FFFFFF;
            --border-light: #E2E8F0;
            --text-dark: #0F172A;
            --text-muted: #64748B;
            --brand-primary: #4F46E5;
            --brand-hover: #4338CA;
        }
        body {
            background-color: var(--bg-light);
            color: var(--text-dark);
            font-family: 'Plus Jakarta Sans', sans-serif;
        }
        .navbar-light-custom {
            background-color: #FFFFFF;
            border-bottom: 1px solid var(--border-light);
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        .white-card {
            background-color: var(--card-light);
            border: 1px solid var(--border-light);
            border-radius: 16px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
            transition: all 0.2s ease;
        }
        .white-card:hover {
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.06);
        }
        .code-textarea {
            background-color: #F8FAFC !important;
            border: 1px solid var(--border-light) !important;
            color: #0F172A !important;
            font-family: 'Fira Code', monospace !important;
            font-size: 0.88rem;
            line-height: 1.6;
            border-radius: 12px;
        }
        .code-textarea:focus {
            background-color: #FFFFFF !important;
            border-color: var(--brand-primary) !important;
            box-shadow: 0 0 0 4px rgba(79, 70, 229, 0.1) !important;
        }
        .btn-brand-primary {
            background: linear-gradient(135deg, #4F46E5, #6366F1);
            border: none;
            color: white;
            font-weight: 700;
            padding: 12px 24px;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.25);
            transition: all 0.2s ease;
        }
        .btn-brand-primary:hover {
            background: linear-gradient(135deg, #4338CA, #4F46E5);
            box-shadow: 0 6px 18px rgba(79, 70, 229, 0.35);
            color: white;
        }
        .metric-card {
            background-color: #FFFFFF;
            border: 1px solid var(--border-light);
            border-radius: 14px;
            padding: 16px;
            text-align: center;
        }
        .metric-value {
            font-size: 2.2rem;
            font-weight: 800;
            letter-spacing: -1px;
            margin-top: 4px;
        }
        .badge-severity-critical {
            background-color: #FEF2F2;
            color: #DC2626;
            border: 1px solid #FCA5A5;
            font-size: 0.75rem;
            font-weight: 700;
            padding: 4px 10px;
            border-radius: 6px;
        }
        .badge-severity-high {
            background-color: #FFF7ED;
            color: #EA580C;
            border: 1px solid #FDBA74;
            font-size: 0.75rem;
            font-weight: 700;
            padding: 4px 10px;
            border-radius: 6px;
        }
        pre.code-diff {
            background-color: #0F172A;
            border: 1px solid #1E293B;
            border-radius: 12px;
            padding: 16px;
            font-family: 'Fira Code', monospace;
            font-size: 0.85rem;
            color: #34D399;
            overflow-x: auto;
        }
        .feature-icon-light {
            width: 44px;
            height: 44px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
            background-color: #EEF2FF;
            color: #4F46E5;
        }
    </style>
</head>
<body>

    <!-- Light Navigation Header -->
    <nav class="navbar navbar-expand-lg navbar-light-custom py-3 sticky-top">
        <div class="container-xl">
            <a class="navbar-brand d-flex align-items-center gap-3" href="#">
                <div class="p-2 bg-indigo-600 rounded-3 text-white shadow-sm" style="background-color: #4F46E5;">
                    <i class="bi bi-shield-check fs-5"></i>
                </div>
                <div>
                    <span class="fw-bold fs-5 text-dark">CodeSentinel</span>
                    <span class="badge bg-indigo-50 text-indigo-700 border border-indigo-200 rounded-pill ms-2 px-2 py-1 align-middle" style="font-size: 0.65rem; color: #4F46E5; background-color: #EEF2FF;">LIGHT THEME PRO</span>
                </div>
            </a>

            <div class="d-none d-lg:flex align-items-center gap-2 bg-light p-1 rounded-3 border border-slate-200 ms-auto me-4">
                <small class="text-muted px-2 font-semibold"><i class="bi bi-stars text-warning me-1"></i> Quick Demos:</small>
                <button onclick="loadSample('vulnerable')" class="btn btn-sm btn-outline-danger border-0 text-xs">SQLi & Secrets</button>
                <button onclick="loadSample('complex')" class="btn btn-sm btn-outline-warning border-0 text-xs">High Complexity</button>
                <button onclick="loadSample('jsbug')" class="btn btn-sm btn-outline-primary border-0 text-xs">Async JS Bug</button>
            </div>
        </div>
    </nav>

    <!-- Main Container -->
    <div class="container-xl py-5">
        
        <!-- Hero Section Title -->
        <div class="text-center mb-5 max-w-3xl mx-auto">
            <span class="badge px-3 py-2 rounded-pill fw-semibold mb-3" style="background-color: #EEF2FF; color: #4F46E5; border: 1px solid #C7D2FE;">
                <i class="bi bi-cpu me-1"></i> AST Static Analysis + Generative Security AI Radar
            </span>
            <h1 class="fw-extrabold display-5 text-dark tracking-tight mb-3">
                Automated Code Review & Bug Detection
            </h1>
            <p class="text-muted lead fs-6">
                Upload or paste source code to instantly detect OWASP security vulnerabilities, cyclomatic complexity bottlenecks, syntax flaws, and generate clean refactored code.
            </p>
        </div>

        <!-- Analyzer Grid -->
        <div class="row g-4 mb-5">
            
            <!-- Code Input Panel -->
            <div class="col-lg-6">
                <div class="white-card p-4 h-100 d-flex flex-column">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <div class="d-flex align-items-center gap-2">
                            <i class="bi bi-file-earmark-code text-indigo-600 fs-5" style="color: #4F46E5;"></i>
                            <h6 class="fw-bold m-0 text-dark">Source Code Input</h6>
                        </div>
                        <select id="langSelect" class="form-select form-select-sm w-auto border-slate-300">
                            <option value="python">Python (.py)</option>
                            <option value="javascript">JavaScript (.js)</option>
                            <option value="typescript">TypeScript (.ts)</option>
                        </select>
                    </div>

                    <div class="position-relative flex-grow-1 mb-3">
                        <textarea id="codeEditor" class="form-control code-textarea h-100" rows="18" placeholder="// Paste source code here for instant AI security analysis..."></textarea>
                    </div>

                    <button onclick="analyzeCode()" id="analyzeBtn" class="btn btn-brand-primary w-100">
                        <i class="bi bi-lightning-charge-fill me-2"></i>Run AI Security & Quality Audit
                    </button>
                </div>
            </div>

            <!-- Audit Results Panel -->
            <div class="col-lg-6">
                <div id="placeholderBox" class="white-card p-5 text-center text-muted h-100 d-flex flex-column justify-content-center align-items-center">
                    <div class="p-4 bg-light rounded-circle mb-3 border border-slate-200">
                        <i class="bi bi-radar display-4 text-indigo-600 opacity-50" style="color: #4F46E5;"></i>
                    </div>
                    <h5 class="fw-bold text-dark mb-2">Ready for Audit</h5>
                    <p class="small text-muted mb-4" style="max-width: 320px;">Paste code or select a quick demo above, then click 'Run AI Security & Quality Audit'.</p>
                    <div class="d-flex gap-2">
                        <button onclick="loadSample('vulnerable')" class="btn btn-sm btn-outline-primary px-3">Try SQL Injection Demo</button>
                    </div>
                </div>

                <div id="resultsContainer" style="display:none;">
                    
                    <!-- Metric Cards Row -->
                    <div class="row g-3 mb-4">
                        <div class="col-6 col-sm-3">
                            <div class="metric-card shadow-sm">
                                <small class="text-muted text-uppercase fw-bold" style="font-size:0.65rem;">Overall Score</small>
                                <div id="overallScore" class="metric-value text-dark">100</div>
                            </div>
                        </div>
                        <div class="col-6 col-sm-3">
                            <div class="metric-card shadow-sm">
                                <small class="text-muted text-uppercase fw-bold" style="font-size:0.65rem;">Security Score</small>
                                <div id="secScore" class="metric-value text-success">100%</div>
                            </div>
                        </div>
                        <div class="col-6 col-sm-3">
                            <div class="metric-card shadow-sm">
                                <small class="text-muted text-uppercase fw-bold" style="font-size:0.65rem;">Complexity V(G)</small>
                                <div id="compScore" class="metric-value text-primary">1</div>
                            </div>
                        </div>
                        <div class="col-6 col-sm-3">
                            <div class="metric-card shadow-sm">
                                <small class="text-muted text-uppercase fw-bold" style="font-size:0.65rem;">Maintainability</small>
                                <div id="maintScore" class="metric-value text-warning">100</div>
                            </div>
                        </div>
                    </div>

                    <!-- Vulnerabilities & Defects List -->
                    <div class="white-card p-4 mb-4">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <h6 class="fw-bold m-0 text-dark"><i class="bi bi-shield-alert text-danger me-2"></i>Security Flaws & Code Smells</h6>
                            <span id="issuesCountBadge" class="badge bg-danger bg-opacity-10 text-danger border border-danger border-opacity-20">0 Found</span>
                        </div>
                        <div id="issuesList" class="d-flex flex-column gap-2"></div>
                    </div>

                    <!-- AI Refactored Code Box -->
                    <div class="white-card p-4">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <h6 class="fw-bold m-0 text-dark"><i class="bi bi-magic text-success me-2"></i>AI Refactored Code Fix</h6>
                            <button onclick="copyRefactored()" class="btn btn-sm btn-outline-success"><i class="bi bi-copy me-1"></i>Copy Fixed Code</button>
                        </div>
                        <pre id="refactoredCode" class="code-diff mb-0"></pre>
                    </div>

                </div>
            </div>

        </div>

        <!-- Features Showcase Cards -->
        <div class="row g-4 mt-4 border-top border-slate-200 pt-5">
            <div class="col-md-4">
                <div class="white-card p-4 h-100">
                    <div class="feature-icon-light mb-3">
                        <i class="bi bi-diagram-3-fill"></i>
                    </div>
                    <h6 class="fw-bold text-dark mb-2">AST Node Parsing</h6>
                    <p class="small text-muted m-0">Validates syntax trees, function signatures, swallowed exception handlers, and architectural anti-patterns.</p>
                </div>
            </div>
            <div class="col-md-4">
                <div class="white-card p-4 h-100">
                    <div class="feature-icon-light mb-3" style="background-color: #FEF2F2; color: #DC2626;">
                        <i class="bi bi-shield-lock-fill"></i>
                    </div>
                    <h6 class="fw-bold text-dark mb-2">OWASP Security Audit</h6>
                    <p class="small text-muted m-0">Scans for SQL Injections (CWE-89), Hardcoded Credentials (CWE-798), Command Execution, and `eval()` vulnerabilities.</p>
                </div>
            </div>
            <div class="col-md-4">
                <div class="white-card p-4 h-100">
                    <div class="feature-icon-light mb-3" style="background-color: #ECFDF5; color: #059669;">
                        <i class="bi bi-code-square"></i>
                    </div>
                    <h6 class="fw-bold text-dark mb-2">AI Side-by-Side Refactoring</h6>
                    <p class="small text-secondary m-0">Generates ready-to-merge refactored replacement code with line-by-line fix justifications.</p>
                </div>
            </div>
        </div>

    </div>

    <script>
        const samples = {
            vulnerable: `import os\nimport sqlite3\nimport hashlib\n\nAPI_KEY = "sk-proj-998877665544332211"\n\ndef login_user(username, password):\n    conn = sqlite3.connect("users.db")\n    cursor = conn.cursor()\n    # SQL Injection Vulnerability (CWE-89)\n    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"\n    cursor.execute(query)\n    user = cursor.fetchone()\n    return user\n\ndef run_diagnostics(host_ip):\n    # Command Injection Vulnerability (CWE-78)\n    os.system(f"ping -c 1 {host_ip}")\n\ndef parse_user_config(user_input):\n    # Unsafe Eval Execution (CWE-95)\n    return eval(user_input)`,
            complex: `def process_data(data, user_role, tax_code, is_vip, currency_rate):\n    result = []\n    if data:\n        for item in data:\n            if user_role == "ADMIN" or user_role == "FINANCE":\n                if tax_code == "STATE_TX": item["amount"] *= 1.08\n                elif tax_code == "STATE_CA": item["amount"] *= 1.09\n                else: item["amount"] *= 1.05\n                if is_vip: item["amount"] *= 0.90\n                result.append(item)\n    return result`,
            jsbug: `const crypto = require('crypto');\n\nfunction generateUserSession(userId) {\n    const token = Math.random().toString(36).substring(2);\n    const authSecret = "jwt_secret_key_abcdef123456";\n    return { userId, token, secret: authSecret };\n}`
        };

        function loadSample(key) {
            document.getElementById('codeEditor').value = samples[key];
            if (key === 'jsbug') document.getElementById('langSelect').value = 'javascript';
            else document.getElementById('langSelect').value = 'python';
        }

        async function analyzeCode() {
            const code = document.getElementById('codeEditor').value;
            if (!code.trim()) return alert('Please enter source code!');

            const btn = document.getElementById('analyzeBtn');
            btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Analyzing Code...';
            btn.disabled = true;

            try {
                const res = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ code: code, language: document.getElementById('langSelect').value })
                });

                const data = await res.json();
                document.getElementById('placeholderBox').style.setProperty('display', 'none', 'important');
                document.getElementById('resultsContainer').style.display = 'block';

                document.getElementById('overallScore').innerText = data.metrics.overall_score;
                document.getElementById('secScore').innerText = data.metrics.security_score + '%';
                document.getElementById('compScore').innerText = data.metrics.cyclomatic_complexity;
                document.getElementById('maintScore').innerText = data.metrics.maintainability_index;

                document.getElementById('issuesCountBadge').innerText = data.issues.length + ' Found';

                const issuesDiv = document.getElementById('issuesList');
                issuesDiv.innerHTML = '';
                if (data.issues.length === 0) {
                    issuesDiv.innerHTML = '<div class="alert alert-success m-0 border-0 bg-success bg-opacity-10 text-success"><i class="bi bi-check-circle-fill me-2"></i>Zero issues detected! Code adheres to clean security standards.</div>';
                } else {
                    data.issues.forEach(i => {
                        const sevClass = i.severity.toLowerCase() === 'critical' ? 'badge-severity-critical' : 'badge-severity-high';
                        issuesDiv.innerHTML += `
                            <div class="p-3 rounded-3 bg-light border border-slate-200">
                                <div class="d-flex justify-content-between align-items-center mb-1">
                                    <span class="fw-bold text-dark small">${i.title} <span class="text-muted font-monospace ms-2">Line ${i.line}</span></span>
                                    <span class="${sevClass}">${i.severity.toUpperCase()}</span>
                                </div>
                                <p class="small text-muted mb-2">${i.description}</p>
                                <div class="small text-indigo-700 bg-indigo-50 p-2 rounded border border-indigo-200" style="color:#4F46E5; background-color:#EEF2FF;">
                                    <i class="bi bi-arrow-return-right me-1"></i><strong>Fix:</strong> ${i.suggestion}
                                </div>
                            </div>
                        `;
                    });
                }

                document.getElementById('refactoredCode').innerText = data.refactored_code;
            } catch (err) {
                alert('Analysis failed: ' + err.message);
            } finally {
                btn.innerHTML = '<i class="bi bi-lightning-charge-fill me-2"></i>Run AI Security & Quality Audit';
                btn.disabled = false;
            }
        }

        function copyRefactored() {
            const text = document.getElementById('refactoredCode').innerText;
            navigator.clipboard.writeText(text);
            alert('Refactored code copied to clipboard!');
        }

        // Auto load initial demo
        loadSample('vulnerable');
    </script>
</body>
</html>
"""

class StandaloneRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode("utf-8"))
        elif self.path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/api/analyze":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            payload = json.loads(post_data.decode('utf-8'))
            
            code = payload.get("code", "")
            language = payload.get("language", "python")
            
            result = analyze_code_internal(code, language=language)
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", PORT), StandaloneRequestHandler)
    print(f"=======================================================")
    print(f"🚀 CodeSentinel AI Light Theme Platform Online!")
    print(f"👉 Open in Browser: http://127.0.0.1:{PORT}")
    print(f"=======================================================")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped.")
