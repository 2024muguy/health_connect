# HealthConnect AI - LLM Provider Status

## ✅ Active Providers

| Priority | Provider | Type | Model | Latency | Status |
|----------|----------|------|-------|---------|--------|
| 1 (Primary) | Groq | Cloud | openai/gpt-oss-20b | ~576ms | ✅ Working |
| 2 (Fallback) | Ollama | Local | llama3.1 | ~141s | ✅ Working |

## Embeddings

| Provider | Model | Dimensions | Status |
|----------|-------|------------|--------|
| Ollama | nomic-embed-text | 768 | ✅ Working |

## Configuration

- **Groq**: Free tier, 30 requests/min, no credit card needed
- **Ollama**: Local, unlimited, works offline
- **Fallback logic**: Groq → Ollama (automatic)

## Performance

- Groq is **245x faster** than Ollama for text generation
- Groq: 576ms average response time
- Ollama: 141s average (CPU-bound on 4-core system)
