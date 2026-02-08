from sqlalchemy import Column, Integer, String, Text, DateTime, UUID, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql import func
import uuid
from .base import Base  # Import the shared Base


class UserQuery(Base):
    __tablename__ = "user_queries"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id = Column(PG_UUID(as_uuid=True), nullable=False)
    query_text = Column(Text, nullable=False)
    query_mode = Column(String(10), nullable=False)  # 'full' or 'selected'
    selected_text = Column(Text, nullable=True)
    session_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())