from fastapi import APIRouter
from pydantic import BaseModel

from app.pipeline import verify_claim_pipeline
from app.explainability_chatbot import answer_user_question

router = APIRouter()


# ============================
# VERIFY CLAIM ROUTE (EXISTING)
# ============================
class ClaimRequest(BaseModel):
    claim: str


@router.post("/api/verify")
def verify_claim(request: ClaimRequest):
    return verify_claim_pipeline(request.claim)


# ============================
# EXPLAINABILITY CHAT ROUTE
# ============================
class ChatRequest(BaseModel):
    query_id: str
    question: str
    label: str
    confidence: float


@router.post("/api/chat")
def explain_decision(request: ChatRequest):
    """
    Interactive explainability chatbot.
    The LLM ONLY explains evidence.
    It does NOT decide truth.
    """
    answer = answer_user_question(
        query_id=request.query_id,
        user_question=request.question,
        final_label=request.label,
        confidence=request.confidence
    )

    return {
        "answer": answer
    }
