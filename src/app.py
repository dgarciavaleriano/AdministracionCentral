from fastapi import FastAPI, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.requests import Request

from api.routers import health, users
from config.settings import settings

app = FastAPI(
    title="API administración central",
    description="API principal para el proyecto administración central",
    version=settings.api_version,
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder({"detail": exc.errors()}),
    )


app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(health.router, prefix="/health", tags=["health"])
