import ast
from typing import Dict, Any, List

class PythonASTVisitor(ast.NodeVisitor):
    def __init__(self):
        self.functions_count = 0
        self.classes_count = 0
        self.imports = []
        self.issues = []
        self.function_names = []
        self.class_names = []

    def visit_FunctionDef(self, node):
        self.functions_count += 1
        self.function_names.append(node.name)
        
        # Check for empty docstrings or excessive arguments
        if len(node.args.args) > 5:
            self.issues.append({
                "type": "complexity",
                "severity": "medium",
                "line": node.lineno,
                "title": "Too Many Parameters",
                "description": f"Function '{node.name}' has {len(node.args.args)} parameters. Consider grouping parameters into a data structure.",
                "suggestion": "Refactor parameters into a Dataclass or Pydantic model.",
                "rule_id": "AST001"
            })
        
        # Check for bare return in function with logic
        if len(node.body) > 30:
            self.issues.append({
                "type": "complexity",
                "severity": "low",
                "line": node.lineno,
                "title": "Long Function Body",
                "description": f"Function '{node.name}' is {len(node.body)} statements long. High complexity functions are harder to maintain.",
                "suggestion": "Break down into smaller modular helper functions.",
                "rule_id": "AST002"
            })
            
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)

    def visit_ClassDef(self, node):
        self.classes_count += 1
        self.class_names.append(node.name)
        self.generic_visit(node)

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            self.imports.append(node.module)
        self.generic_visit(node)

    def visit_ExceptHandler(self, node):
        # Check for bare except: or except Exception: pass
        if node.type is None:
            self.issues.append({
                "type": "smell",
                "severity": "high",
                "line": node.lineno,
                "title": "Bare Except Clause",
                "description": "Catching all exceptions using a bare `except:` masks unexpected bugs and system exit signals.",
                "suggestion": "Specify exact exception types e.g., `except ValueError:` or `except KeyError:`.",
                "rule_id": "AST003"
            })
        elif isinstance(node.body[0], ast.Pass):
            self.issues.append({
                "type": "smell",
                "severity": "medium",
                "line": node.lineno,
                "title": "Silenced Exception",
                "description": "Exception block contains only `pass`, silently swallowing errors without logging or handling.",
                "suggestion": "Log the error or handle exception gracefully.",
                "rule_id": "AST004"
            })
        self.generic_visit(node)

def analyze_python_ast(code: str) -> Dict[str, Any]:
    try:
        tree = ast.parse(code)
        visitor = PythonASTVisitor()
        visitor.visit(tree)
        return {
            "is_valid": True,
            "functions_count": visitor.functions_count,
            "classes_count": visitor.classes_count,
            "imports": visitor.imports,
            "ast_issues": visitor.issues,
            "syntax_error": None
        }
    except SyntaxError as se:
        return {
            "is_valid": False,
            "functions_count": 0,
            "classes_count": 0,
            "imports": [],
            "ast_issues": [{
                "type": "bug",
                "severity": "critical",
                "line": se.lineno or 1,
                "title": "Syntax Error",
                "description": f"SyntaxError: {se.msg} at line {se.lineno}",
                "suggestion": f"Fix syntax near: {se.text.strip() if se.text else ''}",
                "rule_id": "SYNTAX001"
            }],
            "syntax_error": str(se)
        }
    except Exception as e:
        return {
            "is_valid": True,
            "functions_count": 0,
            "classes_count": 0,
            "imports": [],
            "ast_issues": [],
            "syntax_error": str(e)
        }
