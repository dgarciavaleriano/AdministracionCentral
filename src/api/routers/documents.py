import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from api.controllers.documents import DocumentsController
from api.schema.document import DocumentResponse, DocumentRequest

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

@router.get("/user/{id}", response_model=list[DocumentResponse], status_code=status.HTTP_200_OK)
async def get_documents_by_user(id: uuid.UUID,
                       controller: DocumentsController = Depends()):
    document = controller.get_documents_by_user_id(id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="No hay documentos asociados a este usuario"
        )
    return document