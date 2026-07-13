from fastapi import APIRouter

router: APIRouter = APIRouter()

@router.get("/check")
async def check():
    return "Is alive and running!"