import pytest
from unittest.mock import AsyncMock, MagicMock
from src.services.rag_service import RAGService, QueryResult
from src.services.embedding_service import EmbeddingService
from src.services.retrieval_service import RetrievalService
from src.services.generation_service import GenerationService


@pytest.fixture
def mock_embedding_service():
    """Create a mock embedding service."""
    mock = AsyncMock(spec=EmbeddingService)
    mock.generate_embedding.return_value = MagicMock(
        embedding=[0.1, 0.2, 0.3],
        text="test text",
        model="test-model"
    )
    return mock


@pytest.fixture
def mock_retrieval_service():
    """Create a mock retrieval service."""
    mock = AsyncMock(spec=RetrievalService)
    mock.retrieve_relevant_chunks.return_value = []
    return mock


@pytest.fixture
def mock_generation_service():
    """Create a mock generation service."""
    mock = AsyncMock(spec=GenerationService)
    mock.generate_response.return_value = MagicMock(
        text="test response",
        confidence=0.9,
        model="test-model"
    )
    return mock


@pytest.fixture
def rag_service(mock_embedding_service, mock_retrieval_service, mock_generation_service):
    """Create a RAGService with mocked dependencies."""
    service = RAGService(
        cohere_api_key="test-key",
        qdrant_url="test-url",
        qdrant_api_key="test-key",
        neon_db_url="test-db-url"
    )
    service.embedding_service = mock_embedding_service
    service.retrieval_service = mock_retrieval_service
    service.generation_service = mock_generation_service
    return service


@pytest.mark.asyncio
async def test_process_query_full_mode(rag_service, mock_retrieval_service, mock_generation_service):
    """Test processing a query in full mode."""
    # Mock the retrieval service to return some chunks
    from src.services.retrieval_service import RetrievedChunk
    mock_retrieval_service.retrieve_relevant_chunks.return_value = [
        RetrievedChunk(
            id="chunk-1",
            content="This is a test chunk",
            score=0.9,
            book_id="book-1",
            chunk_index=0,
            page_number=1,
            section_title="Test Section"
        )
    ]
    
    # Call the method
    result = await rag_service.process_query(
        query="test query",
        book_id="book-1",
        mode="full"
    )
    
    # Verify the result
    assert isinstance(result, QueryResult)
    assert result.response_text == "test response"
    assert result.confidence_score == 0.9
    assert len(result.sources) == 0  # Sources are not returned in this mock
    
    # Verify the services were called correctly
    mock_retrieval_service.retrieve_relevant_chunks.assert_called_once()
    mock_generation_service.generate_response.assert_called_once()


@pytest.mark.asyncio
async def test_process_query_selected_mode(rag_service, mock_generation_service):
    """Test processing a query in selected text mode."""
    # Call the method
    result = await rag_service.process_query(
        query="test query",
        book_id="book-1",
        selected_text="selected text",
        mode="selected"
    )
    
    # Verify the result
    assert isinstance(result, QueryResult)
    assert result.response_text == "test response"
    assert result.confidence_score == 0.9
    assert len(result.sources) == 0
    
    # Verify the generation service was called (retrieval should be skipped in selected mode)
    mock_generation_service.generate_response.assert_called_once()


@pytest.mark.asyncio
async def test_ingest_book(rag_service, mock_embedding_service):
    """Test ingesting a book."""
    # Call the method
    book_id = await rag_service.ingest_book(
        title="Test Book",
        author="Test Author",
        content="This is a test book content."
    )
    
    # Verify the result
    assert isinstance(book_id, str)
    assert len(book_id) > 0
    
    # Verify the embedding service was called for each chunk
    # With our simple chunking, the content should be split into chunks
    assert mock_embedding_service.generate_embedding.call_count >= 1


def test_latency_threshold_initialization(rag_service):
    """Test that the latency threshold is properly initialized."""
    assert rag_service.latency_threshold == 2.0