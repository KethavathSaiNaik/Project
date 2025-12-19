from fastapi import FastAPI
from app.routes import router

app = FastAPI(
    title="Claim Verification Backend",
    version="1.0"
)

app.include_router(router)
