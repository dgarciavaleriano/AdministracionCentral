import uuid
import datetime
from storage.base import Base
from storage.entities.mixins import Timestamped, UUIDPrimaryKey
from sqlalchemy import  ForeignKey, String, text, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column

class Document(UUIDPrimaryKey, Timestamped, Base):
    __tablename__ = "documents"

    def __init__(self, user_id: uuid.UUID, file_name: str, file_content: bytes):
        self.user_id = user_id
        self.file_name = file_name
        self.file_content = file_content

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )

    file_name: Mapped[str] = mapped_column(String(255))

    file_content: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)

    uploaded_at: Mapped[datetime.datetime] = mapped_column(
        server_default=text("now()"), sort_order=102
    )

    def __repr__(self) -> str:
        return f"<Document {self.file_name} uploaded by User {self.user_id}>"