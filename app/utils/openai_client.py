import os
import openai
from dotenv import load_dotenv
import json

load_dotenv()
openai.api_key = os.getenv("GPT_API_KEY")

async def evaluate_code_with_openai(language: str, code: str, description: str,
                                    input_constraints: str, output_constraints: str,
                                    passed: int, total: int) -> dict:
    # JSON 중괄호를 이스케이프하기 위해 {{ }} 사용
    prompt = f"""
아래는 사용자가 작성한 코드입니다.

언어 : {language}

설명 : {description}
입력 제약 조건 : {input_constraints}
출력 제약 조건 : {output_constraints}
사용자가 작성한 코드 :
---
{code}
---
이 코드는 테스트케이스를 모두 (맞춘 개수) / 전체 개수. : {passed} / {total} 입니다.

이 코드를 다음 기준으로 평가해주세요. 각 항목은 10점 만점입니다.
1. 정확성 (Accuracy)
2. 효율성 (Efficiency)
3. 가독성 (Readability)
4. 테스트 커버리지 (Test Coverage)

테스트커버리지가 다 맞았다면 10점 맞춘 개수 / 전체 테스트케이스 개수로 계산해주세요.

결과는 다음 JSON 형식으로 반환해주세요:
{{
  "accuracy": 정수,
  "efficiency": 정수,
  "readability": 정수,
  "test_coverage": 정수,
  "feedback": "문자열"
}}

*주의*:
- "feedback" 필드에는
  1. 바꿔야 할 부분
  2. 어떻게 수정할지
  3. 점수가 낮은 이유(테스트 커버리지 포함)
  를 번호 형태(1., 2., 3.)로 작성해주세요.
  4. 만약 모든 점수가 10점 만점이라면 축하합니다! 다음 문제를 풀어보세요! 라고 작성해주세요.
- JSON 스키마는 절대 변경하지 마세요.
"""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=0.7,
        messages=[
            {"role": "system", "content": "넌 친절한 코딩 평가자야."},
            {"role": "user", "content": prompt},
        ],
    )
    content = response["choices"][0]["message"]["content"].strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        # 로그 출력 후 기본 피드백 반환
        print("❌ JSON decode error from OpenAI:", e)
        print("Response content was:\n", content)
        # 기본값 설정
        return {
            "accuracy": 0,
            "efficiency": 0,
            "readability": 0,
            "test_coverage": 0,
            "feedback": (
                "OpenAI 응답이 JSON 형식이 아닙니다.\n"
                "원본 응답:\n" + content.replace('"', '\\"')
            )
        }