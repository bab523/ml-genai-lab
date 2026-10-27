import glob, os, re
import pandas as pd
import chromadb
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

HEAD = re.compile(r"^(#{1,3}\s+.+|\d+\.\s+[A-Z][^.]{2,70})$")

def load(path):
    if path.endswith(".pdf"):
        return "\n".join((p.extract_text() or "") for p in PdfReader(path).pages)
    return open(path, encoding="utf-8").read()

def fixed_chunks(text, size=500, overlap=100):
    text = re.sub(r"\s+", " ", text).strip()
    out, i = [], 0
    while i < len(text):
        out.append(text[i:i + size])
        i += size - overlap
    return out

def header_chunks(text, max_chars=1200):
    chunks, head, buf = [], None, []
    def flush():
        body = " ".join(buf).strip()
        if head and len(body) > 100:
            t = f"{head}\n{body}"
            chunks.extend([t] if len(t) <= max_chars else fixed_chunks(t, max_chars, 150))
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if HEAD.match(line):
            flush()
            head = re.sub(r"^#+\s*|^\d+\.\s*", "", line)
            buf = []
        else:
            buf.append(line)
    flush()
    return chunks

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="data/chroma")
stats = []

for strategy, fn in [("fixed", fixed_chunks), ("header", header_chunks)]:
    name = f"clinical_{strategy}"
    try:
        client.delete_collection(name)
    except Exception:
        pass
    col = client.create_collection(name, metadata={"hnsw:space": "cosine"})
    ids, docs, metas = [], [], []
    for path in sorted(glob.glob("data/docs/*")):
        src = os.path.basename(path)
        for i, ch in enumerate(fn(load(path))):
            ids.append(f"{src}-{i}"); docs.append(ch)
            metas.append({"source": src, "strategy": strategy})
    emb = model.encode(docs, normalize_embeddings=True, show_progress_bar=False).tolist()
    col.add(ids=ids, documents=docs, embeddings=emb, metadatas=metas)
    lens = [len(d) for d in docs]
    stats.append({"strategy": strategy, "chunks": len(docs),
                  "avg_chars": round(sum(lens) / len(lens)), "min_chars": min(lens), "max_chars": max(lens)})

df = pd.DataFrame(stats).set_index("strategy")
print(df)
df.to_csv("outputs/chunk_stats.csv")
