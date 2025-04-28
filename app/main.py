from fastapi import FastAPI
from app.api.routes import execute
from app.api.routes import submit
from app import models


app = FastAPI()
app.include_router(execute.router, prefix="/api", tags=["Execute"])
app.include_router(submit.router, prefix="/api", tags=["Submit"])

