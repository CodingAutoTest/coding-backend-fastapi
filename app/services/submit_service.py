import base64
from app.schemas.submit import SubmitRequest, SubmitResponse
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
    # 1) 기본 정보 로딩
    problem        = await get_problem_by_id(db, request.problem_id)
    testcases      = await get_testcases_by_problem_id(db, request.problem_id)
    language_id    = await get_language_id_by_name(db, request.language)
    user           = await get_user_by_id(db, request.user_id)
    already_solved = await has_user_solved(db, request.user_id, request.problem_id)

    total          = len(testcases)
    passed         = 0
    judge0_status  = "Unknown"
    total_time     = 0.0
    max_memory     = 0
    case_details   = []  # 모든 케이스 정보를 담을 리스트

    # 2) 각 테스트케이스별 Judge0 호출 및 디코딩
    for idx, tc in enumerate(testcases, start=1):
        result = await send_to_judge0(
            language_id    = language_id,
            source_code    = request.code,
            stdin          = tc.input,
            cpu_time_limit = float(problem.time_limit),
            memory_limit   = int(problem.memory_limit) * 1024,
        )

        # Base64 디코딩
        stdout_b64     = result.get("stdout") or b""
        stderr_b64     = result.get("stderr") or b""
        compile_b64    = result.get("compile_output") or b""

        output         = base64.b64decode(stdout_b64).decode("utf-8").strip()
        stderr         = base64.b64decode(stderr_b64).decode("utf-8").strip()
        compile_output = base64.b64decode(compile_b64).decode("utf-8").strip()
        status         = result.get("status", {}).get("description", "Unknown")
        expected       = (tc.output or "").strip()

        # 통과 여부 판정
        passed_flag = (status == "Accepted" and output == expected)
        if passed_flag:
            passed += 1

        # 케이스별 상세 정보 수집 (성공/실패 모두 포함)
        detail = (
            f"[TC {idx}] - {'OK' if passed_flag else 'FAIL'}\n"
            f"  입력값: {tc.input!r}\n"
            f"  예상값: {expected!r}\n"
            f"  실제값: {output!r}\n"
            f"  상태: {status}\n"
            f"  stderr: {(stderr or compile_output)!r}"
        )
        case_details.append(detail)

        judge0_status = status
        total_time   += float(result.get("time", 0.0))
        max_memory    = max(max_memory, int(result.get("memory", 0)))

    # 3) 모든 케이스 정보를 하나의 문자열로 합치기
    judge0_stderr = "\n\n".join(case_details)

    # 4) AI 피드백 생성 및 저장
    raw_fb      = await evaluate_code_with_openai(
        request.language,
        request.code,
        problem.description,
        problem.input_constraints,
        problem.output_constraints,
        passed,
        total,
        judge0_status,
        judge0_stderr
    )
    ai_feedback = AiFeedbackModel(**raw_fb)
    await save_feedback(db, ai_feedback)

    # 5) 통계 업데이트
    success_flag = (passed == total)
    problem.submission_count += 1
    if success_flag:
        problem.correct_count += 1
        if not already_solved:
            user.solved_count += 1
            user.rating += int(problem.difficulty * 10)
    problem.acceptance_rate = (problem.correct_count / problem.submission_count) * 100

    # 6) 제출 기록 저장
    submission = UserSubmissionProblem(
        execution_time  = total_time,
        memory_used     = max_memory,
        status          = 1 if success_flag else 0,
        submission_code = request.code,
        ai_feedback_id  = ai_feedback.ai_feedback_id,
        created_by      = user.user_id,
        language_id     = language_id,
        problem_id      = request.problem_id,
        user_id         = request.user_id,
        passed_count    = passed,
        total_count     = total,
        judge0_stderr   = judge0_stderr,
        judge0_status   = judge0_status,
    )
    await save_submission(db, submission)
    await save_problem(db, problem)
    await save_user(db, user)

    return SubmitResponse(user_submission_problem_id=submission.user_submission_problem_id)
