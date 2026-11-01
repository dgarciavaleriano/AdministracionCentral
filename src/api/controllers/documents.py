import uuid
from storage.crud.document_repository import DocumentRepository
from storage.entities.document import Document
from fastapi import Depends
from storage.connectors.db import get_db
from sqlalchemy.orm import Session

class DocumentsController:
    def __init__(self, db: Session = Depends(get_db)):
        self.document_repository = DocumentRepository(db)

    def create_document(self, user_id: uuid.UUID, file_name: str, file_content: bytes) -> Document | None:
        document = Document(user_id, file_name, file_content)
        return self.document_repository.create(document)

    def get_document(self, id: uuid.UUID) -> Document | None:
        return self.document_repository.get(id)

    def update_document(self, id: uuid.UUID, user_id: uuid.UUID, file_name: str, file_content: bytes) -> Document | None:
        document = Document(user_id, file_name, file_content)
        return self.document_repository.update(id, document)

    def delete_document(self, id: uuid.UUID) -> bool:
        return self.document_repository.delete(id)

    def get_documents_by_user_id(self, user_id: uuid.UUID) -> list[Document]:
        return self.document_repository.get_by_user_id(user_id)