from fastapi import APIRouter

api = APIRouter()


@api.get("/health")
async def health_check():
    return {"status": "ok"}