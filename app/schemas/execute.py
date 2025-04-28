from pydantic import BaseModel
from typing import List, Optional

class ExecuteRequest(BaseModel):
    code: str
    language: str
    testcase_ids: List[int]

class ExecuteResult(BaseModel):
    testcase_id: int
    stdout: str
    stderr: Optional[str]
    time: float
    memory: int
    status: str

class ExecuteResponse(BaseModel):
    results: List[ExecuteResult]