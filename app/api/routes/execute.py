from fastapi import APIRouter, Depends
from app.schemas.execute import ExecuteRequest, ExecuteResponse
from app.services.execute_service import execute_multiple_testcases
from app.deps.db import get_db

router = APIRouter()

@router.post("/execute", response_model=ExecuteResponse)
async def run_code(request: ExecuteRequest, db=Depends(get_db)):
    return await execute_multiple_testcases(request, db)
