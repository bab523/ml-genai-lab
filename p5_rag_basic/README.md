# P5: Basic RAG over Clinical Documents
- Data: 5 synthetic clinical documents (PDF, Markdown, TXT) from make_docs.py. They are fictional and not for clinical use.
- Parsing: pypdf for PDFs; plain read for md and txt.
- Chunking: (a) fixed 500 chars with 100 overlap; (b) header-based, one chunk per section.
- Embeddings: sentence-transformers/all-MiniLM-L6-v2 (normalized); ChromaDB with cosine similarity.
- Evaluation: 12 patient-style questions that use different wording from the documents; metrics in outputs/chunking_comparison.csv.
- Run order: make_docs.py, ingest.py, evaluate.py ("your question" for a search).
- Note: data/ is git-ignored, so regenerate it by running make_docs.py and ingest.py.
