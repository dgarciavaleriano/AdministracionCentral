import os
import uuid
from uvicorn import logging
from storage.crud.document_repository import DocumentRepository
from storage.entities.document import Document
from fastapi import Depends
from storage.connectors.db import get_db
from sqlalchemy.orm import Session
from src.services.boe_client import BOEClient

class DocumentsController:
    def __init__(self, db: Session = Depends(get_db)):
        self.document_repository = DocumentRepository(db)

    def create_document(self, user_id: uuid.UUID, file_name: str, file_content: bytes) -> Document | None:
        document = Document(user_id=user_id, file_name=file_name, file_content=file_content)
        return self.document_repository.create(document)

    def get_document(self, id: uuid.UUID) -> Document | None:
        return self.document_repository.get(id)

    def update_document(self, id: uuid.UUID, user_id: uuid.UUID, file_name: str, file_content: bytes) -> Document | None:
        document = Document(user_id=user_id, file_name=file_name, file_content=file_content)
        return self.document_repository.update(id, document)

    def delete_document(self, id: uuid.UUID) -> bool:
        return self.document_repository.delete(id)

    def get_documents_by_user_id(self, user_id: uuid.UUID) -> list[Document]:
        return self.document_repository.get_by_user_id(user_id)

    def get_all_documents(self) -> list[Document]:
        """Devuelve todos los documentos para el panel de admin."""
        return self.document_repository.get_all() 

    def sync_boe_documents(self, fecha: str, db: Session = Depends(get_db)):
        """
        Descarga los PDFs del BOE para una fecha y los registra en la base de datos.
        """
        try:
            client = BOEClient()
            # El cliente guarda los PDFs en la ruta indicada y devuelve las rutas locales
            rutas_descargadas = client.descargar_sumario_completo(fecha, directorio_destino="data/pdfs")

            # GUARDAR EN BASE DE DATOS
            for ruta in rutas_descargadas:
                nombre = ruta.split("/")[-1].split("\\")[-1] # Windows y Linux
                
                # Comprobar si ya existe para no duplicar
                # (Deberías tener un método get_by_filename en tu repositorio)
                # existente = self.document_repository.get_by_filename(nombre)
                # if existente: continue

                nuevo_doc = Document(
                    file_name=nombre,
                    file_path=ruta,
                    fecha_boe=fecha,
                    tipo="BOE",
                    tamaño=os.path.getsize(ruta),
                    estado="Pendiente"
                )
                self.document_repository.create(nuevo_doc)
        
            return len(rutas_descargadas)
        except Exception as e:
            raise e