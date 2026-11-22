from fastapi import FastAPI, status
from starlette.requests import Request

from api.routers import users
from api.routers import health
from api.routers import documents
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings

app = FastAPI(
    title="API administración central",
    description="API principal para el proyecto administración central",
    version=settings.api_version
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder({"detail": exc.errors()}),
    )

app.include_router(users.router, prefix="/users",
                   tags=["users"])

app.include_router(health.router, prefix="/health",
                   tags=["health"])

app.include_router(documents.router, prefix="/documents",
                   tags=["documents"])

# Permitir peticiones desde el frontend de NiceGUI (ajusta el puerto si es necesario)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)