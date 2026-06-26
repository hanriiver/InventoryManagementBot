from fastapi import FastAPI

from app.core.scheduler import start_scheduler
from app.routers import admin, kakao

app = FastAPI(title="Bar Inventory Bot")

app.include_router(kakao.router)
app.include_router(admin.router)


@app.on_event("startup")
async def on_startup():
    start_scheduler()


@app.get("/health")
async def health():
    return {"status": "ok"}
