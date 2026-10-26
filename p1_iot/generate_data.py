import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
frames = []
start = pd.Timestamp("2026-01-01")

for machine_id in range(1, 101):
    life = int(rng.integers(300, 600))      # operating hours until failure
    hours = np.arange(life)
    rul = life - hours                      # remaining useful life
    wear = 1 - rul / life                   # 0 = new, 1 = failing

    df = pd.DataFrame({
        "machine_id": machine_id,
        "timestamp": start + pd.to_timedelta(hours, unit="h"),
        "vibration": 0.5 + 2.0 * wear**2 + rng.normal(0, 0.15, life),
        "temperature": 60 + 25 * wear + rng.normal(0, 2, life),
        "voltage": 230 - 8 * wear + rng.normal(0, 1.5, life),
        "noise": 65 + 15 * wear**1.5 + rng.normal(0, 1.5, life),
        "rul_hours": rul,
    })
    df["failure_24h"] = (df["rul_hours"] <= 24).astype(int)
    frames.append(df)

data = pd.concat(frames, ignore_index=True)

# Make it dirty: 2% missing values per sensor, plus a few spikes
for col in ["vibration", "temperature", "voltage", "noise"]:
    idx = rng.choice(data.index, size=int(0.02 * len(data)), replace=False)
    data.loc[idx, col] = np.nan
spikes = rng.choice(data.index, size=50, replace=False)
data.loc[spikes, "vibration"] *= 5

data.to_csv("data/telemetry.csv", index=False)
print("rows:", len(data), "| failure rate:", round(data["failure_24h"].mean(), 3))
