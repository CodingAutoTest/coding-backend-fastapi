from app.schemas.submit import SubmitRequest, SubmitResponse, AiFeedback
from app.utils.judge0 import send_to_judge0
from app.utils.openai_client import evaluate_code_with_openai
from app.models.user_submission_problem import UserSubmissionProblem
from app.models.ai_feedback import AiFeedback as AiFeedbackModel
from app.repositories.user_repository import get_user_by_id, save_user
from app.repositories.testcase_repository import get_testcases_by_problem_id
from app.repositories.problem_repository import get_problem_by_id, save_problem
from app.repositories.language_repository import get_language_id_by_name
from app.repositories.user_submission_problem_repository import save_submission, has_user_solved
from app.repositories.ai_feedback_repository import save_feedback
from app.utils.error_classifier import classify_error

async def evaluate_submission(request: SubmitRequest, db) -> SubmitResponse:
    # 기본 정보 로딩
    problem = await get_problem_by_id(db, request.problem_id)
    testcases = await get_testcases_by_problem_id(db, request.problem_id)
    language_id = await get_language_id_by_name(db, request.language)
    user = await get_user_by_id(db, request.user_id)
    already_solved = await has_user_solved(db, request.user_id, request.problem_id)
    
    # 채점 결과 초기화
    total, passed = len(testcases), 0
    error_msg = None
    total_time = 0.0
    max_memory = 0

    for tc in testcases:
        result = await send_to_judge0(
            language_id=language_id,
            source_code=request.code,
            stdin=tc.input,
            cpu_time_limit=float(problem.time_limit),
            memory_limit=int(problem.memory_limit) * 1024
        )

        output = (result.get("stdout") or "").strip()
        expected = (tc.output or "").strip()
        status = result.get("status", {}).get("description", "Unknown")
        stderr = (result.get("stderr") or "").strip()
        compile_output = (result.get("compile_output") or "").strip()

        if status == "Accepted" and output == expected:
            passed += 1
            error_msg = error_msg or "Accepted"
        else:
            error_msg = error_msg or classify_error(status, compile_output, stderr)

        total_time += float(result.get("time", 0.0))
        max_memory = max(max_memory, int(result.get("memory", 0)))

    # AI 피드백 생성 및 저장
    raw_feedback = await evaluate_code_with_openai(
        request.language, request.code,
        problem.description, problem.input_constraints, problem.output_constraints
    )
    ai_feedback = AiFeedbackModel(**raw_feedback)
    await save_feedback(db, ai_feedback)

    # 제출 결과 처리
    status_flag = 1 if passed == total else 0
    problem.submission_count += 1

    if status_flag == 1:
        problem.correct_count += 1
        if not already_solved:
            user.solved_count += 1
            user.rating += int(problem.difficulty * 10)

    problem.acceptance_rate = (problem.correct_count / problem.submission_count) * 100

    # 제출 저장
    submission = UserSubmissionProblem(
        execution_time=total_time,
        memory_used=max_memory,
        status=status_flag,
        submission_code=request.code,
        ai_feedback_id=ai_feedback.ai_feedback_id,
        language_id=language_id,
        problem_id=request.problem_id,
        user_id=request.user_id,
        passed_count=passed,
        total_count=total,
        error=error_msg
    )

    # DB 저장
    await save_submission(db, submission)
    await save_problem(db, problem)
    await save_user(db, user)

    return SubmitResponse(user_submission_problem_id=submission.user_submission_problem_id)
