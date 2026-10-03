from pydantic import BaseModel


class StudentCreate(BaseModel):
    name: str
    education: str | None = None
    skills: str | None = None
    projects: str | None = None
    interests: str | None = None
    target_role: str | None = None
class StudentUpdate(BaseModel):
    name: str | None = None
    education: str | None = None
    skills: str | None = None
    projects: str | None = None
    interests: str | None = None
    target_role: str | None = None

class StudentResponse(StudentCreate):
    id: int

    class Config:
        from_attributes = True