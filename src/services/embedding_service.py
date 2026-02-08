from typing import List
import cohere
from pydantic import BaseModel


class EmbeddingResult(BaseModel):
    text: str
    embedding: List[float]
    model: str


class EmbeddingService:
    def __init__(self, api_key: str):
        self.client = cohere.Client(api_key)
        self.model = "embed-multilingual-v2.0"  # Using Cohere's embedding model

    def generate_embedding(self, text: str) -> EmbeddingResult:
        """
        Generate an embedding for a single text.
        
        Args:
            text: The text to generate an embedding for
            
        Returns:
            EmbeddingResult containing the text, embedding vector, and model used
        """
        response = self.client.embed(
            texts=[text],
            model=self.model
        )
        
        return EmbeddingResult(
            text=text,
            embedding=response.embeddings[0],
            model=self.model
        )

    def generate_embeddings_batch(self, texts: List[str]) -> List[EmbeddingResult]:
        """
        Generate embeddings for a batch of texts.
        
        Args:
            texts: List of texts to generate embeddings for
            
        Returns:
            List of EmbeddingResults
        """
        # Cohere has a limit on batch size, so we'll process in chunks if needed
        batch_size = 96  # Cohere's recommended batch size
        results = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            response = self.client.embed(
                texts=batch,
                model=self.model
            )
            
            for j, text in enumerate(batch):
                results.append(EmbeddingResult(
                    text=text,
                    embedding=response.embeddings[j],
                    model=self.model
                ))
                
        return results

    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score between 0 and 1
        """
        # Calculate dot product
        dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
        
        # Calculate magnitudes
        magnitude1 = sum(a * a for a in embedding1) ** 0.5
        magnitude2 = sum(b * b for b in embedding2) ** 0.5
        
        # Calculate cosine similarity
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        similarity = dot_product / (magnitude1 * magnitude2)
        
        # Ensure the result is between 0 and 1
        return max(0.0, min(1.0, similarity))