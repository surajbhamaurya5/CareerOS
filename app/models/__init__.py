from sqlalchemy import Column, Integer, String, Text
from app.database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    education = Column(String(200))
    skills = Column(Text)
    projects = Column(Text)
    interests = Column(Text)
    target_role = Column(String(100))
class ResumeAnalysis(Base):
    __tablename__ = "resume_analyses"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, nullable=False)

    filename = Column(String(200))
    skills = Column(Text)
    education = Column(Text)
    projects = Column(Text)
    experience = Column(Text)
    certifications = Column(Text)

class SkillGapAnalysis(Base):
    __tablename__ = "skill_gap_analyses"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, nullable=False)

    target_role = Column(String(100))
    current_skills = Column(Text)
    required_skills = Column(Text)
    missing_skills = Column(Text)
    priority = Column(Text)


class CareerRoadmap(Base):
    __tablename__ = "career_roadmaps"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, nullable=False)

    target_role = Column(String(100))
    roadmap = Column(Text)


class PlacementIntelligence(Base):
    __tablename__ = "placement_intelligence"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, nullable=False)

    target_role = Column(String(100))
    technical_topics = Column(Text)
    dsa_topics = Column(Text)
    interview_topics = Column(Text)
    important_projects = Column(Text)
    preparation_priorities = Column(Text)