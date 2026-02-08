from typing import List, Optional
import qdrant_client
from qdrant_client.http import models
from pydantic import BaseModel
import uuid


class RetrievedChunk(BaseModel):
    id: str
    content: str
    score: float
    book_id: str
    chunk_index: int
    page_number: Optional[int] = None
    section_title: Optional[str] = None


class RetrievalService:
    def __init__(self, qdrant_url: str, api_key: str, collection_name: str = "book_chunks"):
        self.client = qdrant_client.QdrantClient(
            url=qdrant_url,
            api_key=api_key,
            prefer_grpc=False
        )
        self.collection_name = collection_name

        # Ensure the collection exists
        self._ensure_collection_exists()

    def _ensure_collection_exists(self):
        """Ensure the collection exists, create it if it doesn't."""
        try:
            # Try to get collection info to see if it exists
            collection_info = self.client.get_collection(self.collection_name)
            print(f"Collection {self.collection_name} already exists")
        except Exception as e:
            print(f"Collection {self.collection_name} does not exist: {e}")
            # Collection doesn't exist, create it
            # Note: Cohere's embed-multilingual-v2.0 produces 768-dimensional vectors
            vector_size = 768
            try:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE),
                )
                print(f"Created collection: {self.collection_name} with {vector_size}-dimensional vectors")
            except Exception as create_error:
                print(f"Failed to create collection {self.collection_name}: {create_error}")
                # Try with a different approach - maybe the cloud version requires different parameters
                try:
                    # For Qdrant Cloud, sometimes we need to specify the config differently
                    from qdrant_client.http import models as rest_models
                    self.client.create_collection(
                        collection_name=self.collection_name,
                        vectors_config=rest_models.VectorParams(size=vector_size, distance=rest_models.Distance.COSINE)
                    )
                    print(f"Created collection: {self.collection_name} using REST models")
                except Exception as fallback_error:
                    print(f"Fallback creation also failed: {fallback_error}")
                    raise create_error

    def retrieve_relevant_chunks(
        self,
        query_embedding: List[float],
        book_id: str,
        top_k: int = 10,
        score_threshold: float = 0.82
    ) -> List[RetrievedChunk]:
        """
        Retrieve relevant chunks from the vector database based on the query embedding.

        Args:
            query_embedding: The embedding vector for the query
            book_id: The ID of the book to search within
            top_k: Maximum number of results to return
            score_threshold: Minimum similarity score for results

        Returns:
            List of RetrievedChunks with content and metadata
        """
        # Ensure collection exists before attempting search
        self._ensure_collection_exists()

        try:
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="book_id",
                            match=models.MatchValue(value=book_id)
                        )
                    ]
                ),
                limit=top_k,
                score_threshold=score_threshold
            )

            retrieved_chunks = []
            for result in search_results:
                if result.score >= score_threshold:
                    retrieved_chunks.append(RetrievedChunk(
                        id=result.id,
                        content=result.payload.get("content", ""),
                        score=result.score,
                        book_id=result.payload.get("book_id", ""),
                        chunk_index=result.payload.get("chunk_index", 0),
                        page_number=result.payload.get("page_number"),
                        section_title=result.payload.get("section_title")
                    ))

            return retrieved_chunks
        except Exception as e:
            # If collection doesn't exist or other error, return empty list
            print(f"Retrieval service error: {e}")
            return []

    def retrieve_by_ids(self, chunk_ids: List[str]) -> List[RetrievedChunk]:
        """
        Retrieve specific chunks by their IDs.
        
        Args:
            chunk_ids: List of chunk IDs to retrieve
            
        Returns:
            List of RetrievedChunks
        """
        results = self.client.retrieve(
            collection_name=self.collection_name,
            ids=chunk_ids,
            with_payload=True,
            with_vectors=False
        )
        
        retrieved_chunks = []
        for result in results:
            retrieved_chunks.append(RetrievedChunk(
                id=result.id,
                content=result.payload.get("content", ""),
                score=1.0,  # Score is not applicable when retrieving by ID
                book_id=result.payload.get("book_id", ""),
                chunk_index=result.payload.get("chunk_index", 0),
                page_number=result.payload.get("page_number"),
                section_title=result.payload.get("section_title")
            ))
        
        return retrieved_chunks

    def add_chunk(
        self, 
        chunk_id: str, 
        embedding: List[float], 
        content: str, 
        book_id: str, 
        chunk_index: int,
        page_number: Optional[int] = None,
        section_title: Optional[str] = None
    ):
        """
        Add a chunk to the vector database.
        
        Args:
            chunk_id: Unique ID for the chunk
            embedding: The embedding vector for the chunk
            content: The text content of the chunk
            book_id: The ID of the book this chunk belongs to
            chunk_index: The sequential position of this chunk in the book
            page_number: The page number where this chunk originated (optional)
            section_title: The section title where this chunk originated (optional)
        """
        point = models.PointStruct(
            id=chunk_id,
            vector=embedding,
            payload={
                "content": content,
                "book_id": book_id,
                "chunk_index": chunk_index,
                "page_number": page_number,
                "section_title": section_title
            }
        )
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=[point]
        )

    def delete_chunks_for_book(self, book_id: str):
        """
        Delete all chunks associated with a specific book.
        
        Args:
            book_id: The ID of the book to delete chunks for
        """
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="book_id",
                            match=models.MatchValue(value=book_id)
                        )
                    ]
                )
            )
        )