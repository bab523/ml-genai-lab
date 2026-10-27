import sys
import chromadb
import pandas as pd
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="data/chroma")

def search(strategy, query, k=3):
    col = client.get_collection(f"clinical_{strategy}")
    q = model.encode([query], normalize_embeddings=True).tolist()
    r = col.query(query_embeddings=q, n_results=k)
    return [{"source": m["source"], "text": d, "score": 1 - dist}
            for d, m, dist in zip(r["documents"][0], r["metadatas"][0], r["distances"][0])]

# interactive mode: python evaluate.py "your question"
if len(sys.argv) > 1:
    q = " ".join(sys.argv[1:])
    for s in ["fixed", "header"]:
        print(f"\n=== {s} ===")
        for h in search(s, q):
            print(f"[{h['score']:.2f}] {h['source']}: {h['text'][:200].replace(chr(10), ' ')}...")
    sys.exit()

TESTS = [
 ("Patient is very thirsty, urinating constantly and has lost weight", "diabetes_protocol.txt", "hba1c"),
 ("Elderly patient on a blood thinner was just prescribed an antibiotic", "drug_interactions.pdf", "inr"),
 ("Patient on an ACE inhibitor developed a dry irritating cough", "hypertension_guideline.md", "cough"),
 ("Blood pressure 200/130 with chest pain and confusion, what drug to give", "hypertension_guideline.md", "nicardipine"),
 ("Septic patient still has low blood pressure after fluids, which drug next", "sepsis_protocol.pdf", "norepinephrine"),
 ("How much fluid should a septic patient receive", "sepsis_protocol.pdf", "30 ml/kg"),
 ("Muscle pain and dark urine in a patient taking a cholesterol drug with an antibiotic", "drug_interactions.pdf", "rhabdomyolysis"),
 ("Patient wheezing badly and too breathless to talk", "asthma_guideline.md", "full sentences"),
 ("Low blood sugar in a conscious patient, what should I give", "diabetes_protocol.txt", "15 grams"),
 ("Which blood pressure medicines are safe for a pregnant woman", "hypertension_guideline.md", "methyldopa"),
 ("Agitation, tremor and sweating after starting an antidepressant together with a painkiller", "drug_interactions.pdf", "serotonin syndrome"),
 ("Diabetic patient with vomiting, fruity breath and deep fast breathing", "diabetes_protocol.txt", "ketoacidosis"),
]

rows, examples = [], []
for s in ["fixed", "header"]:
    src1 = ans1 = ans3 = 0
    chars = []
    for q, src, kw in TESTS:
        hits = search(s, q, 3)
        src1 += hits[0]["source"] == src
        ans1 += kw in hits[0]["text"].lower()
        ans3 += any(kw in h["text"].lower() for h in hits)
        chars.append(sum(len(h["text"]) for h in hits))
        if q == TESTS[0][0] or q == TESTS[1][0]:
            examples.append(f"### [{s}] {q}\n- top hit: {hits[0]['source']} (score {hits[0]['score']:.2f})\n"
                            f"- text: {hits[0]['text'][:300].replace(chr(10), ' ')}\n")
    n = len(TESTS)
    rows.append({"strategy": s, "top1_correct_doc": round(src1 / n, 3),
                 "top1_has_answer": round(ans1 / n, 3), "top3_has_answer": round(ans3 / n, 3),
                 "avg_context_chars": round(sum(chars) / n)})

res = pd.DataFrame(rows).set_index("strategy")
print(res)
res.to_csv("outputs/chunking_comparison.csv")

with open("outputs/chunking_report.md", "w") as f:
    f.write("# Chunking strategy comparison\n\n")
    f.write("| strategy | top1_correct_doc | top1_has_answer | top3_has_answer | avg_context_chars |\n|---|---|---|---|---|\n")
    for s, r in res.iterrows():
        f.write(f"| {s} | {r.top1_correct_doc} | {r.top1_has_answer} | {r.top3_has_answer} | {int(r.avg_context_chars)} |\n")
    f.write("\n## Example retrievals\n\n" + "\n".join(examples))
print("Saved outputs/chunking_comparison.csv and outputs/chunking_report.md")
