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
    # 사용자 코드 및 Judge0 결과를 기반으로 AI 평가를 요청합니다.
    # 반드시 순수 JSON만 응답하도록 지시합니다.
    prompt = f"""
아래는 사용자가 작성한 정보와 채점 결과입니다. 이 내용을 바탕으로 평가를 수행하세요.

-- 입력 정보 --
• 언어: {language}
• 설명: {description}
• 입력 제약 조건: {input_constraints}
• 출력 제약 조건: {output_constraints}
• 코드:
```
{code}
```
• 테스트 통과 개수: {passed} / {total}
• Judge0 상태: {judge0_status}
• Judge0 에러 상세:
```
{judge0_stderr}
```

-- 평가 기준 (각 항목 10점 만점) --
1. 정확성 (Accuracy):
   문제 명세와 요구사항 충족 여부
2. 효율성 (Efficiency):
   시간 복잡도와 공간 복잡도를 고려하여 평가
3. 가독성 (Readability):
   설명 및 제약 조건과 코드 구조, 변수명, 주석 등을 참고하여 평가
4. 테스트 커버리지 (Test Coverage):
   통과된 테스트 수 / 전체 테스트 수 비율로 계산

-- 조건 --
1. judge0_status가 "Accepted"이면 accuracy를 10점으로 설정하세요.
2. judge0_stderr가 비어있지 않으면, feedback 필드 시작에 반드시 다음 형식으로 포함하세요:

   ERROR! : {judge0_stderr}

3. feedback에는 각 항목에 대한 점수 산정 이유와 개선 방안을 번호(1., 2., 3.)로 작성하고,
   각 번호 사이에 빈 줄 하나를 넣어 가독성을 높이세요.
4. 모든 항목 점수가 10점이면, feedback에는 "축하합니다! 모든 테스트를 통과했습니다. 다음 문제를 도전해보세요!"라는 한 문장만 포함하세요.
5. 에러가 발생한 경우 몇번째 줄에서 무슨 에러가 발생했는지 설명하고 정답을 간접적으로 알려주세요.

-- 응답 규칙 --
- **절대** JSON 이외의 출력은 금지됩니다.
- 출력은 아래 JSON 스키마로만 구성되어야 합니다.

-- 응답 JSON 스키마 --
```json
{{
  "accuracy": <정수>,
  "efficiency": <정수>,
  "readability": <정수>,
  "test_coverage": <정수>,
  "feedback": "<문자열>"
}}
```
"""

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=0.7,
        messages=[
            {"role": "system", "content": "너는 친절한 코드 평가자야. 응답은 JSON 오브젝트 하나로만 출력해야 해."},
            {"role": "user",   "content": prompt},
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
