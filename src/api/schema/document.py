import base64
import uuid
from pydantic import BaseModel, ConfigDict, field_serializer, Field, field_validator
from config.logger import Logging

logging = Logging(__name__)

class DocumentRequest(BaseModel):
    user_id: uuid.UUID = Field(..., description="Uuid del usuario al que pertenece el documento")
    file_name: str = Field(..., description="Nombre del archivo que sube el usuario")
    file_content: bytes = Field(..., description="Contenido del archivo del usuario en base64")

    @field_validator("file_content", mode="after")
    def decode_base64(cls, v: str) -> bytes:
        try:
            return base64.b64decode(v)
        except Exception as e:
            logging.error("El contenido del archivo debe ser una cadena base64 válida", e)
            raise ValueError("El contenido del archivo debe ser una cadena base64 válida")

class DocumentResponse(BaseModel):
    id: uuid.UUID = Field(..., description="Uuid del documento")
    user_id: uuid.UUID = Field(..., description="Uuid del usuario al que pertenece el documento")
    file_name: str = Field(..., description="Nombre del archivo que sube el usuario")
    file_content: bytes = Field(..., description="Contenido del archivo del usuario en base64")

    model_config = ConfigDict(from_attributes=True)
    
    @field_serializer('file_content')
    def code_base64(self, file_content: bytes) -> str:
        try:
            return base64.b64encode(file_content).decode('utf-8')
        except Exception as e:
            logging.error("No se ha podido codificar en base64 el contenido del archivo", e)
            raise ValueError("No se ha podido codificar en base64 el contenido del archivo")