from fastapi import APIRouter

router: APIRouter = APIRouter()

@router.get("/")
async def hello_world():
    return "Hello from administracioncentral!"