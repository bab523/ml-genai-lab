import ast, glob, operator, re, sqlite3
import numpy as np
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

DB = "data/clients.db"

def sql_query(query: str) -> str:
    """Run a read-only SQL SELECT on tables clients(client_id,name,risk_profile,tax_bracket)
    and holdings(client_id,asset_class,sector,balance). Returns rows as text."""
    if not query.strip().lower().startswith("select"):
        return "ERROR: only SELECT queries are allowed."
    try:
        con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
        cur = con.execute(query)
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()
        con.close()
        return str(cols) + "\n" + "\n".join(str(r) for r in rows[:30]) if rows else "no rows"
    except Exception as e:
        return f"ERROR: {e}"

# ---- market RAG (reuses the idea from P5) ----
_emb = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
_chunks = []
for p in sorted(glob.glob("data/reports/*.pdf")):
    txt = "\n".join(pg.extract_text() or "" for pg in PdfReader(p).pages)
    for line in txt.splitlines():
        if len(line.strip()) > 30:
            _chunks.append((p.split("/")[-1], line.strip()))
_vecs = _emb.encode([c[1] for c in _chunks], normalize_embeddings=True)

def market_search(question: str) -> str:
    """Search the market outlook and tax PDFs. Returns the 3 most relevant lines."""
    s = _vecs @ _emb.encode([question], normalize_embeddings=True)[0]
    top = np.argsort(-s)[:3]
    return "\n".join(f"[{_chunks[i][0]}] {_chunks[i][1]}" for i in top)

_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.USub: operator.neg, ast.Pow: operator.pow}

def _ev(n):
    if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
        return n.value
    if isinstance(n, ast.BinOp) and type(n.op) in _OPS:
        return _OPS[type(n.op)](_ev(n.left), _ev(n.right))
    if isinstance(n, ast.UnaryOp) and type(n.op) in _OPS:
        return _OPS[type(n.op)](_ev(n.operand))
    raise ValueError("unsupported expression")

def calculator(expression: str) -> str:
    """Evaluate arithmetic like '420000 * -0.12 * 0.32'. Supports + - * / **. No variables."""
    try:
        return str(round(_ev(ast.parse(expression.replace(",", "").strip(), mode="eval").body), 4))
    except Exception as e:
        return f"ERROR: {e}"

TOOLS = {"sql_query": sql_query, "market_search": market_search, "calculator": calculator}

if __name__ == "__main__":
    print(sql_query("SELECT * FROM clients"))
    print(market_search("technology equities outlook"))
    print(calculator("420000 * -0.12 * 0.32"))
