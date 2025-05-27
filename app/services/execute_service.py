from app.schemas.execute import ExecuteRequest, ExecuteResponse, ExecuteResult
from app.utils.judge0 import send_to_judge0
from app.repositories.testcase_repository import get_testcase_by_id
from app.repositories.problem_repository import get_problem_by_id
from app.repositories.language_repository import get_language_id_by_name
import base64

async def execute_multiple_testcases(request: ExecuteRequest, db) -> ExecuteResponse:
    results = []

    for idx, testcase_id in enumerate(request.testcase_ids, start=1):
        # 1) 테스트케이스 조회
        testcase = await get_testcase_by_id(db, testcase_id)
        if not testcase:
            continue

        # 2) 문제 조회
        problem = await get_problem_by_id(db, testcase.problem_id)
        if not problem:
            continue 
        
        # 3) 언어 ID 조회
        language_id = await get_language_id_by_name(db, request.language)
        if not language_id:
            continue

        # 4) Judge0 실행
        judge0_result = await send_to_judge0(
            language_id    = language_id,
            source_code    = request.code,
            stdin          = testcase.input,
            cpu_time_limit = float(problem.time_limit),
            memory_limit   = int(problem.memory_limit) * 1024
        )

        # 5) Base64 디코딩
        raw_stdout        = judge0_result.get("stdout") or ""
        raw_stderr        = judge0_result.get("stderr") or ""
        raw_compile_output= judge0_result.get("compile_output") or ""

        decoded_stdout       = base64.b64decode(raw_stdout).decode("utf-8").strip()
        decoded_stderr       = base64.b64decode(raw_stderr).decode("utf-8").strip()
        decoded_compile_out  = base64.b64decode(raw_compile_output).decode("utf-8").strip()

        # 6) 비교 및 상태 결정
        expected_output = (testcase.output or "").strip()
        if decoded_stdout == expected_output:
            final_status = "Accepted"
        else:
            final_status = "Wrong Answer"

        # 7) 결과 리스트에 추가
        results.append(ExecuteResult(
            testcase_id = testcase_id,
            stdout      = decoded_stdout,
            stderr      = decoded_stderr,
            time        = judge0_result.get("time", 0.0),
            memory      = judge0_result.get("memory", 0),
            status      = final_status
        ))

    return ExecuteResponse(results=results)
