import os, random
os.makedirs("data/contracts", exist_ok=True)
random.seed(11)

CLAUSES = [
 ("Term and Renewal", "This Agreement begins on the Effective Date and continues for an initial term of {n} years. It renews automatically for successive one-year periods unless either party gives {d} days written notice of non-renewal."),
 ("Payment Terms", "Customer shall pay each invoice within {d} days of receipt. Late amounts accrue interest at {p} percent per month. Disputed amounts must be notified in writing within 15 days."),
 ("Limitation of Liability", "Neither party's total liability shall exceed {p} times the fees paid in the twelve months preceding the claim. This cap does not apply to breach of confidentiality or indemnification obligations."),
 ("Termination for Cause", "Either party may terminate this Agreement immediately by written notice if the other party materially breaches and fails to cure within {d} days of notice."),
 ("Confidentiality", "Each party shall protect the other's Confidential Information with at least reasonable care and shall not disclose it for {n} years after termination."),
 ("Data Protection", "Supplier shall process personal data only on documented instructions and shall notify Customer of any personal data breach within {h} hours of becoming aware."),
 ("Indemnification", "Supplier shall indemnify Customer against third-party claims alleging that the Services infringe intellectual property rights, subject to prompt notice and sole control of the defence."),
 ("Governing Law", "This Agreement is governed by the laws of {law}. The courts of {law} have exclusive jurisdiction over any dispute."),
 ("Force Majeure", "Neither party is liable for delay caused by events beyond its reasonable control, including natural disasters, war or government action, provided it gives notice within {d} days."),
 ("Assignment", "Neither party may assign this Agreement without the other's prior written consent, except to a successor in a merger or sale of substantially all assets."),
 ("Service Levels", "Supplier shall maintain monthly availability of {av} percent. Failure entitles Customer to a service credit of {p} percent of the monthly fee per full percentage point below target."),
 ("Insurance", "Supplier shall maintain commercial general liability insurance of at least USD {m} million per occurrence throughout the term."),
]
LAWS = ["England and Wales", "New York", "Singapore", "Delaware", "Ireland", "Karnataka, India"]
NAMES = [("Aldrin Logistics", "Nimbus Cloud"), ("Borealis Retail", "Vertex Software"),
         ("Cobalt Energy", "Helix Analytics"), ("Dune Pharma", "Orbit Data"),
         ("Everest Banking", "Quanta Systems"), ("Fjord Shipping", "Lumen Networks")]

truth = []
for i, (cust, sup) in enumerate(NAMES, 1):
    code = f"MSA-{2024 + i % 3}-{100 + i * 7}"
    lines = [f"MASTER SERVICES AGREEMENT {code}", "",
             f"Between {cust} (Customer) and {sup} (Supplier). Synthetic lab document.", ""]
    picks = random.sample(CLAUSES, 10)
    for idx, (title, tpl) in enumerate(picks, 1):
        vals = dict(n=random.choice([2, 3, 5]), d=random.choice([15, 30, 45, 60, 90]),
                    p=random.choice([1, 2, 5, 10]), h=random.choice([24, 48, 72]),
                    av=random.choice(["99.5", "99.9", "99.95"]), m=random.choice([2, 5, 10]),
                    law=random.choice(LAWS))
        body = tpl.format(**vals)
        sub = f"{idx}.{random.randint(1, 3)}({random.choice('abc')})"
        lines += [f"Clause {idx}. {title}", f"Section {sub}: {body}", ""]
        truth.append({"contract": f"{code}.txt", "customer": cust, "supplier": sup, "clause_no": idx,
                      "section": sub, "title": title, "text": body})
    open(f"data/contracts/{code}.txt", "w").write("\n".join(lines))
    print("created", code, "-", cust, "/", sup)

import json
json.dump(truth, open("data/truth.json", "w"), indent=1)
print("clauses:", len(truth))
