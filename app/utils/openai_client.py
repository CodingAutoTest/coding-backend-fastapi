import os
import openai
from dotenv import load_dotenv
import json

load_dotenv()

openai.api_key = os.getenv("GPT_API_KEY")

async def evaluate_code_with_openai(language: str, code: str) -> dict:
    prompt = f"""
아래는 사용자가 작성한 코드입니다.

언어: {language}

코드:
---
{code}
---

이 코드를 다음 기준으로 평가해주세요. 각 항목은 10점 만점입니다.
1. 정확성 (Accuracy)
2. 효율성 (Efficiency)
3. 가독성 (Readability)
4. 테스트 커버리지 (Test Coverage)

그리고 코드 전반에 대한 피드백을 작성해주세요 현재 코드에서 바꿔야할 부분을 알려주며

결과는 다음 JSON 형식으로 반환해주세요:
{{
  "accuracy": 정수,
  "efficiency": 정수,
  "readability": 정수,
  "test_coverage": 정수,
  "feedback": "문자열"
}}
"""

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=0.7,
        messages=[
            {"role": "system", "content": "넌 친절한 코딩 평가자야."},
            {"role": "user", "content": prompt},
        ],
    )
    content = response["choices"][0]["message"]["content"]
    
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        print("❌ JSON decode error from OpenAI:", e)
        raise ValueError("OpenAI 응답이 JSON 형식이 아닙니다.")
