from fastapi import FastAPI

from app.routers import admin, kakao

app = FastAPI(title="Bar Inventory Bot")

app.include_router(kakao.router)
app.include_router(admin.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
