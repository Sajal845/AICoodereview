from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON
from datetime import datetime
from app.database import Base

class CodeAnalysisReport(Base):
    __tablename__ = "analysis_reports"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), default="snippet.py")
    language = Column(String(50), default="python")
    code_content = Column(Text, nullable=False)
    
    # Quantitative Scores
    overall_score = Column(Float, default=100.0)
    security_score = Column(Float, default=100.0)
    maintainability_index = Column(Float, default=100.0)
    cyclomatic_complexity = Column(Integer, default=1)
    
    # Detailed Data (JSON payload)
    metrics = Column(JSON, nullable=False)
    issues = Column(JSON, nullable=False)
    refactored_code = Column(Text, nullable=True)
    explanation = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
