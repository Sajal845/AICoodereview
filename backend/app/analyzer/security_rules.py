import re
from typing import List, Dict, Any

SECURITY_PATTERNS = [
    {
        "id": "SEC001",
        "title": "Potential SQL Injection",
        "type": "security",
        "severity": "critical",
        "cwe": "CWE-89",
        "pattern": r"(SELECT|INSERT|UPDATE|DELETE)\s+.*?\+.*?\b|\bexecute\s*\(\s*['\"].*?%s|f['\"].*?(SELECT|INSERT|UPDATE|DELETE)",
        "description": "SQL query created using dynamic string concatenation or f-strings instead of parameterized queries.",
        "suggestion": "Use parameterized queries or ORM binding e.g., `cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))`"
    },
    {
        "id": "SEC002",
        "title": "Hardcoded Secret / API Key",
        "type": "security",
        "severity": "critical",
        "cwe": "CWE-798",
        "pattern": r"(api[_-]?key|secret[_-]?key|password|jwt[_-]?token|auth[_-]?token)\s*=\s*['\"][A-Za-z0-9_\-\.]{8,}'\"]",
        "description": "Hardcoded sensitive credentials detected in source code.",
        "suggestion": "Extract secrets into environment variables or a secret management service (e.g. `os.getenv('API_KEY')`)."
    },
    {
        "id": "SEC003",
        "title": "Unsafe Dynamic Evaluation (eval/exec)",
        "type": "security",
        "severity": "critical",
        "cwe": "CWE-95",
        "pattern": r"\b(eval|exec)\s*\(",
        "description": "Execution of dynamic string code using `eval()` or `exec()`. Allows arbitrary code execution.",
        "suggestion": "Avoid `eval()` / `exec()`. Use `ast.literal_eval()` for safe evaluation of literals."
    },
    {
        "id": "SEC004",
        "title": "Command Injection Vulnerability",
        "type": "security",
        "severity": "critical",
        "cwe": "CWE-78",
        "pattern": r"\b(os\.system|subprocess\.Popen|subprocess\.call|subprocess\.run)\s*\(\s*f?['\"].*?\+|subprocess.*shell\s*=\s*True",
        "description": "OS command execution with raw string concatenation or `shell=True`.",
        "suggestion": "Pass command arguments as a list of strings and set `shell=False` e.g., `subprocess.run(['ls', '-l'])`."
    },
    {
        "id": "SEC005",
        "title": "Insecure Deserialization (pickle)",
        "type": "security",
        "severity": "high",
        "cwe": "CWE-502",
        "pattern": r"\bpickle\.loads?\s*\(",
        "description": "Deserializing untrusted data with `pickle` can execute arbitrary bytecode.",
        "suggestion": "Use safer serialization formats like JSON, Protocol Buffers, or `json.loads()`."
    },
    {
        "id": "SEC006",
        "title": "Weak Cryptographic Hashing Algorithm",
        "type": "security",
        "severity": "high",
        "cwe": "CWE-327",
        "pattern": r"\b(hashlib\.md5|hashlib\.sha1)\b",
        "description": "MD5 and SHA-1 algorithms are cryptographically vulnerable to collision attacks.",
        "suggestion": "Upgrade to SHA-256 (`hashlib.sha256()`) or password hashing standards like Argon2 / bcrypt."
    },
    {
        "id": "SEC007",
        "title": "Insecure CORS Configuration",
        "type": "security",
        "severity": "medium",
        "cwe": "CWE-942",
        "pattern": r"allow_origins\s*=\s*\[\s*['\"]\*['\"]\s*\]",
        "description": "CORS configured with wildcard origin `*` allows any third-party website to make authenticated requests.",
        "suggestion": "Specify explicit allowed origin domains e.g., `allow_origins=['https://mydomain.com']`."
    },
    {
        "id": "SEC008",
        "title": "Insecure Randomness for Security",
        "type": "security",
        "severity": "medium",
        "cwe": "CWE-330",
        "pattern": r"\bimport random\b|\brandom\.(randint|choice|random)\s*\(",
        "description": "Standard `random` module uses pseudo-random generator, unsafe for security tokens, nonces, or passwords.",
        "suggestion": "Use `secrets` module for cryptographically secure random values e.g., `secrets.token_hex(16)`."
    }
]

def scan_security_issues(code: str) -> List[Dict[str, Any]]:
    issues = []
    lines = code.splitlines()
    
    for rule in SECURITY_PATTERNS:
        compiled_regex = re.compile(rule["pattern"], re.IGNORECASE)
        for line_idx, line_content in enumerate(lines, start=1):
            if compiled_regex.search(line_content):
                issues.append({
                    "type": rule["type"],
                    "severity": rule["severity"],
                    "line": line_idx,
                    "title": rule["title"],
                    "description": rule["description"],
                    "suggestion": rule["suggestion"],
                    "rule_id": rule["id"],
                    "cwe": rule["cwe"]
                })
    return issues
