# P4: Support Ticket Router (LLM API and Prompt Engineering)
- Model: local llama3.2:3b via Ollama (OpenAI-compatible API). Any provider works through .env.
- Data: 60 synthetic labeled tickets (generate_tickets.py); the benchmark uses a 30-ticket sample.
- Output: Pydantic-validated JSON (priority, category, draft_response).
- Reliability: tenacity retries with exponential backoff; retried on API errors and invalid JSON.
- Prompt variants: zero-shot, few-shot, chain-of-thought. Results: outputs/prompt_benchmark.csv.
- Setup: copy .env.example values into .env (never commit keys).
