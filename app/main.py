from fastapi import FastAPI
from fastapi.responses import FileResponse
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware

from app.routes.student import router as student_router
from app.database import engine, Base
from app.models import (
    Student,
    ResumeAnalysis,
    SkillGapAnalysis,
    CareerRoadmap,
    PlacementIntelligence
)

from app.routes.placement import router as placement_router
from app.routes.ai import router as ai_router
from app.routes.resume import router as resume_router
from app.routes.skill_gap import router as skill_gap_router
from app.routes.roadmap import router as roadmap_router


# ==========================================
# CREATE DATABASE TABLES
# ==========================================

Base.metadata.create_all(bind=engine)


# ==========================================
# FASTAPI APP
# ==========================================

app = FastAPI(
    title="CareerOS API",
    description="AI-Powered Placement & Skill Intelligence Platform",
    version="1.0.0"
)


# ==========================================
# CORS
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# FRONTEND
# ==========================================

@app.get("/")
def home():
    frontend_path = (
        Path(__file__).resolve().parent.parent
        / "frontend"
        / "index.html"
    )

    return FileResponse(frontend_path)


# ==========================================
# API ROUTES
# ==========================================

app.include_router(ai_router, prefix="/api")
app.include_router(student_router, prefix="/api")
app.include_router(resume_router, prefix="/api")
app.include_router(skill_gap_router, prefix="/api")
app.include_router(roadmap_router, prefix="/api")
app.include_router(placement_router, prefix="/api")