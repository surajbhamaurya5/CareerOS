from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

import json
import re

from app.database import SessionLocal
from app.models import (
    Student,
    ResumeAnalysis,
    CareerRoadmap
)

from app.services.ai_service import (
    analyze_skill_gap,
    generate_career_roadmap
)


router = APIRouter()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


class RoadmapRequest(BaseModel):
    student_id: int
    target_role: str


@router.post("/roadmap")
def roadmap(
    data: RoadmapRequest,
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

    # Current skills
    current_skills = json.loads(resume.skills)

    # Generate skill gap
    skill_gap = analyze_skill_gap(
        current_skills,
        data.target_role
    )

    skill_gap = re.sub(
        r"```json\s*|\s*```",
        "",
        skill_gap
    ).strip()

    skill_gap = json.loads(skill_gap)

    missing_skills = skill_gap["missing_skills"]

    # Generate roadmap
    result = generate_career_roadmap(
        current_skills,
        missing_skills,
        data.target_role
    )

    result = re.sub(
        r"```json\s*|\s*```",
        "",
        result
    ).strip()

    result = json.loads(result)

    # Save roadmap
    roadmap_data = CareerRoadmap(
        student_id=data.student_id,
        target_role=data.target_role,
        roadmap=json.dumps(result["roadmap"])
    )

    db.add(roadmap_data)
    db.commit()
    db.refresh(roadmap_data)

    return {
        "id": roadmap_data.id,
        "student_id": data.student_id,
        "target_role": data.target_role,
        "roadmap": result["roadmap"]
    }
@router.get("/roadmap/{student_id}")
def get_roadmap(
    student_id: int,
    db: Session = Depends(get_db)
):

    roadmap_data = (
        db.query(CareerRoadmap)
        .filter(CareerRoadmap.student_id == student_id)
        .order_by(CareerRoadmap.id.desc())
        .first()
    )

    if not roadmap_data:
        raise HTTPException(
            status_code=404,
            detail="No career roadmap found"
        )

    return {
        "id": roadmap_data.id,
        "student_id": roadmap_data.student_id,
        "target_role": roadmap_data.target_role,
        "roadmap": json.loads(roadmap_data.roadmap)
    }