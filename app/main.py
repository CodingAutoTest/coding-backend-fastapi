from fastapi import FastAPI
from app.db.database import engine

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(lambda _: None)  # 연결 확인용 더미 쿼리
        print("db 연결 성공")
    except Exception as e:
        print("db 연결 실패", e)
