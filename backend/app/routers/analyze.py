from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models import CodeAnalysisReport
from app.schemas import CodeSubmission, AnalysisResponse, CodeMetrics, IssueItem
from app.analyzer.ast_analyzer import analyze_python_ast
from app.analyzer.security_rules import scan_security_issues
from app.analyzer.complexity import (
    calculate_lines_metrics,
    calculate_complexity,
    calculate_maintainability,
    compute_overall_scores
)
from app.analyzer.llm_analyzer import analyze_with_llm

router = APIRouter(prefix="/api/analyze", tags=["Code Analysis"])

def _perform_analysis(code: str, filename: str, language: str, llm_provider: str, db: Session) -> AnalysisResponse:
    if not code or not code.strip():
        raise HTTPException(status_code=400, detail="Source code cannot be empty.")

    # 1. Line count metrics
    line_stats = calculate_lines_metrics(code)
    
    # 2. Language specific AST & Security static analysis
    issues = []
    functions_count = 0
    classes_count = 0

    if language.lower() in ["python", "py"]:
        ast_res = analyze_python_ast(code)
        functions_count = ast_res["functions_count"]
        classes_count = ast_res["classes_count"]
        issues.extend(ast_res["ast_issues"])

    # 3. Security vulnerability scan
    sec_issues = scan_security_issues(code)
    issues.extend(sec_issues)

    # 4. Complexity & Maintainability metrics
    cyclomatic_complexity = calculate_complexity(code, language)
    maintainability_idx = calculate_maintainability(code, cyclomatic_complexity, line_stats["code_lines"])
    
    # 5. Quantitative Scoring
    critical_count = sum(1 for item in issues if item.get("severity") == "critical")
    sec_issues_count = sum(1 for item in issues if item.get("type") == "security")
    scores = compute_overall_scores(sec_issues_count, critical_count, maintainability_idx, cyclomatic_complexity)

    # Build CodeMetrics schema
    metrics = CodeMetrics(
        total_lines=line_stats["total_lines"],
        code_lines=line_stats["code_lines"],
        comment_lines=line_stats["comment_lines"],
        blank_lines=line_stats["blank_lines"],
        functions_count=functions_count,
        classes_count=classes_count,
        cyclomatic_complexity=cyclomatic_complexity,
        maintainability_index=maintainability_idx,
        security_score=scores["security_score"],
        overall_score=scores["overall_score"],
        risk_level=scores["risk_level"]
    )

    # 6. AI/LLM Review & Refactored Code Generation
    llm_res = analyze_with_llm(code, language, issues, provider=llm_provider)

    # 7. Persist to Database
    issue_objects = [issue for issue in issues]
    db_report = CodeAnalysisReport(
        filename=filename,
        language=language,
        code_content=code,
        overall_score=scores["overall_score"],
        security_score=scores["security_score"],
        maintainability_index=maintainability_idx,
        cyclomatic_complexity=cyclomatic_complexity,
        metrics=metrics.model_dump(),
        issues=issue_objects,
        refactored_code=llm_res["refactored_code"],
        explanation=llm_res["explanation"]
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)

    return AnalysisResponse(
        id=db_report.id,
        filename=filename,
        language=language,
        metrics=metrics,
        issues=[IssueItem(**item) for item in issue_objects],
        refactored_code=llm_res["refactored_code"],
        explanation=llm_res["explanation"],
        created_at=db_report.created_at
    )


@router.post("/text", response_model=AnalysisResponse)
def analyze_text_code(submission: CodeSubmission, db: Session = Depends(get_db)):
    return _perform_analysis(
        code=submission.code,
        filename=submission.filename or "snippet.py",
        language=submission.language or "python",
        llm_provider=submission.llm_provider or "auto",
        db=db
    )


@router.post("/file", response_model=AnalysisResponse)
async def analyze_file_code(
    file: UploadFile = File(...),
    llm_provider: Optional[str] = Form("auto"),
    db: Session = Depends(get_db)
):
    content_bytes = await file.read()
    try:
        code_text = content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Uploaded file must be UTF-8 text.")

    ext = file.filename.split(".")[-1].lower() if "." in file.filename else "py"
    lang_map = {
        "py": "python", "js": "javascript", "ts": "typescript",
        "java": "java", "cpp": "cpp", "c": "c", "cs": "csharp",
        "go": "go", "rs": "rust", "php": "php", "rb": "ruby"
    }
    language = lang_map.get(ext, ext)

    return _perform_analysis(
        code=code_text,
        filename=file.filename,
        language=language,
        llm_provider=llm_provider,
        db=db
    )
