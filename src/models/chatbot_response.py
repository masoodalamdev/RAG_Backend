from sqlalchemy import Column, Integer, String, Text, DateTime, UUID, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql import func
import uuid
import json
from .base import Base


class ChatbotResponse(Base):
    __tablename__ = "chatbot_responses"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_query_id = Column(PG_UUID(as_uuid=True), nullable=False)
    response_text = Column(Text, nullable=False)
    sources = Column(String, nullable=False)  # JSON string representing the sources
    confidence_score = Column(Integer, nullable=False)  # Stored as integer (percentage)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())

    def set_sources(self, sources_list):
        """Convert sources list to JSON string for storage."""
        self.sources = json.dumps(sources_list)

    def get_sources(self):
        """Convert stored JSON string back to sources list."""
        return json.loads(self.sources)