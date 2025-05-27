from fastapi import FastAPI
from app.api.routes import execute
from app.api.routes import submit
from app import models
from dotenv import load_dotenv, find_dotenv

dotenv_path = find_dotenv(usecwd=True)
if not dotenv_path:
    raise RuntimeError("❌ 프로젝트 루트에 .env 파일이 없습니다.")
load_dotenv(dotenv_path)

app = FastAPI()
app.include_router(execute.router, prefix="/api", tags=["Execute"])
app.include_router(submit.router, prefix="/api", tags=["Submit"])

