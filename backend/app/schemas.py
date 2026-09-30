from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from datetime import datetime

class CodeSubmission(BaseModel):
    code: str
    filename: Optional[str] = "snippet.py"
    language: Optional[str] = "python"
    llm_provider: Optional[str] = "auto" # auto, openai, gemini, ollama, fallback

class IssueItem(BaseModel):
    type: str # security, bug, complexity, smell, performance
    severity: str # critical, high, medium, low, info
    line: int
    title: str
    description: str
    suggestion: str
    rule_id: Optional[str] = None
    cwe: Optional[str] = None

class CodeMetrics(BaseModel):
    total_lines: int
    code_lines: int
    comment_lines: int
    blank_lines: int
    functions_count: int
    classes_count: int
    cyclomatic_complexity: int
    maintainability_index: float
    security_score: float
    overall_score: float
    risk_level: str

class AnalysisResponse(BaseModel):
    id: Optional[int] = None
    filename: str
    language: str
    metrics: CodeMetrics
    issues: List[IssueItem]
    refactored_code: str
    explanation: str
    created_at: Optional[datetime] = None

class HistoryItemResponse(BaseModel):
    id: int
    filename: str
    language: str
    overall_score: float
    security_score: float
    issues_count: int
    created_at: datetime

    class Config:
        from_attributes = True
