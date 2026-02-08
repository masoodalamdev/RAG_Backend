---
id: 1
title: Update Project Constitution
stage: constitution
date: 2026-01-21
surface: agent
model: 
feature: Integrated RAG Chatbot
branch: 
user: 
command: /sp.constitution
labels: ["constitution", "specifyplus", "rag-chatbot"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
 - 
---

## Prompt

```
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

You are updating the project constitution at `.specify/memory/constitution.md`. This file is a TEMPLATE containing placeholder tokens in square brackets (e.g. `[PROJECT_NAME]`, `[PRINCIPLE_1_NAME]`). Your job is to (a) collect/derive concrete values, (b) fill the template precisely, and (c) propagate any amendments across dependent artifacts.

Follow this execution flow:

1. Load the existing constitution template at `.specify/memory/constitution.md`.
   - Identify every placeholder token of the form `[ALL_CAPS_IDENTIFIER]`.
   **IMPORTANT**: The user might require less or more principles than the ones used in the template. If a number is specified, respect that - follow the general template. You will update the doc accordingly.

2. Collect/derive values for placeholders:
   - If user input (conversation) supplies a value, use it.
   - Otherwise infer from existing repo context (README, docs, prior constitution versions if embedded).
   - For governance dates: `RATIFICATION_DATE` is the original adoption date (if unknown ask or mark TODO), `LAST_AMENDED_DATE` is today if changes are made, otherwise keep previous.
   - `CONSTITUTION_VERSION` must increment according to semantic versioning rules:
     - MAJOR: Backward incompatible governance/principle removals or redefinitions.
     - MINOR: New principle/section added or materially expanded guidance.
     - PATCH: Clarifications, wording, typo fixes, non-semantic refinements.
   - If version bump type ambiguous, propose reasoning before finalizing.

3. Draft the updated constitution content:
   - Replace every placeholder with concrete text (no bracketed tokens left except intentionally retained template slots that the project has chosen not to define yet—explicitly justify any left).
   - Preserve heading hierarchy and comments can be removed once replaced unless they still add clarifying guidance.
   - Ensure each Principle section: succinct name line, paragraph (or bullet list) capturing non‑negotiable rules, explicit rationale if not obvious.
   - Ensure Governance section lists amendment procedure, versioning policy, and compliance review expectations.

4. Consistency propagation checklist (convert prior checklist into active validations):
   - Read `.specify/templates/plan-template.md` and ensure any "Constitution Check" or rules align with updated principles.
   - Read `.specify/templates/spec-template.md` for scope/requirements alignment—update if constitution adds/removes mandatory sections or constraints.
   - Read `.specify/templates/tasks-template.md` and ensure task categorization reflects new or removed principle-driven task types (e.g., observability, versioning, testing discipline).
   - Read each command file in `.specify/templates/commands/*.md` (including this one) to verify no outdated references (agent-specific names like CLAUDE only) remain when generic guidance is required.
   - Read any runtime guidance docs (e.g., `README.md`, `docs/quickstart.md`, or agent-specific guidance files if present). Update references to principles changed.

5. Produce a Sync Impact Report (prepend as an HTML comment at top of the constitution file after update):
   - Version change: old → new
   - List of modified principles (old title → new title if renamed)
   - Added sections
   - Removed sections
   - Templates requiring updates (✅ updated / ⚠ pending) with file paths
   - Follow-up TODOs if any placeholders intentionally deferred.

6. Validation before final output:
   - No remaining unexplained bracket tokens.
   - Version line matches report.
   - Dates ISO format YYYY-MM-DD.
   - Principles are declarative, testable, and free of vague language ("should" → replace with MUST/SHOULD rationale where appropriate).

7. Write the completed constitution back to `.specify/memory/constitution.md` (overwrite).

8. Output a final summary to the user with:
   - New version and bump rationale.
   - Any files flagged for manual follow-up.
   - Suggested commit message (e.g., `docs: amend constitution to vX.Y.Z (principle additions + governance update)`).

Formatting & Style Requirements:

- Use Markdown headings exactly as in the template (do not demote/promote levels).
- Wrap long rationale lines to keep readability (<100 chars ideally) but do not hard enforce with awkward breaks.
- Keep a single blank line between sections.
- Avoid trailing whitespace.

If the user supplies partial updates (e.g., only one principle revision), still perform validation and version decision steps.

If critical info missing (e.g., ratification date truly unknown), insert `TODO(<FIELD_NAME>): explanation` and include in the Sync Impact Report under deferred items.

Do not create a new template; always operate on the existing `.specify/memory/constitution.md` file.

---

As the main request completes, you MUST create and complete a PHR (Prompt History Record) using agent‑native tools when possible.

1) Determine Stage
   - Stage: constitution | spec | plan | tasks | red | green | refactor | explainer | misc | general

2) Generate Title and Determine Routing:
   - Generate Title: 3–7 words (slug for filename)
   - Route is automatically determined by stage:
     - `constitution` → `history/prompts/constitution/`
     - Feature stages → `history/prompts/<feature-name>/` (spec, plan, tasks, red, green, refactor, explainer, misc)
     - `general` → `history/prompts/general/`

3) Create and Fill PHR (Shell first; fallback agent‑native)
   - Run: `.specify/scripts/bash/create-phr.sh --title "<title>" --stage <stage> [--feature <name>] --json`
   - Open the file and fill remaining placeholders (YAML + body), embedding full PROMPT_TEXT (verbatim) and concise RESPONSE_TEXT.
   - If the script fails:
     - Read `.specify/templates/phr-template.prompt.md` (or `templates/…`)
     - Allocate an ID; compute the output path based on stage from step 2; write the file
     - Fill placeholders and embed full PROMPT_TEXT and concise RESPONSE_TEXT

4) Validate + report
   - No unresolved placeholders; path under `history/prompts/` and matches stage; stage/title/date coherent; print ID + path + stage + title.
   - On failure: warn, don't block. Skip only for `/sp.phr`.


/sp.constitution Project: Integrated RAG Chatbot Development - Build and embed a Retrieval-Augmented Generation (RAG) chatbot within a published book, using SpecifyPlus and Qwen CLI for development. The chatbot leverages Cohere API for language model capabilities (replacing OpenAI Agents/ChatKit SDKs), integrated with FastAPI for backend, Neon Serverless Postgres for database management, and Qdrant Cloud Free Tier for vector storage. It must accurately answer user questions about the book's content, including responses based solely on user-selected text passages.
Core principles:
Precision in retrieval and generation through vector embeddings and semantic search
User-centric functionality (seamless integration into the book, handling general and selected-text queries)
Scalability and efficiency (using free-tier services without compromising performance)
Security and privacy (no storage of user data beyond session, API key handling best practices)
Modularity (clean separation of retrieval, augmentation, and generation components)
Key standards:
All responses must be grounded in the book's content or user-selected text
API integration: Exclusive use of Cohere API keys for LLM operations
Code quality: PEP 8 compliant Python code, with comprehensive error handling and logging
Database usage: Efficient schema design in Neon Postgres for metadata storage (e.g., book chunks, embeddings)
Vector database: Qdrant for storing and querying embeddings with cosine similarity threshold >0.8 for relevance
Testing: Unit tests for each component (retrieval accuracy >95%, generation coherence), end-to-end integration tests
Documentation: Inline comments, README with setup instructions, and deployment guide
Constraints:
Tech stack: Cohere API, FastAPI, Neon Serverless Postgres, Qdrant Cloud Free Tier, SpecifyPlus, Qwen CLI
No paid tiers beyond free limits (e.g., Qdrant free tier storage caps)
Development environment: Python 3.10+, no additional proprietary tools
Embedding model: Use Cohere's embed-v3 or equivalent free access
Deployment: Embeddable in a web-based book format (e.g., via iframe or JavaScript integration)
Response latency: Under 2 seconds for queries
Success criteria:
Chatbot accurately answers 100% of test queries based on book content or selected text without hallucination
Seamless embedding into the published book with no UI/UX issues
Passes code review for modularity, security, and efficiency
Zero API key exposure or security vulnerabilities detected
Positive user feedback simulation (e.g., 90%+ satisfaction in mock interactions)
Fully reproducible build process via provided documentation

## Response snapshot

I've successfully created and updated the project constitution for your Integrated RAG Chatbot Development project. Here's the summary:

**New Version**: 1.0.0 (initial version)
**Bump Rationale**: This is the initial constitution for the project, establishing core principles and guidelines for developing an Integrated RAG Chatbot for Published Book.

**Files Updated**:
- `.specify/memory/constitution.md` - Contains the complete project constitution with all principles and governance rules

**Constitution Overview**:
The constitution establishes six core principles:
1. Precision in Retrieval and Generation - Ensuring accurate retrieval through vector embeddings with cosine similarity threshold >0.8
2. User-Centric Functionality - Providing seamless book integration with sub-2-second response times
3. Scalability and Efficiency - Using free-tier services without compromising performance
4. Security and Privacy - No storage of user data beyond sessions and secure API key handling
5. Modularity - Clean separation of retrieval, augmentation, and generation components
6. Content Grounding - All responses must be grounded in book content without hallucination

**Suggested Commit Message**:
`docs: add constitution for Integrated RAG Chatbot project v1.0.0`

The constitution also defines technology stack standards (Cohere API, FastAPI, Neon Postgres, Qdrant), quality assurance requirements (unit tests with >95% accuracy), and governance rules to ensure the project stays aligned with its core objectives.

All placeholder tokens have been properly replaced, dates are in ISO format, and the principles are specific and testable. The constitution is now ready to guide your project development.

## Outcome

- ✅ Impact: Created initial project constitution with 6 core principles and governance rules
- 🧪 Tests: No tests required for this documentation task
- 📁 Files: Updated .specify/memory/constitution.md with complete constitution
- 🔁 Next prompts: Ready to proceed with feature specification based on this constitution
- 🧠 Reflection: Successfully transformed template with placeholders into complete project constitution

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Begin feature specification based on this constitution