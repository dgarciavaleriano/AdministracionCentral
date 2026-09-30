import uuid
from storage.crud.repository import Repository
from sqlalchemy.orm import Session
from sqlalchemy import select
from storage.entities.document import Document
from config.logger import Logging

logging = Logging(__name__)

class DocumentRepository(Repository[Document]):
    def __init__(self, session: Session):
        self.session = session

    def create(self, entity: Document) -> Document | None:
        try:
            self.session.add(entity)
            self.session.flush()
            self.session.refresh(entity)
            logging.info(f"Creado el documento con el id: {entity.id}")
            return entity
        except Exception as e:
            self.session.rollback()
            logging.error("Error al crear el documento", e)
            return None

    def get(self, id: uuid.UUID) -> Document | None:
        return self.session.get(Document, id)

    def update(self, id: uuid.UUID, entity: Document) -> Document | None:
        try:
            document = self.session.get(Document, id)
            if document:
                document.user_id = entity.user_id
                document.file_name = entity.file_name
                document.file_content = entity.file_content
                self.session.flush()
                self.session.refresh(document)
                logging.info(f"Actualizado el documento con el id: {document.id}")
                return document
            return None
        except Exception as e:
            self.session.rollback()
            logging.error("Error al actualizar el documento", e)
            return None

    def delete(self, id: uuid.UUID) -> bool:
        document = self.session.get(Document, id)
        if document:
            self.session.delete(document)
            self.session.flush()
            logging.info(f"Eliminado el documento con el id: {document.id}")
            return True
        return False

    def get_by_user_id(self, user_id: uuid.UUID) -> list[Document]:
        query = select(Document).where(Document.user_id == user_id)
        return list(self.session.scalars(query).all())