from pydantic import BaseModel
from typing import Optional

class SubmitRequest(BaseModel):
    problem_id: int
    language: str
    code: str
    user_id: int

class AiFeedback(BaseModel):
    accuracy: int
    efficiency: int
    readability: int
    test_coverage: int
    feedback: str

class ProblemMeta(BaseModel):
    time_limit: float
    memory_limit: int

class SubmitResponse(BaseModel):
    user_submission_problem_id: int