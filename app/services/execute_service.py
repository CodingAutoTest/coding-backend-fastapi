from app.schemas.execute import ExecuteRequest, ExecuteResponse, ExecuteResult
from app.utils.judge0 import send_to_judge0
from app.repositories.testcase_repository import get_testcase_by_id
from app.repositories.problem_repository import get_problem_by_id
from app.repositories.language_repository import get_language_id_by_name

async def execute_multiple_testcases(request: ExecuteRequest, db) -> ExecuteResponse:
    results = []

    for testcase_id in request.testcase_ids:
        # 테스트케이스 조회
        testcase = await get_testcase_by_id(db, testcase_id)
        if not testcase:
            continue

        # 문제 조회
        problem = await get_problem_by_id(db, testcase.problem_id)
        if not problem:
            continue 
        
        # 언어 ID 조회
        language_id = await get_language_id_by_name(db, request.language)
        if not language_id:
            continue

        # Judge0로 코드 실행
        judge0_result = await send_to_judge0(
            language_id=language_id,
            source_code=request.code,
            stdin=testcase.input,
            cpu_time_limit=float(problem.time_limit),
            memory_limit=int(problem.memory_limit) * 1024
        )

        # 실행 결과 받아오기
        user_stdout = (judge0_result.get("stdout") or "").strip()
        expected_output = (testcase.output or "").strip()

        # 정답 비교
        if user_stdout == expected_output:
            final_status = "Accepted"
        else:
            final_status = "Wrong Answer"

        results.append(ExecuteResult(
            testcase_id=testcase_id,
            stdout=user_stdout,
            stderr=judge0_result.get("stderr"),
            time=judge0_result.get("time", 0.0),
            memory=judge0_result.get("memory", 0),
            status=final_status
        ))

    return ExecuteResponse(results=results)
