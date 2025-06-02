import os
import openai
from dotenv import load_dotenv
import json

load_dotenv()
openai.api_key = os.getenv("GPT_API_KEY")

async def evaluate_code_with_openai(
    language: str,
    code: str,
    description: str,
    input_constraints: str,
    output_constraints: str,
    passed: int,
    total: int,
    judge0_status: str,
    judge0_stderr: str,
) -> dict:
    # 1) system 메시지에 평가 기준, 조건, JSON 스키마 지시와
    #    초·중학생 눈높이로 설명하라는 지시를 모두 넣습니다.
    system_prompt = """
    너는 친절한 코드 평가자야. 이 평가는 초등학생·중학생도 이해할 수 있도록 아주 쉽게 써야 해. 
    아래 지시사항을 반드시 따라야 해. 

    응답은 순수 JSON 오브젝트 하나로만 출력해야 하며, 그 외의 출력은 절대 허용되지 않아.

    -- 평가 기준 (각 항목 10점 만점) --
    1. 정확성 (Accuracy):
    문제에서 원하는 대로 정확하게 동작했는지 확인해 줘.
    2. 효율성 (Efficiency):
    코드가 너무 느리거나 메모리를 많이 쓰면 점수를 조금 깎아 줘.
    3. 가독성 (Readability):
    변수 이름, 주석, 코드 모양을 보고 다른 친구가 읽을 때 이해하기 쉬운지 판단해 줘.
    4. 테스트 커버리지 (Test Coverage):
    통과한 테스트 수/전체 테스트 수 비율로 계산해 줘.

    -- 조건 --
    1. judge0_status가 "Accepted"이면 Accuracy를 10점으로 해 줘.
    2. judge0_stderr에 값이 있으면, feedback 제일 앞에 아래처럼 적어 주고 시작해 줘:
    ERROR! : {judge0_stderr}

    3. feedback에는 아래 순서대로 아주 쉽게 적어 줘:
    1. “무슨 문제인지” (예: “숫자를 받아오는 부분이 빠져서 실행이 안 돼요.”)
    2. “왜 그렇다고 생각하는지” (예: “컴퓨터가 a와 b가 뭔지 몰라서 NameError가 났어요.”)
    3. “어떻게 고치면 되는지” (예시 코드를 보여 주고, “input()으로 먼저 숫자를 받아야 해요.” 같이 설명)
    4. “잘 고친 뒤 어떻게 되는지 예시로 보여 주기” (예: “32 32를 입력하면 64가 나와요.”)
    5. 마지막에 “앞으로 이렇게 해 보세요!” 같은 짧은 격려 문장

    각 번호 사이에는 빈 줄 하나씩 넣어 주어서 읽기 편하게 해 줘.

    4. 모든 항목 점수가 10점이면, feedback에는 “축하합니다! 모든 테스트를 통과했습니다. 다음 문제를 도전해보세요!” 한 문장만 넣어 줘.
    5. 에러가 발생한 경우에는 몇 번째 줄에서 무슨 에러가 났는지 쉽게 설명하고, 정답을 어떻게 하면 되는지도 알려 줘.

    -- 응답 규칙 --
    - **절대** JSON 이외의 출력은 금지됩니다.
    - 출력은 아래 JSON 스키마로만 구성되어야 합니다.

    -- 응답 JSON 스키마 --
    ```json
    {
    "accuracy": <정수>,
    "efficiency": <정수>,
    "readability": <정수>,
    "test_coverage": <정수>,
    "feedback": "<문자열>"
    }

    """

    # 2) user 메시지에는 평가할 코드 및 Judge0 결과만 담습니다.
    user_prompt = f"""
    아래는 사용자가 작성한 정보와 채점 결과입니다. 이 내용을 바탕으로 평가를 수행하세요.

    • 언어 : {language}
    • 설명 : {description}
    • 입력 제약 조건 : {input_constraints}
    • 출력 제약 조건 : {output_constraints}
    • 코드 : {code}
    • 테스트 통과 개수 : {passed} / {total}
    • Judge0 상태 : {judge0_status}
    • Judge0 에러 상세: {judge0_stderr}
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=0.7,
        messages=[
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": user_prompt.strip()},
        ],
    )

    content = response["choices"][0]["message"]["content"].strip()
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        print("❌ JSON decode error:", e)
        print("Response was:\n", content)
        return {
            "accuracy": 0,
            "efficiency": 0,
            "readability": 0,
            "test_coverage": 0,
            "feedback": (
                "OpenAI 응답이 JSON 형식이 아닙니다. 원본 응답:\n" + content.replace('"', '\\"')
            ),
        }
