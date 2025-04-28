from app.schemas.submit import SubmitRequest, SubmitResponse, AiFeedback, ProblemMeta
from app.utils.judge0 import send_to_judge0
from app.utils.openai_client import evaluate_code_with_openai
from app.repositories.testcase_repository import get_testcases_by_problem_id
from app.repositories.problem_repository import get_problem_by_id
from app.models.user_submission_problem import UserSubmissionProblem
from app.models.ai_feedback import AiFeedback as AiFeedbackModel
from sqlalchemy.future import select
from app.repositories.language_repository import get_language_id_by_name
from app.repositories.user_submission_problem_repository import save_submission
from app.repositories.ai_feedback_repository import save_feedback

async def evaluate_submission(request: SubmitRequest, db) -> SubmitResponse:
    problem = await get_problem_by_id(db, request.problem_id)
    testcases = await get_testcases_by_problem_id(db, request.problem_id)
    language_id = await get_language_id_by_name(db, request.language)

    total = len(testcases)
    passed = 0
    error_msg = None

    total_execution_time = 0.0
    max_memory_used = 0

    for tc in testcases:
        result = await send_to_judge0(
            language_id=language_id,
            source_code=request.code,
            stdin=tc.input,
            cpu_time_limit=float(problem.time_limit),
            memory_limit=int(problem.memory_limit) * 1024
        )
        output = result.get("stdout", "").strip()
        if output == tc.output.strip():
            passed += 1
        elif result.get("stderr"):
            error_msg = result["stderr"][:50]

        total_execution_time += float(result.get("time", 0.0))
        max_memory_used = max(max_memory_used, int(result.get("memory", 0)))

    feedback_raw = await evaluate_code_with_openai(request.language, request.code)
    feedback = AiFeedback(**feedback_raw)

    ai_feedback = AiFeedbackModel(**feedback_raw)
    
    await save_feedback(db, ai_feedback)

    submission = UserSubmissionProblem(
        execution_time=total_execution_time,
        memory_used=max_memory_used,
        status=1,
        submission_code=request.code,
        ai_feedback_id=ai_feedback.ai_feedback_id,
        language_id=language_id,
        problem_id=request.problem_id,
        user_id=request.user_id,
        passed_count=passed,
        total_count=total,
        error=error_msg
    )

    await save_submission(db, submission)

    return SubmitResponse(user_submission_problem_id=submission.user_submission_problem_id)