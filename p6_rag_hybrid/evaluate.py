import json, random
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from retrievers import chunks, retrieve

random.seed(2)
truth = json.load(open("data/truth.json"))
id_of = {(c["contract"].replace(".txt", ""), c["title"]): i for i, c in enumerate(chunks)}

PARAPHRASE = {
 "Limitation of Liability": "what is the maximum amount either side can be made to pay if something goes wrong",
 "Payment Terms": "how long does the customer have to settle an invoice and what happens if they are late",
 "Termination for Cause": "can the agreement be ended right away if the other side seriously breaks it",
 "Data Protection": "how fast must the supplier tell us if personal information is leaked",
 "Service Levels": "what uptime is guaranteed and what compensation applies if it is missed",
 "Governing Law": "which country's courts decide disputes",
 "Insurance": "what insurance cover must the vendor carry",
 "Confidentiality": "how long must secrets be kept after the contract ends",
}

tests = []
for t in random.sample(truth, 25):    # exact: names the contract and section number
    cid = t["contract"].replace(".txt", "")
    tests.append(("exact", f"{cid} Section {t['section']} {t['title']}", id_of[(cid, t["title"])]))
for t in truth:                        # semantic: paraphrase, names the supplier only
    if t["title"] in PARAPHRASE and random.random() < 0.55:
        cid = t["contract"].replace(".txt", "")
        tests.append(("semantic", f"{PARAPHRASE[t['title']]} in the {t['supplier']} agreement", id_of[(cid, t["title"])]))
print("test questions:", len(tests), "(exact:", sum(1 for t in tests if t[0] == "exact"), ")")

rows = []
for method in ["bm25", "dense", "hybrid", "hybrid_rerank"]:
    for kind in ["exact", "semantic", "all"]:
        sub = [t for t in tests if kind == "all" or t[0] == kind]
        top1 = hit3 = 0
        for _, q, gold in sub:
            r = retrieve(q, method, 3)
            top1 += r[0] == gold
            hit3 += gold in r
        n = len(sub)
        rows.append({"method": method, "queries": kind, "n": n,
                     "precision@1": round(top1 / n, 3), "recall@3": round(hit3 / n, 3)})
    print(method, "done")

res = pd.DataFrame(rows)
res.to_csv("outputs/retrieval_benchmark.csv", index=False)
print(res.pivot(index="method", columns="queries", values="recall@3"))
print(res.pivot(index="method", columns="queries", values="precision@1"))

pv = res[res.queries == "all"].set_index("method")[["precision@1", "recall@3"]]
pv.plot.bar(rot=0, title="Retrieval quality (all queries)"); plt.ylim(0, 1.05)
plt.tight_layout(); plt.savefig("outputs/retrieval_benchmark.png", dpi=150)
print("saved outputs/retrieval_benchmark.csv and .png")
