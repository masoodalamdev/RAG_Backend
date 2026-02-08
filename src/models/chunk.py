from sqlalchemy import Column, Integer, String, Text, DateTime, UUID, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql import func
import uuid
from .base import Base


class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_content_id = Column(PG_UUID(as_uuid=True), nullable=False)
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    page_number = Column(Integer, nullable=True)
    section_title = Column(String, nullable=True)
    embedding_id = Column(String, nullable=False)  # Reference ID for the vector embedding in Qdrant
    created_at = Column(DateTime(timezone=True), server_default=func.now())