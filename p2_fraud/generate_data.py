import numpy as np
import pandas as pd

rng = np.random.default_rng(7)

n = 60000
fraud = rng.random(n) < 0.02
tx = pd.DataFrame({
    "amount": np.where(fraud, rng.lognormal(5.5, 1.0, n), rng.lognormal(3.8, 1.0, n)),
    "location_delta_km": np.where(fraud, rng.exponential(300, n), rng.exponential(20, n)),
    "new_device": np.where(fraud, rng.random(n) < 0.6, rng.random(n) < 0.05).astype(int),
    "txns_last_hour": np.where(fraud, rng.poisson(5, n), rng.poisson(1, n)),
    "account_age_days": np.where(fraud, rng.integers(1, 400, n), rng.integers(1, 3000, n)),
    "hour": rng.integers(0, 24, n),
    "is_fraud": fraud.astype(int),
})
tx.to_csv("data/transactions.csv", index=False)
print("transactions:", len(tx), "| fraud rate:", round(tx.is_fraud.mean(), 4))

groups = {
    "budget":     (30, 12, 0.02, 800),
    "regular":    (80, 25, 0.05, 1500),
    "high_value": (400, 40, 0.15, 2500),
    "risky":      (150, 60, 0.45, 200),
}
rows = []
for name, (spend, freq, intl, age) in groups.items():
    m = 750
    rows.append(pd.DataFrame({
        "avg_spend": rng.normal(spend, spend * 0.2, m).clip(5),
        "txns_per_month": rng.normal(freq, freq * 0.2, m).clip(1),
        "intl_share": rng.normal(intl, 0.04, m).clip(0, 1),
        "account_age_days": rng.normal(age, age * 0.25, m).clip(10),
    }))
cust = pd.concat(rows, ignore_index=True).sample(frac=1, random_state=1)
cust.to_csv("data/customers.csv", index=False)
print("customers:", len(cust))
