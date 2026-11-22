import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from api.controllers.documents import DocumentsController
from api.schema.document import DocumentResponse, DocumentRequest, DocumentSummary

from sqlalchemy.orm import Session
# Asume que tienes una dependencia get_db configurada
from src.storage.connectors.db import get_db 
from src.api.controllers import documents as doc_controller
from src.api.schema.document import SyncBOEResponse

router: APIRouter = APIRouter()

@router.post("/", response_model= DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(document: DocumentRequest,
                          controller: DocumentsController = Depends()):
    result = controller.create_document(document.user_id, document.file_name, document.file_content)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo crear el documento"
        )
    return result

@router.get("/{id}", response_model=DocumentResponse, status_code=status.HTTP_200_OK)
async def get_document(id: uuid.UUID,
                       controller: DocumentsController = Depends()):
    result = controller.get_document(id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Documento no encontrado"
        )
    return result

@router.put("/{id}", response_model=DocumentResponse, status_code=status.HTTP_200_OK)
async def update_document(id: uuid.UUID,
                       document: DocumentRequest,
                       controller: DocumentsController = Depends()):
    result = controller.update_document(id, document.user_id, document.file_name, document.file_content)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo actualizar el documento"
        )
    return result

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(id: uuid.UUID,
                       controller: DocumentsController = Depends()):
    result = controller.delete_document(id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Documento no encontrado"
        )

@router.get("/user/{id}", response_model=list[DocumentSummary], status_code=status.HTTP_200_OK)
async def get_documents_by_user(id: uuid.UUID,
                       controller: DocumentsController = Depends()):
    document = controller.get_documents_by_user_id(id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="No hay documentos asociados a este usuario"
        )
    return document

@router.get("/", response_model=list[DocumentSummary], status_code=status.HTTP_200_OK)
async def get_all_documents(controller: DocumentsController = Depends()):
    """Devuelve todos los documentos registrados en el sistema."""
    return controller.get_all_documents()

@router.post("/sync-boe/{fecha}", response_model=SyncBOEResponse)
def sync_boe_endpoint(fecha: str, db: Session = Depends(get_db), controller: DocumentsController = Depends()):
    """
    Descarga los documentos del BOE para una fecha específica (YYYY-MM-DD).
    """
    try:
        # Usamos la instancia del controlador inyectada
        count = controller.sync_boe_documents(fecha, db)
        return SyncBOEResponse(
            message="Sincronización completada con éxito",
            downloaded_count=count,
            fecha=fecha
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno al sincronizar: {str(e)}")