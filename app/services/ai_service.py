import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

MODEL = "openrouter/free"

URL = "https://openrouter.ai/api/v1/chat/completions"


# =========================================================
# COMMON AI FUNCTION
# =========================================================

def ask_ai(prompt: str):

    if not OPENROUTER_API_KEY:
        raise Exception("OPENROUTER_API_KEY is missing in .env")

    response = requests.post(
        URL,
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.2,
        },
        timeout=120,
    )

    if response.status_code != 200:
        raise Exception(
            f"OpenRouter Error {response.status_code}: {response.text}"
        )

    data = response.json()

    return data["choices"][0]["message"]["content"]


# =========================================================
# CLEAN JSON RESPONSE
# =========================================================

def clean_json_response(result: str):

    result = result.strip()

    # Remove markdown code fences
    if result.startswith("```"):
        result = result.replace("```json", "")
        result = result.replace("```", "")
        result = result.strip()

    return result


# =========================================================
# RESUME ANALYSIS
# =========================================================

def analyze_resume(text: str):

    prompt = f"""
You are a professional resume analyzer.

Analyze the following resume.

Return ONLY valid JSON.
Do not write anything before or after the JSON.

Required JSON structure:

{{
    "name": "",
    "email": "",
    "phone": "",
    "skills": [],
    "education": [],
    "projects": [],
    "experience": [],
    "certifications": [],
    "summary": "",
    "strengths": [],
    "weaknesses": [],
    "missing_sections": [],
    "ats_score": 0
}}

Rules:

1. Do not invent information.
2. If information is not present, return an empty string or empty list.
3. ATS score must be between 0 and 100.
4. Keep the analysis concise.
5. Return JSON only.

RESUME:

{text}
"""

    result = ask_ai(prompt)

    result = clean_json_response(result)

    # Validate JSON before returning
    try:
        json.loads(result)
        return result

    except json.JSONDecodeError:

        # Safe fallback
        fallback = {
            "name": "",
            "email": "",
            "phone": "",
            "skills": [],
            "education": [],
            "projects": [],
            "experience": [],
            "certifications": [],
            "summary": result,
            "strengths": [],
            "weaknesses": [],
            "missing_sections": [],
            "ats_score": 0
        }

        return json.dumps(fallback)


# =========================================================
# SKILL GAP ANALYSIS
# =========================================================

def analyze_skill_gap(current_skills, target_role):

    prompt = f"""
You are a career and skill-gap analyst.

Analyze the student's current skills for the target job role.

Target Role:
{target_role}

Current Skills:
{json.dumps(current_skills)}

Return ONLY valid JSON.

Required JSON structure:

{{
    "target_role": "",
    "current_skills": [],
    "required_skills": [],
    "missing_skills": [],
    "priority": []
}}

Rules:

1. Do not invent student's current skills.
2. current_skills must contain only skills provided by the student.
3. required_skills should contain realistic skills required for the target role.
4. missing_skills should contain skills required but missing from current_skills.
5. priority should contain the most important missing skills to learn first.
6. Return JSON only.
"""

    result = ask_ai(prompt)

    result = clean_json_response(result)

    try:
        json.loads(result)
        return result

    except json.JSONDecodeError:

        fallback = {
            "target_role": target_role,
            "current_skills": current_skills,
            "required_skills": [],
            "missing_skills": [],
            "priority": []
        }

        return json.dumps(fallback)


# =========================================================
# PLACEMENT INTELLIGENCE
# =========================================================

def generate_placement_intelligence(
    target_role,
    current_skills,
    missing_skills
):

    prompt = f"""
You are a placement preparation expert.

Create a placement preparation analysis for a student.

Target Role:
{target_role}

Current Skills:
{json.dumps(current_skills)}

Missing Skills:
{json.dumps(missing_skills)}

Return ONLY valid JSON.

Required JSON structure:

{{
    "technical_topics": [],
    "dsa_topics": [],
    "interview_topics": [],
    "important_projects": [],
    "preparation_priorities": []
}}

Rules:

1. Focus on realistic placement preparation.
2. technical_topics should contain important technical subjects for the target role.
3. dsa_topics should contain important DSA topics for placement interviews.
4. interview_topics should contain important interview preparation areas.
5. important_projects should contain useful project types the student should build.
6. preparation_priorities should be ordered by importance.
7. Return JSON only.
"""

    result = ask_ai(prompt)

    result = clean_json_response(result)

    try:
        json.loads(result)
        return result

    except json.JSONDecodeError:

        fallback = {
            "technical_topics": [],
            "dsa_topics": [],
            "interview_topics": [],
            "important_projects": [],
            "preparation_priorities": []
        }

        return json.dumps(fallback)


# =========================================================
# CAREER ROADMAP
# =========================================================

def generate_career_roadmap(
    current_skills,
    missing_skills,
    target_role
):

    prompt = f"""
You are a career roadmap planner.

Create a practical learning roadmap for a student.

Target Role:
{target_role}

Current Skills:
{json.dumps(current_skills)}

Missing Skills:
{json.dumps(missing_skills)}

Return ONLY valid JSON.

Required JSON structure:

{{
    "roadmap": []
}}

Each roadmap item should contain:

{{
    "phase": "",
    "duration": "",
    "topics": [],
    "projects": [],
    "outcome": ""
}}

Rules:

1. Start from the student's current skill level.
2. Focus on skills required for the target role.
3. Put topics in a logical learning order.
4. Include practical projects.
5. Keep the roadmap realistic for a college student.
6. Return JSON only.
"""

    result = ask_ai(prompt)

    result = clean_json_response(result)

    try:
        json.loads(result)
        return result

    except json.JSONDecodeError:

        fallback = {
            "roadmap": []
        }

        return json.dumps(fallback)