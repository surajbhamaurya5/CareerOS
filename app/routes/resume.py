import os
import shutil
import json
import re
import tempfile

from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import ResumeAnalysis
from app.utils.pdf_reader import extract_text_from_pdf
from app.services.ai_service import analyze_resume


router = APIRouter()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post("/resume/upload/{student_id}")
def upload_resume(
    student_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    # =========================================================
    # 1. VALIDATE PDF
    # =========================================================

    if not file.filename:
        return {
            "error": "No file selected"
        }

    if not file.filename.lower().endswith(".pdf"):
        return {
            "error": "Only PDF files are allowed"
        }


    # =========================================================
    # 2. CREATE SAFE TEMPORARY FILE
    # =========================================================

    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    )

    file_path = temp_file.name

    try:

        # =====================================================
        # 3. SAVE UPLOADED PDF
        # =====================================================

        with temp_file:
            shutil.copyfileobj(
                file.file,
                temp_file
            )


        print(f"Resume saved temporarily at: {file_path}")


        # =====================================================
        # 4. EXTRACT TEXT FROM PDF
        # =====================================================

        text = extract_text_from_pdf(file_path)

        if not text or not text.strip():

            return {
                "error": "Could not extract text from the PDF. "
                         "The PDF may be scanned/image-based."
            }


        print("Resume text extracted successfully.")


        # =====================================================
        # 5. AI RESUME ANALYSIS
        # =====================================================

        analysis = analyze_resume(text)

        print("AI resume analysis received.")


        # =====================================================
        # 6. CLEAN AI RESPONSE
        # =====================================================

        analysis = re.sub(
            r"```json\s*|\s*```",
            "",
            analysis
        ).strip()


        # =====================================================
        # 7. CONVERT AI RESPONSE TO JSON
        # =====================================================

        try:

            analysis = json.loads(analysis)

        except json.JSONDecodeError as e:

            print("AI returned invalid JSON:")
            print(analysis)

            return {
                "error": "AI returned an invalid analysis format.",
                "details": str(e)
            }


        # =====================================================
        # 8. GET VALUES SAFELY
        # =====================================================

        skills = analysis.get("skills", [])
        education = analysis.get("education", [])
        projects = analysis.get("projects", [])
        experience = analysis.get("experience", [])
        certifications = analysis.get("certifications", [])


        # =====================================================
        # 9. SAVE ANALYSIS TO DATABASE
        # =====================================================

        resume_analysis = ResumeAnalysis(
            student_id=student_id,
            filename=file.filename,
            skills=json.dumps(skills),
            education=json.dumps(education),
            projects=json.dumps(projects),
            experience=json.dumps(experience),
            certifications=json.dumps(certifications)
        )

        db.add(resume_analysis)
        db.commit()
        db.refresh(resume_analysis)


        print(
            f"Resume analysis saved successfully. "
            f"ID: {resume_analysis.id}"
        )


        # =====================================================
        # 10. RETURN RESULT TO FRONTEND
        # =====================================================

        return {
            "id": resume_analysis.id,
            "filename": file.filename,
            "analysis": analysis
        }


    except Exception as e:

        # =====================================================
        # ERROR HANDLING
        # =====================================================

        print("Resume processing error:")
        print(type(e).__name__, e)

        db.rollback()

        return {
            "error": "Resume processing failed.",
            "details": str(e)
        }


    finally:

        # =====================================================
        # 11. ALWAYS DELETE TEMP FILE
        # =====================================================

        if os.path.exists(file_path):

            try:
                os.remove(file_path)
                print("Temporary resume file deleted.")

            except OSError as e:
                print(
                    f"Warning: Could not delete temporary file: {e}"
                )


# =============================================================
# GET LATEST RESUME ANALYSIS
# =============================================================

@router.get("/resume/{student_id}")
def get_resume_analysis(
    student_id: int,
    db: Session = Depends(get_db)
):

    resume = (
        db.query(ResumeAnalysis)
        .filter(
            ResumeAnalysis.student_id == student_id
        )
        .order_by(
            ResumeAnalysis.id.desc()
        )
        .first()
    )


    if not resume:

        return {
            "message": "No resume analysis found"
        }


    return {
        "id": resume.id,
        "student_id": resume.student_id,
        "filename": resume.filename,

        "skills": json.loads(resume.skills),

        "education": json.loads(
            resume.education
        ),

        "projects": json.loads(
            resume.projects
        ),

        "experience": json.loads(
            resume.experience
        ),

        "certifications": json.loads(
            resume.certifications
        )
    }