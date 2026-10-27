import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from llm_router import classify

N = int(os.getenv("N", 30))
df = pd.read_csv("data/tickets.csv").sample(N, random_state=1)

rows, log = [], []
for variant in ["zero_shot", "few_shot", "cot"]:
    ok_cat = ok_pri = fails = 0
    lat = []
    for _, r in df.iterrows():
        try:
            res, sec = classify(r.text, variant)
        except Exception as e:
            fails += 1
            log.append({"variant": variant, "ticket_id": r.ticket_id, "error": str(e)[:150]})
            continue
        lat.append(sec)
        ok_cat += res.category == r.true_category
        ok_pri += res.priority == r.true_priority
        log.append({"variant": variant, "ticket_id": r.ticket_id, "category": res.category,
                    "priority": res.priority, "draft": res.draft_response})
    rows.append({"variant": variant,
                 "category_acc": round(ok_cat / N, 3),
                 "priority_acc": round(ok_pri / N, 3),
                 "avg_latency_s": round(sum(lat) / max(len(lat), 1), 2),
                 "failures": fails})
    print(rows[-1])

res = pd.DataFrame(rows).set_index("variant")
res.to_csv("outputs/prompt_benchmark.csv")
pd.DataFrame(log).to_csv("outputs/benchmark_log.csv", index=False)
print("\n", res)

fig, ax = plt.subplots(1, 2, figsize=(10, 4))
res[["category_acc", "priority_acc"]].plot.bar(ax=ax[0], rot=0, title="Accuracy"); ax[0].set_ylim(0, 1)
res["avg_latency_s"].plot.bar(ax=ax[1], rot=0, title="Avg latency (s)")
plt.tight_layout(); plt.savefig("outputs/prompt_benchmark.png", dpi=150)
