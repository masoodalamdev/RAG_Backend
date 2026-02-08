# Data Model: Integrated RAG Chatbot for Published Book

## Entities

### BookContent
Represents the published book's textual content that serves as the knowledge base for the RAG system.

**Fields:**
- `id` (UUID): Unique identifier for the book content
- `title` (String): Title of the book
- `author` (String): Author of the book
- `isbn` (String, nullable): ISBN of the book
- `content` (Text): The full text content of the book
- `created_at` (DateTime): Timestamp when the book content was ingested
- `updated_at` (DateTime): Timestamp when the book content was last updated

**Relationships:**
- One-to-many with `Chunk` (one book content has many chunks)

### Chunk
Represents a segment of book content that has been processed for vector storage.

**Fields:**
- `id` (UUID): Unique identifier for the chunk
- `book_content_id` (UUID): Reference to the parent BookContent
- `content` (Text): The text content of the chunk
- `chunk_index` (Integer): The sequential position of this chunk in the book
- `page_number` (Integer, nullable): Page number where this chunk originated
- `section_title` (String, nullable): Section title where this chunk originated
- `embedding_id` (String): Reference ID for the vector embedding in Qdrant
- `created_at` (DateTime): Timestamp when the chunk was created

**Relationships:**
- Many-to-one with `BookContent` (many chunks belong to one book content)

### UserQuery
Represents questions or requests submitted by readers to the chatbot.

**Fields:**
- `id` (UUID): Unique identifier for the query
- `book_id` (UUID): Reference to the book being queried
- `query_text` (Text): The text of the user's query
- `query_mode` (Enum: 'full', 'selected'): Whether the query is for full book or selected text
- `selected_text` (Text, nullable): Specific text selected by the user (if applicable)
- `session_id` (String, nullable): Session identifier for grouping related queries
- `created_at` (DateTime): Timestamp when the query was submitted

**Relationships:**
- Many-to-one with `BookContent` (queries relate to a specific book)

### SelectedTextPassage
Represents specific portions of book content that users have highlighted or selected for focused queries.

**Fields:**
- `id` (UUID): Unique identifier for the selected text passage
- `book_content_id` (UUID): Reference to the parent BookContent
- `passage_text` (Text): The text that was selected
- `start_position` (Integer): Character position where selection started
- `end_position` (Integer): Character position where selection ended
- `created_at` (DateTime): Timestamp when the selection was made

**Relationships:**
- Many-to-one with `BookContent` (passages relate to a specific book)

### VectorEmbedding
Represents the mathematical representations of book content used for semantic search and retrieval.

**Fields:**
- `id` (String): Identifier for the embedding in the vector database
- `chunk_id` (UUID): Reference to the associated Chunk
- `model_used` (String): The embedding model used (e.g., "embed-v3")
- `embedding_vector` (Array, stored externally in Qdrant): The actual embedding vector
- `created_at` (DateTime): Timestamp when the embedding was generated

**Relationships:**
- One-to-one with `Chunk` (each chunk has one embedding)

### ChatbotResponse
Represents the generated answers provided to users based on book content.

**Fields:**
- `id` (UUID): Unique identifier for the response
- `user_query_id` (UUID): Reference to the associated UserQuery
- `response_text` (Text): The text of the chatbot's response
- `sources` (JSON): List of source references used in the response
- `confidence_score` (Float): Confidence score of the response (0.0-1.0)
- `generated_at` (DateTime): Timestamp when the response was generated

**Relationships:**
- Many-to-one with `UserQuery` (responses are for specific queries)

## Validation Rules

### BookContent
- Title and author are required
- Content must be non-empty
- ISBN, if provided, must follow valid ISBN format

### Chunk
- Content must be non-empty
- Chunk index must be non-negative
- Book content reference must exist

### UserQuery
- Query text must be non-empty
- Book ID must reference an existing book
- Query mode must be either 'full' or 'selected'

### SelectedTextPassage
- Passage text must be non-empty
- Start position must be less than end position
- Book content reference must exist

### VectorEmbedding
- Chunk reference must exist
- Model used must be a valid Cohere embedding model

### ChatbotResponse
- Response text must be non-empty
- User query reference must exist
- Confidence score must be between 0.0 and 1.0

## State Transitions

### BookContent
- `DRAFT` → `INGESTED` (when content is processed and chunks created)
- `INGESTED` → `UPDATED` (when content is modified and re-processed)

### Chunk
- `CREATED` → `EMBEDDED` (when vector embedding is generated)
- `EMBEDDED` → `INDEXED` (when embedding is stored in vector database)

## Indexes

### BookContent
- Index on `title` and `author` for efficient searching
- Index on `isbn` if provided

### Chunk
- Index on `book_content_id` for efficient retrieval
- Index on `chunk_index` for ordered access

### UserQuery
- Index on `book_id` and `created_at` for efficient query history retrieval
- Index on `session_id` if sessions are implemented

### SelectedTextPassage
- Index on `book_content_id` for efficient retrieval

### VectorEmbedding
- Index on `chunk_id` for efficient lookup
- Vector index in Qdrant for similarity search

### ChatbotResponse
- Index on `user_query_id` for efficient linking to queries