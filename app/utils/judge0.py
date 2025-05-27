import os
import httpx
import base64
from dotenv import load_dotenv, find_dotenv

# 1) .env 자동 로드 (override=True 로 시스템 변수 덮어쓰기)
dotenv_path = find_dotenv(usecwd=True)
if not dotenv_path:
    raise RuntimeError("❌ 프로젝트 루트에 .env 파일이 없습니다.")
load_dotenv(dotenv_path, override=True)

# 2) JUDGE0_URL 읽어오기 및 보정
raw_url = os.getenv("JUDGE0_URL", "").strip()
if not raw_url:
    raise RuntimeError("❌ .env에 JUDGE0_URL이 정의되어 있지 않습니다.")

# unicode_escape 디코딩으로 '\x3a' 같은 시퀀스 해제
raw_url = raw_url.encode("utf-8").decode("unicode_escape")

if not raw_url.startswith(("http://", "https://")):
    raw_url = "http://" + raw_url
if not raw_url.rstrip("/").endswith("/submissions"):
    raw_url = raw_url.rstrip("/") + "/submissions"

JUDGE0_URL = raw_url

async def send_to_judge0(
    language_id: int,
    source_code: str,
    stdin: str = "",
    cpu_time_limit: float = 1.0,
    memory_limit: int = 512000,
) -> dict:
    encoded_code = base64.b64encode(source_code.encode("utf-8")).decode("utf-8")
    encoded_stdin = base64.b64encode(stdin.encode("utf-8")).decode("utf-8")
    payload = {
        "language_id":    language_id,
        "source_code":    encoded_code,
        "stdin":          encoded_stdin,
        "cpu_time_limit": cpu_time_limit,
        "memory_limit":   memory_limit,
    }

    url = f"{JUDGE0_URL}/?base64_encoded=true&wait=true"
    async with httpx.AsyncClient() as client:
        res = await client.post(url, json=payload)
        res.raise_for_status()
        return res.json()
