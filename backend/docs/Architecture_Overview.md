
## docs/Architecture_Overview.md

```markdown
# HealthConnect AI - Architecture Overview

## System Architecture
The HealthConnect AI Assistant is built on a multi-layer architecture:

1. **User Layer**: Web and mobile interfaces
2. **API Gateway**: Authentication, rate limiting
3. **Application Layer**: FastAPI server with services
4. **AI Layer**: Multi-agent system and RAG pipeline
5. **MCP Layer**: Tool integration servers
6. **Data Layer**: PostgreSQL, Redis, Pinecone

## Multi-Agent System
- Intent Router Agent
- Conversation Agent
- Knowledge Agent
- Safety Agent
- Action Agent
- Summary Agent
- Feedback Agent
- Analytics Agent

## RAG Pipeline
1. Document Ingestion
2. Chunking
3. Embedding
4. Vector Storage
5. Retrieval
6. Re-ranking
7. Context Building
8. Citation Generation