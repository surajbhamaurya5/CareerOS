from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

import json
import re

from app.database import SessionLocal
from app.models import Student, ResumeAnalysis, SkillGapAnalysis
from app.services.ai_service import analyze_skill_gap


router = APIRouter()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


class SkillGapRequest(BaseModel):
    student_id: int
    target_role: str


@router.post("/skill-gap")
def skill_gap(
    data: SkillGapRequest,
    db: Session = Depends(get_db)
):

    # Check student
    student = (
        db.query(Student)
        .filter(Student.id == data.student_id)
        .first()
    )

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    # Get latest resume
    resume = (
        db.query(ResumeAnalysis)
        .filter(ResumeAnalysis.student_id == data.student_id)
        .order_by(ResumeAnalysis.id.desc())
        .first()
    )

    if not resume:
        raise HTTPException(
            status_code=404,
            detail="No resume analysis found for this student"
        )

    # Get current skills
    current_skills = json.loads(resume.skills)

    # AI skill gap analysis
    result = analyze_skill_gap(
        current_skills,
        data.target_role
    )

    result = re.sub(
        r"```json\s*|\s*```",
        "",
        result
    ).strip()

    result = json.loads(result)

    # Save result in database
    analysis = SkillGapAnalysis(
        student_id=data.student_id,
        target_role=data.target_role,
        current_skills=json.dumps(result["current_skills"]),
        required_skills=json.dumps(result["required_skills"]),
        missing_skills=json.dumps(result["missing_skills"]),
        priority=json.dumps(result["priority"])
    )

    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    return {
        "id": analysis.id,
        "student_id": data.student_id,
        "result": result
    }

@router.get("/skill-gap/{student_id}")
def get_skill_gap(
    student_id: int,
    db: Session = Depends(get_db)
):

    analysis = (
        db.query(SkillGapAnalysis)
        .filter(SkillGapAnalysis.student_id == student_id)
        .order_by(SkillGapAnalysis.id.desc())
        .first()
    )

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="No skill gap analysis found"
        )

    return {
        "id": analysis.id,
        "student_id": analysis.student_id,
        "target_role": analysis.target_role,
        "current_skills": json.loads(analysis.current_skills),
        "required_skills": json.loads(analysis.required_skills),
        "missing_skills": json.loads(analysis.missing_skills),
        "priority": json.loads(analysis.priority)
    }