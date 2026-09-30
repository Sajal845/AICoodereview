import ast
import math
from typing import Dict, Any

try:
    from radon.complexity import cc_visit
    from radon.metrics import mi_visit
    RADON_AVAILABLE = True
except ImportError:
    RADON_AVAILABLE = False

def calculate_lines_metrics(code: str) -> Dict[str, int]:
    lines = code.splitlines()
    total_lines = len(lines)
    blank_lines = 0
    comment_lines = 0
    code_lines = 0

    for line in lines:
        stripped = line.strip()
        if not stripped:
            blank_lines += 1
        elif stripped.startswith("#") or stripped.startswith("//") or stripped.startswith("/*"):
            comment_lines += 1
        else:
            code_lines += 1

    return {
        "total_lines": total_lines,
        "code_lines": code_lines,
        "comment_lines": comment_lines,
        "blank_lines": blank_lines
    }

def calculate_complexity(code: str, language: str = "python") -> int:
    if language.lower() == "python":
        if RADON_AVAILABLE:
            try:
                blocks = cc_visit(code)
                if blocks:
                    return max([block.complexity for block in blocks])
            except Exception:
                pass
        
        # Fallback AST-based cyclomatic complexity calculation
        try:
            tree = ast.parse(code)
            complexity = 1
            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.For, ast.While, ast.And, ast.Or, ast.ExceptHandler, ast.With, ast.Try)):
                    complexity += 1
            return complexity
        except Exception:
            return 1
    
    # Generic fallback regex branch count for other languages
    branches = code.count("if ") + code.count("else if") + code.count("for ") + code.count("while ") + code.count("catch ") + code.count("case ")
    return max(1, branches + 1)

def calculate_maintainability(code: str, complexity: int, code_lines: int) -> float:
    if RADON_AVAILABLE:
        try:
            return round(mi_visit(code, multi=True), 2)
        except Exception:
            pass

    # Standard Maintainability Index Formula approximation:
    # MI = 171 - 5.2 * ln(Halstead Volume) - 0.23 * (Cyclomatic Complexity) - 16.2 * ln(LOC)
    loc = max(1, code_lines)
    mi = 171 - (0.23 * complexity) - (16.2 * math.log(loc))
    normalized_mi = max(0.0, min(100.0, mi))
    return round(normalized_mi, 2)

def compute_overall_scores(security_issues_count: int, critical_issues: int, maintainability: float, complexity: int) -> Dict[str, Any]:
    # Calculate Security Score (0 to 100)
    sec_deduction = (critical_issues * 25) + ((security_issues_count - critical_issues) * 10)
    security_score = max(0.0, 100.0 - sec_deduction)

    # Calculate Complexity penalty
    comp_penalty = max(0, (complexity - 5) * 4)

    # Overall Score weighted average
    overall = (security_score * 0.45) + (maintainability * 0.40) + (max(0, 100 - comp_penalty) * 0.15)
    overall_score = round(max(0.0, min(100.0, overall)), 1)

    if overall_score >= 85:
        risk_level = "LOW RISK"
    elif overall_score >= 60:
        risk_level = "MODERATE RISK"
    elif overall_score >= 40:
        risk_level = "HIGH RISK"
    else:
        risk_level = "CRITICAL RISK"

    return {
        "security_score": round(security_score, 1),
        "overall_score": overall_score,
        "risk_level": risk_level
    }
