# P4: Support Ticket Router (LLM API and Prompt Engineering)
- Model: local llama3.2:3b via Ollama (OpenAI-compatible API). Any provider works through .env.
- Data: 60 synthetic labeled tickets (generate_tickets.py); the benchmark uses a 30-ticket sample.
- Output: Pydantic-validated JSON (priority, category, draft_response).
- Reliability: tenacity retries with exponential backoff; retried on API errors and invalid JSON.
- Prompt variants: zero-shot, few-shot, chain-of-thought. Results: outputs/prompt_benchmark.csv.
- Setup: copy .env.example values into .env (never commit keys).

## Findings
- Few-shot gave the best category accuracy (0.933) and the lowest latency (5.3 s).
- Chain-of-thought did not help the 3B model (category 0.767) and was slower than few-shot.
- Priority accuracy was about 0.6-0.67 for all variants. Priority labels are subjective, and 30 tickets is a small sample, so those differences are noise.
- Zero-shot latency includes the model warm-up on the first call.
