from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

import json
import re

from app.database import SessionLocal
from app.models import (
    Student,
    ResumeAnalysis,
    PlacementIntelligence
)

from app.services.ai_service import (
    analyze_skill_gap,
    generate_placement_intelligence
)


router = APIRouter()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


class PlacementRequest(BaseModel):
    student_id: int
    target_role: str


@router.post("/placement")
def placement(
    data: PlacementRequest,
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

    # Generate placement intelligence
    result = generate_placement_intelligence(
        data.target_role,
        current_skills,
        missing_skills
    )

    result = re.sub(
        r"```json\s*|\s*```",
        "",
        result
    ).strip()

    result = json.loads(result)

    # Save placement intelligence
    placement_data = PlacementIntelligence(
        student_id=data.student_id,
        target_role=data.target_role,
        technical_topics=json.dumps(result["technical_topics"]),
        dsa_topics=json.dumps(result["dsa_topics"]),
        interview_topics=json.dumps(result["interview_topics"]),
        important_projects=json.dumps(result["important_projects"]),
        preparation_priorities=json.dumps(
            result["preparation_priorities"]
        )
    )

    db.add(placement_data)
    db.commit()
    db.refresh(placement_data)

    return {
        "id": placement_data.id,
        "student_id": data.student_id,
        "target_role": data.target_role,
        "placement_intelligence": result
    }

@router.get("/placement/{student_id}")
def get_placement_intelligence(
    student_id: int,
    db: Session = Depends(get_db)
):

    placement = (
        db.query(PlacementIntelligence)
        .filter(PlacementIntelligence.student_id == student_id)
        .order_by(PlacementIntelligence.id.desc())
        .first()
    )

    if not placement:
        raise HTTPException(
            status_code=404,
            detail="No placement intelligence found"
        )

    return {
        "id": placement.id,
        "student_id": placement.student_id,
        "target_role": placement.target_role,
        "technical_topics": json.loads(
            placement.technical_topics
        ),
        "dsa_topics": json.loads(
            placement.dsa_topics
        ),
        "interview_topics": json.loads(
            placement.interview_topics
        ),
        "important_projects": json.loads(
            placement.important_projects
        ),
        "preparation_priorities": json.loads(
            placement.preparation_priorities
        )
    }