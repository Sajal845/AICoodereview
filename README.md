# 🛡️ AI Code Review & Bug Detection Platform ⭐⭐⭐⭐⭐

An enterprise-grade, full-stack platform combining **AST (Abstract Syntax Tree) static analysis**, **security vulnerability scanners (OWASP Top 10)**, **cyclomatic complexity calculators**, and **AI/LLM code refactoring** to detect bugs, security flaws, performance bottlenecks, and generate visual side-by-side corrected diffs.

---

## 🌟 Key Features

1. **Multi-layer Code Analysis Pipeline**:
   - **AST Structural Parser**: Extracts functions, classes, AST node count, import graphs, and AST-level anti-patterns (bare excepts, swallowed exceptions, parameter bloat).
   - **Static Security Scanner**: Scans for SQL Injection (CWE-89), Hardcoded Credentials (CWE-798), Dynamic `eval()` Execution (CWE-95), Command Injection (CWE-78), Unsafe Deserialization (CWE-502), Weak MD5 Hashing (CWE-327), and Insecure Randomness (CWE-330).
   - **Complexity & Quality Index**: Calculates Cyclomatic Complexity $V(G)$, Maintainability Index (MI), Lines of Code (LOC, SLOC), and overall Risk Rating (LOW, MODERATE, HIGH, CRITICAL).

2. **AI & LLM Integration Engine**:
   - Multi-provider support: **OpenAI (GPT-4o)**, **Google Gemini**, **Ollama (CodeLlama)**.
   - **Smart Built-in Heuristic AI Fallback Engine**: Works seamlessly out-of-the-box even without external API keys.

3. **Modern React Dashboard**:
   - Interactive code editor with drag-and-drop file upload (`.py`, `.js`, `.ts`, `.cpp`, `.java`, `.go`, `.rs`, etc.).
   - Preset sample vulnerability loader (SQLi & secrets demo, high complexity demo, async JS bug demo).
   - Visual score cards and severity-tagged issue list (Critical, High, Medium, Low).
   - Side-by-side original vs refactored code diff viewer with 1-click copy.
   - Historical audit database logging backed by SQLite.
   - Report Exporter: Export audit summaries as Markdown or JSON reports.

4. **Dockerized Deployment**:
   - Production-ready `Dockerfile`s for both FastAPI backend and React frontend.
   - 1-command startup via `docker-compose up --build`.

---

## 🚀 Quick Start Guide

### Option 1: Running Locally (FastAPI + React)

#### 1. Backend Setup (FastAPI)
```bash
cd ai-code-reviewer/backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/Mac:
# source venv/bin/activate

pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```
Backend API interactive docs will be available at: [http://localhost:8000/docs](http://localhost:8000/docs)

#### 2. Frontend Setup (React + Vite)
```bash
cd ai-code-reviewer/frontend
npm install
npm run dev
```
Open your browser at: [http://localhost:3000](http://localhost:3000)

---

### Option 2: Running with Docker Compose
```bash
cd ai-code-reviewer
docker-compose up --build
```
- Frontend: [http://localhost:3000](http://localhost:3000)
- Backend API: [http://localhost:8000](http://localhost:8000)

---

## 🧪 Testing Sample Files

Pre-loaded sample files are located in `sample_codes/`:
- `vulnerable_python.py`: SQL injection, hardcoded secrets, weak MD5 hash, command injection, unsafe `eval()`.
- `complex_python.py`: Nested conditional logic with high cyclomatic complexity.
- `buggy_js.js`: Async race condition and insecure random token generation.

You can also use the **Samples** quick-loader buttons directly inside the web navigation header!
