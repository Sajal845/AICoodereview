from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import analyze, history

# Initialize SQLite database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Code Review & Bug Detection API",
    description="FastAPI Service for Automated AST Parsing, Security Vulnerability Scanning, and AI Refactoring",
    version="1.0.0"
)

# Enable CORS for cross-origin frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount APIRouters
app.include_router(analyze.router)
app.include_router(history.router)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "AI Code Review & Bug Detection API",
        "docs": "/docs"
    }

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    from fastapi.responses import Response
    return Response(status_code=204)

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
