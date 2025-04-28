from fastapi import APIRouter, Depends
from app.schemas.submit import SubmitRequest, SubmitResponse
from app.services.submit_service import evaluate_submission
from app.deps.db import get_db

router = APIRouter()

@router.post("/submit", response_model=SubmitResponse)
async def submit_code(request: SubmitRequest, db=Depends(get_db)):
    return await evaluate_submission(request, db)