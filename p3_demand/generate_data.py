import numpy as np
import pandas as pd

rng = np.random.default_rng(3)
n_sku, n_days = 200, 365
dates = pd.date_range("2025-01-01", periods=n_days)
sku_cat = rng.integers(0, 5, n_sku)
sku_base = rng.lognormal(3.0, 0.5, n_sku)

frames = []
for s in range(n_sku):
    d = pd.DataFrame({"sku": s, "date": dates})
    d["category"] = sku_cat[s]
    d["dow"] = d["date"].dt.dayofweek
    d["month"] = d["date"].dt.month
    d["discount"] = rng.choice([0, 0.1, 0.2, 0.3, 0.5], n_days, p=[.6, .15, .1, .1, .05])
    d["temp_c"] = 20 + 10 * np.sin(2 * np.pi * (d["date"].dt.dayofyear - 80) / 365) + rng.normal(0, 3, n_days)
    d["ship_delay_days"] = rng.poisson(2, n_days)
    d["sku_avg_demand"] = round(sku_base[s], 2)

    season = 1 + 0.4 * np.sin(2 * np.pi * (d["month"] - 1) / 12) + 0.8 * (d["month"] >= 11)
    weekend = 1 + 0.3 * (d["dow"] >= 5)
    promo = 1 + 3 * d["discount"] ** 1.5 * (1 + (d["category"] == 2))   # category x discount interaction
    weather = 1 + 0.03 * (d["temp_c"] - 20) * (d["category"] == 1)       # weather matters for one category
    delay = np.exp(-0.12 * d["ship_delay_days"])                         # delays suppress sales
    mu = sku_base[s] * season * weekend * promo * weather * delay
    d["units"] = rng.poisson(mu)
    frames.append(d)

data = pd.concat(frames, ignore_index=True)
data.to_csv("data/demand.csv", index=False)
print("rows:", len(data), "| mean units/day:", round(data.units.mean(), 1))
