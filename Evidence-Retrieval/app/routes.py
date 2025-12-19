from fastapi import APIRouter
from pydantic import BaseModel
from app.pipeline import verify_claim_pipeline

router = APIRouter()


class ClaimRequest(BaseModel):
    claim: str


@router.post("/api/verify")
def verify_claim(request: ClaimRequest):
    return verify_claim_pipeline(request.claim)
