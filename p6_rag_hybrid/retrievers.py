import json, re, glob, os
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer, CrossEncoder

def tok(s):
    return re.findall(r"[a-z0-9\.\(\)\-]+", s.lower())

# ---- Load: one chunk per clause, prefixed with the contract id ----
chunks = []
for path in sorted(glob.glob("data/contracts/*.txt")):
    cid = os.path.basename(path).replace(".txt", "")
    text = open(path).read()
    for m in re.finditer(r"Clause (\d+)\. ([^\n]+)\nSection ([^:]+): ([^\n]+)", text):
        no, title, sec, body = m.groups()
        chunks.append({"id": f"{cid}#{no}", "contract": cid, "title": title, "section": sec,
                       "text": f"[{cid}] Clause {no}. {title} Section {sec}: {body}"})
texts = [c["text"] for c in chunks]

# ---- Indexes ----
bm25 = BM25Okapi([tok(t) for t in texts])
embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
emb = embedder.encode(texts, normalize_embeddings=True, show_progress_bar=False)
_reranker = None

def bm25_rank(q, k=20):
    s = bm25.get_scores(tok(q))
    return list(np.argsort(-s)[:k])

def dense_rank(q, k=20):
    s = emb @ embedder.encode([q], normalize_embeddings=True)[0]
    return list(np.argsort(-s)[:k])

def rrf(rank_lists, k=60):
    score = {}
    for rl in rank_lists:
        for pos, idx in enumerate(rl):
            score[idx] = score.get(idx, 0) + 1 / (k + pos + 1)
    return [i for i, _ in sorted(score.items(), key=lambda x: -x[1])]

def hybrid_rank(q, k=20):
    return rrf([bm25_rank(q, 30), dense_rank(q, 30)])[:k]

def rerank(q, idxs, top_n=3):
    global _reranker
    if _reranker is None:
        _reranker = CrossEncoder("BAAI/bge-reranker-base")
    scores = _reranker.predict([(q, texts[i]) for i in idxs])
    order = np.argsort(-np.array(scores))[:top_n]
    return [idxs[i] for i in order]

def retrieve(q, method="hybrid_rerank", top_n=3):
    if method == "bm25":
        return bm25_rank(q, top_n)
    if method == "dense":
        return dense_rank(q, top_n)
    if method == "hybrid":
        return hybrid_rank(q, top_n)
    if method == "hybrid_rerank":
        return rerank(q, hybrid_rank(q, 20), top_n)
    raise ValueError(method)

if __name__ == "__main__":
    print("chunks:", len(chunks))
    q = "MSA-2025-107 Clause 3 limitation of liability cap"
    for m in ["bm25", "dense", "hybrid", "hybrid_rerank"]:
        print(f"\n[{m}]")
        for i in retrieve(q, m, 3):
            print(" ", chunks[i]["id"], "|", chunks[i]["title"])
