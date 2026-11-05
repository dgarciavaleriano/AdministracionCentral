"""Tabla `documents`: ficheros que sube cada usuario (nóminas, certificados...)."""

import uuid

from sqlalchemy import Column, DateTime, ForeignKey, LargeBinary, String, Uuid, func

from storage.connectors.db import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    # Si se borra el usuario, se borran también sus documentos.
    user_id = Column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    file_name = Column(String, nullable=False)
    file_content = Column(LargeBinary, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Document {self.file_name} del usuario {self.user_id}>"
