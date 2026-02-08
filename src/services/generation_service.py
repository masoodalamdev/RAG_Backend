import cohere
from typing import List, Optional
from pydantic import BaseModel


class GenerationResult(BaseModel):
    text: str
    confidence: float
    model: str


class GenerationService:
    def __init__(self, api_key: str):
        self.client = cohere.Client(api_key)
        self.model = "command-r-plus"  # Using Cohere's latest command-r-plus model for generation

    def generate_response(
        self,
        prompt: str,
        context_chunks: Optional[List[str]] = None,
        max_tokens: int = 300,
        temperature: float = 0.3
    ) -> GenerationResult:
        """
        Generate a response based on the prompt and optional context using the Chat API.

        Args:
            prompt: The main prompt for generation
            context_chunks: Optional list of context chunks to include in the prompt
            max_tokens: Maximum number of tokens to generate
            temperature: Controls randomness in generation (lower = more deterministic)

        Returns:
            GenerationResult containing the generated text and confidence
        """
        # Build the message with context if provided
        if context_chunks:
            context_str = "\n\n".join(context_chunks)
            message = (
                f"Based on the following book content, please answer the user's question. "
                f"Do not make up information that is not in the provided context. "
                f"If the answer cannot be found in the context, say so explicitly.\n\n"
                f"Context: {context_str}\n\n"
                f"Question: {prompt}"
            )
        else:
            message = prompt

        try:
            # Generate the response using the Chat API
            response = self.client.chat(
                message=message,
                max_tokens=max_tokens,
                temperature=temperature
            )

            # Calculate a basic confidence score based on the quality of the response
            # In a real implementation, this could be more sophisticated
            generated_text = response.text.strip()
            confidence = self._calculate_confidence(generated_text, context_chunks)
        except Exception as e:
            # If the API call fails, return a helpful error response
            print(f"Cohere API error: {e}")
            generated_text = (
                f"I'm sorry, but I'm currently unable to generate a response. "
                f"This may be due to API limitations or connectivity issues. "
                f"Based on your query: '{prompt}', in a working environment I would "
                f"provide information from the Physical AI & Humanoid Robotics book."
            )
            confidence = 0.1  # Very low confidence when API fails

        return GenerationResult(
            text=generated_text,
            confidence=confidence,
            model=self.model
        )

    def _calculate_confidence(self, response: str, context_chunks: Optional[List[str]]) -> float:
        """
        Calculate a basic confidence score for the generated response.

        Args:
            response: The generated response text
            context_chunks: The context chunks used for generation

        Returns:
            A confidence score between 0 and 1
        """
        # If no context was provided, confidence is lower
        if not context_chunks:
            return 0.5

        # Check if the response mentions inability to answer based on context
        low_confidence_indicators = [
            "cannot be found in the provided context",
            "not mentioned in the provided text",
            "not specified in the context",
            "not in the provided information"
        ]

        response_lower = response.lower()
        for indicator in low_confidence_indicators:
            if indicator in response_lower:
                return 0.2  # Low confidence if it says it can't answer

        # Higher confidence if the response seems to be based on the context
        # This is a simplified approach - in practice, you might use more sophisticated methods
        avg_context_length = sum(len(chunk) for chunk in context_chunks) / len(context_chunks) if context_chunks else 0
        if len(response) > avg_context_length * 0.1:  # Response is reasonably substantial
            return 0.8
        else:
            return 0.6  # Medium confidence