import os
import httpx
from dotenv import load_dotenv

load_dotenv()

JUDGE0_URL = os.getenv("JUDGE0_URL")
if not JUDGE0_URL:
    raise RuntimeError("❌ JUDGE0_URL이 .env에 정의되어 있지 않습니다.")

async def send_to_judge0(
    language_id: int,
    source_code: str,
    stdin: str,
    cpu_time_limit: float,
    memory_limit: int
) -> dict:
    payload = {
        "language_id": language_id,
        "source_code": source_code,
        "stdin": stdin,
        "cpu_time_limit": cpu_time_limit,
        "memory_limit": memory_limit
    }

    async with httpx.AsyncClient() as client:
        res = await client.post(JUDGE0_URL, json=payload)
        res.raise_for_status()
        return res.json()
