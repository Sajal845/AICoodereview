from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import CodeAnalysisReport
from app.schemas import HistoryItemResponse, AnalysisResponse, CodeMetrics, IssueItem

router = APIRouter(prefix="/api/history", tags=["History"])

@router.get("", response_model=List[HistoryItemResponse])
def get_analysis_history(db: Session = Depends(get_db)):
    reports = db.query(CodeAnalysisReport).order_by(CodeAnalysisReport.created_at.desc()).all()
    result = []
    for r in reports:
        issues_list = r.issues if isinstance(r.issues, list) else []
        result.append(HistoryItemResponse(
            id=r.id,
            filename=r.filename,
            language=r.language,
            overall_score=r.overall_score,
            security_score=r.security_score,
            issues_count=len(issues_list),
            created_at=r.created_at
        ))
    return result

@router.get("/{report_id}", response_model=AnalysisResponse)
def get_report_detail(report_id: int, db: Session = Depends(get_db)):
    r = db.query(CodeAnalysisReport).filter(CodeAnalysisReport.id == report_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Analysis report not found.")

    raw_metrics = r.metrics or {}
    metrics = CodeMetrics(**raw_metrics)
    raw_issues = r.issues or []
    issues = [IssueItem(**i) for i in raw_issues]

    return AnalysisResponse(
        id=r.id,
        filename=r.filename,
        language=r.language,
        metrics=metrics,
        issues=issues,
        refactored_code=r.refactored_code or "",
        explanation=r.explanation or "",
        created_at=r.created_at
    )

@router.delete("/{report_id}")
def delete_report(report_id: int, db: Session = Depends(get_db)):
    r = db.query(CodeAnalysisReport).filter(CodeAnalysisReport.id == report_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Analysis report not found.")
    db.delete(r)
    db.commit()
    return {"message": "Report deleted successfully", "id": report_id}
