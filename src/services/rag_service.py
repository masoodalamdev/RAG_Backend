from typing import Optional, List
from pydantic import BaseModel
import uuid
import time
import logging
from src.models.book_content import BookContent
from src.models.chunk import Chunk
from src.models.user_query import UserQuery
from src.models.chatbot_response import ChatbotResponse
from src.services.embedding_service import EmbeddingService
from src.services.retrieval_service import RetrievalService, RetrievedChunk
from src.services.generation_service import GenerationService
from src.utils.metrics import metrics_collector


class SourceReference(BaseModel):
    chunk_id: str
    page_number: Optional[int]
    section_title: Optional[str]


class QueryResult(BaseModel):
    response_text: str
    sources: List[SourceReference]
    confidence_score: float


class RAGService:
    def __init__(
        self,
        cohere_api_key: str,
        qdrant_url: str,
        qdrant_api_key: str,
        neon_db_url: str
    ):
        self.embedding_service = EmbeddingService(cohere_api_key)
        self.retrieval_service = RetrievalService(qdrant_url, qdrant_api_key)
        self.generation_service = GenerationService(cohere_api_key)
        self.neon_db_url = neon_db_url
        self.collection_name = "book_chunks"

        # Performance monitoring
        self.logger = logging.getLogger(__name__)
        self.latency_threshold = 2.0  # 2 seconds threshold

    async def process_query(
        self,
        query: str,
        book_id: str,
        selected_text: Optional[str] = None,
        mode: str = "full"
    ) -> QueryResult:
        """
        Process a user query and return a response based on book content.

        Args:
            query: The user's query
            book_id: The ID of the book to query
            selected_text: Optional selected text for focused queries
            mode: Query mode ("full" for entire book, "selected" for selected text)

        Returns:
            QueryResult containing the response, sources, and confidence score
        """
        start_time = time.time()

        try:
            # Generate embedding for the query
            embedding_start = time.time()
            query_embedding_result = self.embedding_service.generate_embedding(query)
            query_embedding = query_embedding_result.embedding
            embedding_time = time.time() - embedding_start

            # Retrieve relevant chunks based on the query
            retrieval_start = time.time()
            if mode == "selected" and selected_text:
                # For selected text mode, we'll use the selected text directly
                context = f"Based on the selected text: {selected_text}. "
                context += f"The user asks: {query}"

                # Set retrieval_time to 0 since we're not retrieving from vector DB in selected mode
                retrieval_time = 0.0

                # Generate response using the selected text as context
                generation_start = time.time()
                generation_result = self.generation_service.generate_response(
                    prompt=context,
                    max_tokens=300,
                    temperature=0.3
                )
                generation_time = time.time() - generation_start

                # For selected text mode, we don't have traditional sources
                sources = []
                confidence_score = generation_result.confidence
            else:
                # For full book mode, retrieve relevant chunks from vector DB
                retrieved_chunks = self.retrieval_service.retrieve_relevant_chunks(
                    query_embedding=query_embedding,
                    book_id=book_id,
                    top_k=10,
                    score_threshold=0.82
                )
                retrieval_time = time.time() - retrieval_start

                # Build context from retrieved chunks
                context_parts = []
                sources = []

                for chunk in retrieved_chunks:
                    if chunk.score >= 0.82:  # Only include results above threshold
                        context_parts.append(chunk.content)

                        # Add source reference
                        sources.append(SourceReference(
                            chunk_id=chunk.id,
                            page_number=chunk.page_number,
                            section_title=chunk.section_title
                        ))

                # Combine context and query for generation
                if context_parts:
                    context = (
                        "Based on the following book content, please answer the user's question. "
                        "Do not make up information that is not in the provided context. "
                        "If the answer cannot be found in the context, say so explicitly.\n\n"
                        f"Context: {' '.join(context_parts[:5])}\n\n"  # Limit to first 5 chunks
                        f"Question: {query}"
                    )
                else:
                    # If no context was retrieved, ask the model to respond based on general knowledge
                    # but indicate that it's not from the book
                    context = (
                        f"Please answer the following question: {query}. "
                        f"Note: I couldn't find specific information about this in the book content, "
                        f"so I'm providing a general response."
                    )

                # Generate response using Cohere
                generation_start = time.time()
                generation_result = self.generation_service.generate_response(
                    prompt=context,
                    max_tokens=300,
                    temperature=0.3
                )
                generation_time = time.time() - generation_start

                # Calculate a confidence score based on the number of sources and their scores
                if retrieved_chunks:
                    avg_score = sum(c.score for c in retrieved_chunks) / len(retrieved_chunks)
                    confidence_score = min(1.0, avg_score * 1.2)  # Boost slightly for having good matches
                else:
                    confidence_score = 0.2  # Low confidence if no relevant chunks found

            total_time = time.time() - start_time

            # Record metrics
            metrics_collector.record_response_time("/chat", total_time)
            metrics_collector.record_request("/chat")

            # Log performance metrics
            self.logger.info(
                f"Query processed: total_time={total_time:.2f}s, "
                f"embedding_time={embedding_time:.2f}s, "
                f"retrieval_time={retrieval_time:.2f}s, "
                f"generation_time={generation_time:.2f}s, "
                f"book_id={book_id}, "
                f"mode={mode}"
            )

            # Check if response time exceeds the threshold
            if total_time > self.latency_threshold:
                self.logger.warning(f"Query response time exceeded {self.latency_threshold} seconds: {total_time:.2f}s")
                metrics_collector.record_error("/chat")

            return QueryResult(
                response_text=generation_result.text.strip(),
                sources=sources,
                confidence_score=confidence_score
            )
        except Exception as e:
            # If anything goes wrong, return a helpful error response
            self.logger.error(f"Error processing query: {str(e)}")

            # Return a fallback response
            return QueryResult(
                response_text=(
                    f"I'm sorry, but I'm currently experiencing technical difficulties. "
                    f"Based on your query '{query}', in a working environment I would "
                    f"provide information from the Physical AI & Humanoid Robotics book. "
                    f"Please try again later or contact support if the issue persists."
                ),
                sources=[],
                confidence_score=0.1
            )

    async def ingest_book(
        self,
        title: str,
        author: str,
        content: Optional[str] = None,
        file_path: Optional[str] = None,
        isbn: Optional[str] = None
    ) -> str:
        """
        Ingest a book into the RAG system.

        Args:
            title: The title of the book
            author: The author of the book
            content: The content of the book (as text)
            file_path: Path to a file containing the book content
            isbn: The ISBN of the book (optional)

        Returns:
            The ID of the ingested book
        """
        start_time = time.time()

        # If content is not provided but file_path is, read the file
        if not content and file_path:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

        if not content:
            raise ValueError("Either content or file_path must be provided")

        # Create a unique ID for the book
        book_id = str(uuid.uuid4())

        # Chunk the content (simplified - in reality, you'd want more sophisticated chunking)
        chunk_size = 500  # tokens, approximately
        chunks = self._chunk_text(content, chunk_size)

        # Process each chunk
        for i, chunk_text in enumerate(chunks):
            # Create embedding for the chunk
            embedding_result = self.embedding_service.generate_embedding(chunk_text)
            embedding = embedding_result.embedding

            # Generate a unique ID for the chunk
            chunk_id = str(uuid.uuid4())

            # Add the chunk to the retrieval service (which handles Qdrant)
            self.retrieval_service.add_chunk(
                chunk_id=chunk_id,
                embedding=embedding,
                content=chunk_text,
                book_id=book_id,
                chunk_index=i,
                page_number=None,  # Would come from more sophisticated chunking
                section_title=None  # Would come from more sophisticated chunking
            )

        total_time = time.time() - start_time

        # Record metrics
        metrics_collector.record_response_time("/ingest", total_time)
        metrics_collector.record_request("/ingest")

        # Log performance metrics
        self.logger.info(
            f"Book ingested: total_time={total_time:.2f}s, "
            f"book_id={book_id}, "
            f"title={title}, "
            f"author={author}, "
            f"chunks_count={len(chunks)}"
        )

        return book_id

    def _chunk_text(self, text: str, chunk_size: int) -> List[str]:
        """
        Simple function to chunk text into smaller pieces.
        In a real implementation, you'd want more sophisticated chunking
        that respects sentence boundaries and semantic coherence.
        """
        # This is a very basic chunking implementation
        # In practice, you'd want to use more sophisticated methods
        # that preserve context and respect sentence boundaries
        words = text.split()
        chunks = []

        for i in range(0, len(words), chunk_size):
            chunk_words = words[i:i + chunk_size]
            chunks.append(' '.join(chunk_words))

        return chunks