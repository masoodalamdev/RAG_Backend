from sqlalchemy import Column, Integer, String, Text, DateTime, UUID, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql import func
import uuid
from .base import Base


class SelectedTextPassage(Base):
    __tablename__ = "selected_text_passages"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_content_id = Column(PG_UUID(as_uuid=True), nullable=False)
    passage_text = Column(Text, nullable=False)
    start_position = Column(Integer, nullable=False)
    end_position = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())