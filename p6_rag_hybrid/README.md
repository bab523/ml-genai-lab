# P6: Hybrid RAG with Cross-Encoder Re-Ranking
- Data: 6 synthetic master services agreements, 60 clauses (make_contracts.py).
- Chunking: one clause per chunk, prefixed with the contract id.
- Retrievers: BM25 (rank_bm25), dense (all-MiniLM-L6-v2), hybrid (Reciprocal Rank Fusion, k=60),
  hybrid + BAAI/bge-reranker-base cross-encoder (top 20 -> top 3).
- Evaluation: exact-reference queries vs paraphrased queries; precision@1 and recall@3 in outputs/retrieval_benchmark.csv.
- Generation: answer.py uses a local llama3.2:3b with enforced clause-id citations and refusal when the context lacks the answer.
- Run order: make_contracts.py, retrievers.py, evaluate.py, answer.py.
