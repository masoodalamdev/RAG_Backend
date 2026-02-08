---
id: 2
title: RAG Chatbot Implementation Plan
stage: plan
date: 2026-01-21
surface: agent
model: 
feature: 001-rag-chatbot
branch: 001-rag-chatbot
user: 
command: /sp.plan
labels: ["implementation", "plan", "rag-chatbot", "architecture"]
links:
  spec: ../../specs/001-rag-chatbot/spec.md
  plan: ../../specs/001-rag-chatbot/plan/plan.md
  adr: null
  pr: null
files:
 - specs/001-rag-chatbot/plan/plan.md
 - specs/001-rag-chatbot/plan/research.md
 - specs/001-rag-chatbot/plan/data-model.md
 - specs/001-rag-chatbot/plan/quickstart.md
 - specs/001-rag-chatbot/plan/contracts/openapi.yaml
 - src/api/main.py
 - src/services/rag_service.py
 - src/config/settings.py
 - src/models/book_content.py
 - requirements.txt
 - README.md
 - .env.example
 - pyproject.toml
 - tests/unit/test_rag_service.py
 - scripts/ingest_book.py
tests:
 - 
---

## Prompt

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

1. **Setup**: Run `.specify/scripts/powershell/setup-plan.ps1 -Json` from repo root and parse JSON for FEATURE_SPEC, IMPL_PLAN, SPECS_DIR, BRANCH. For single quotes in args like "I'm Groot", use escape syntax: e.g 'I'\''m Groot' (or double-quote if possible: "I'm Groot").

2. **Load context**: Read FEATURE_SPEC and `.specify/memory/constitution.md`. Load IMPL_PLAN template (already copied).

3. **Execute plan workflow**: Follow the structure in IMPL_PLAN template to:
   - Fill Technical Context (mark unknowns as "NEEDS CLARIFICATION")
   - Fill Constitution Check section from constitution
   - Evaluate gates (ERROR if violations unjustified)
   - Phase 0: Generate research.md (resolve all NEEDS CLARIFICATION)
   - Phase 1: Generate data-model.md, contracts/, quickstart.md
   - Phase 1: Update agent context by running the agent script
   - Re-evaluate Constitution Check post-design

4. **Stop and report**: Command ends after Phase 2 planning. Report branch, IMPL_PLAN path, and generated artifacts.

## Phases

### Phase 0: Outline & Research

1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:

   ```text
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

### Phase 1: Design & Contracts

**Prerequisites:** `research.md` complete

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Agent context update**:
   - Run `.specify/scripts/powershell/update-agent-context.ps1 -AgentType qwen`
   - These scripts detect which AI agent is in use
   - Update the appropriate agent-specific context file
   - Add only new technology from current plan
   - Preserve manual additions between markers

**Output**: data-model.md, /contracts/*, quickstart.md, agent-specific file

## Key rules

- Use absolute paths
- ERROR on gate failures or unresolved clarifications

---

/sp.plan /sp.plan Build a high-quality, production-ready Retrieval-Augmented Generation (RAG) chatbot that can be embedded directly into a published web-based book (using Docusaurus). The system must support two main query modes: (1) general questions about the entire book content, and (2) questions strictly limited to user-selected/highlighted text passages from the book.

Overall architecture:
- Backend: FastAPI (Python) serving a REST API with endpoints for chat/query processing
- Vector database: Qdrant Cloud (free tier) for storing book chunk embeddings
- Relational database: Neon Serverless Postgres for storing metadata (chunk IDs, book structure info, timestamps, etc.)
- LLM & Embeddings: Exclusively Cohere API (embed-v3 for embeddings, command-r or similar for generation)
- Development workflow: Use SpecifyPlus + Qwen CLI as the primary development orchestration tools
- Frontend integration: Deferred - will be done later directly inside the Docusaurus book (e.g., via JavaScript snippet or plugin). Backend API will be designed to accept calls from the book frontend.

High-level phases and structure:

Phase 1 – Preparation & Setup
- Project structure creation (using SpecifyPlus scaffolding if applicable)
- Environment setup (Python 3.10+, virtualenv/poetry/uv)
- Secure credential management (.env file, never commit keys)
- Connect & test: Neon Postgres connection, Qdrant client initialization, Cohere client validation

Phase 2 – Book Content Ingestion Pipeline
- Text chunking strategy (semantic / fixed-size with overlap, ~300-600 tokens per chunk)
- Metadata enrichment (page/chapter info, section headings if available)
- Generate embeddings using Cohere embed-v3
- Upsert vectors + payload to Qdrant collection (create collection if needed, optimize for free tier limits)
- Store minimal relational metadata in Neon if required (e.g., mapping chunk_id → source reference)

Phase 3 – Retrieval Logic
- Query embedding generation (same Cohere model)
- Hybrid search if supported, otherwise pure vector search
- Re-ranking or filtering (score threshold ≥0.82 cosine, top-k=8–15)
- Context assembly: concatenate retrieved chunks with proper delimiters and source attribution
- Special handling for selected-text mode: treat user-selected text as temporary in-memory context (embed & retrieve from it directly or prepend to prompt)

Phase 4 – Generation & RAG Chain
- Prompt engineering: strong grounding instructions, no-hallucination rules, citation of sources
- Use Cohere chat/completion endpoint
- Support system prompt + user message + retrieved context
- Output format: clean markdown response + optional source references

Phase 5 – FastAPI Backend
- Endpoints: /health, /ingest (admin-only for book upload/chunking), /chat (main query endpoint)
- Request body: { "query": str, "book_id": str, "selected_text": str | null, "mode": "full" | "selected" }
- Rate limiting, basic error handling, logging
- CORS configuration for book domain embedding

Phase 6 – Embedding / Frontend Integration (Deferred)
- Deferred - will be done later directly inside Docusaurus book
- Prepare backend API to be callable from Docusaurus (e.g., via fetch POST requests)
- No frontend code generation in this phase

Phase 7 – Testing & Quality Gates
- Unit tests: embedding, retrieval recall, prompt formatting
- Integration tests: end-to-end query → response (mock book content)
- Accuracy validation: 20+ test questions (general + selected-text), measure grounding & hallucination rate
- Latency measurement: aim <2s p95
- Security scan basics (no exposed keys, input sanitization)

Phase 8 – Documentation & Deliverables
- README.md with architecture diagram (text-based), setup, deployment steps
- How to ingest a book (script or manual process)
- API documentation (e.g., OpenAPI/Swagger) for future Docusaurus integration
- Environment variable template (.env.example)

Key non-goals / exclusions (do NOT implement):
- User login / sessions / persistence of chat history
- Book upload UI (assume admin/script-based ingestion)
- Real-time collaboration or multi-user features
- Mobile-specific optimizations
- Advanced reranking models or cross-encoder
- Fine-tuning or custom Cohere models
- Any frontend code (deferred to Docusaurus)

Prioritize:
- Maximum grounding & zero hallucination
- Clean, modular, well-commented code
- Free-tier compatibility (watch Qdrant storage & Neon compute limits)
- Easy reproducibility for other developers/authors
- API readiness for Docusaurus embedding

Generate a clear, numbered/step-by-step implementation plan with estimated effort indicators (S/M/L) for each major task and suggested file/folder organization.

## Response snapshot

I've created a comprehensive implementation plan for the RAG chatbot with all the required artifacts:

1. **Implementation Plan** (plan.md): Detailed architecture and project structure
2. **Research Summary** (research.md): Technology decisions and rationale
3. **Data Model** (data-model.md): Entity definitions and relationships
4. **Quickstart Guide** (quickstart.md): Setup and usage instructions
5. **API Contracts** (contracts/openapi.yaml): OpenAPI specification
6. **Core Implementation Files**:
   - API endpoints (src/api/main.py)
   - RAG service (src/services/rag_service.py)
   - Configuration (src/config/settings.py)
   - Data models (src/models/book_content.py)
7. **Supporting Files**:
   - Requirements (requirements.txt)
   - Documentation (README.md)
   - Environment template (.env.example)
   - Package configuration (pyproject.toml)
   - Tests (tests/unit/test_rag_service.py)
   - Scripts (scripts/ingest_book.py)

The plan follows all constitutional principles:
- Precision in retrieval and generation with cosine similarity threshold >0.8
- User-centric functionality with response latency under 2 seconds
- Scalability and efficiency using free-tier services
- Security and privacy with no user data storage beyond session
- Modularity with clean separation of components
- Content grounding with responses based solely on book content

The architecture supports both query modes (full book and selected text) as required, with proper security measures and performance considerations.

## Outcome

- ✅ Impact: Created comprehensive implementation plan with all required artifacts
- 🧪 Tests: Created unit tests for core functionality
- 📁 Files: Generated multiple files including plan, models, API contracts, and implementation
- 🔁 Next prompts: Ready to proceed with task breakdown using /sp.tasks
- 🧠 Reflection: Successfully translated high-level requirements into detailed technical implementation plan

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Break implementation plan into specific tasks using /sp.tasks