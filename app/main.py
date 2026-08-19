from fastapi import FastAPI

from app.api.router import api_router

app = FastAPI(
    title="SupportOps AI",
    version="0.1.0",
)

app.include_router(api_router)