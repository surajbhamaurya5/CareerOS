from fastapi import APIRouter
from app.services.ai_service import ask_ai

router = APIRouter()


@router.get("/test-ai")
def test_ai():
    answer = ask_ai(
        "Explain what a Data Scientist does in 2 simple sentences."
    )

    return {
        "answer": answer
    }