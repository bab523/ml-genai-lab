import json, time
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import optuna
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error

torch.manual_seed(0); np.random.seed(0)
optuna.logging.set_verbosity(optuna.logging.WARNING)

# ---------- Data ----------
df = pd.read_csv("data/demand.csv", parse_dates=["date"])
df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)
df = pd.get_dummies(df, columns=["category", "dow"], dtype=float)
FEATS = [c for c in df.columns if c not in ("sku", "date", "units", "month")]

t0 = df["date"].min()
train = df[df["date"] < t0 + pd.Timedelta(days=270)]
val = df[(df["date"] >= t0 + pd.Timedelta(days=270)) & (df["date"] < t0 + pd.Timedelta(days=320))]
test = df[df["date"] >= t0 + pd.Timedelta(days=320)]
print(f"train {len(train)} | val {len(val)} | test {len(test)} | features {len(FEATS)}")

sc = StandardScaler().fit(train[FEATS])
def tens(d):
    X = torch.tensor(sc.transform(d[FEATS]), dtype=torch.float32)
    y = torch.tensor(np.log1p(d["units"].values), dtype=torch.float32).unsqueeze(1)
    return X, y
Xtr, ytr = tens(train); Xva, yva = tens(val); Xte, yte = tens(test)

def rmse_orig(model, X, units):
    model.eval()
    with torch.no_grad():
        p = np.expm1(model(X).squeeze(1).numpy()).clip(0)
    return float(np.sqrt(mean_squared_error(units, p))), float(mean_absolute_error(units, p))

# ---------- Model ----------
def build(in_dim, layers, width, dropout, act):
    mods, d = [], in_dim
    for _ in range(layers):
        mods += [nn.Linear(d, width), nn.BatchNorm1d(width), act(), nn.Dropout(dropout)]
        d = width
    mods.append(nn.Linear(d, 1))
    return nn.Sequential(*mods)

ACTS = {"relu": nn.ReLU, "tanh": nn.Tanh, "gelu": nn.GELU}

def fit(p, epochs):
    model = build(Xtr.shape[1], p["layers"], p["width"], p["dropout"], ACTS[p["act"]])
    opt = torch.optim.Adam(model.parameters(), lr=p["lr"], weight_decay=p["l2"])  # weight_decay = L2 penalty
    loss_fn = nn.MSELoss()
    hist = {"train": [], "val": []}
    best_rmse, best_state = 1e9, None
    for ep in range(epochs):
        model.train()
        perm = torch.randperm(len(Xtr)); tot = 0.0
        for i in range(0, len(Xtr), 512):
            idx = perm[i:i + 512]
            if len(idx) < 2:
                continue
            opt.zero_grad()
            loss = loss_fn(model(Xtr[idx]), ytr[idx])
            loss.backward(); opt.step()
            tot += loss.item() * len(idx)
        model.eval()
        with torch.no_grad():
            vloss = loss_fn(model(Xva), yva).item()
        hist["train"].append(tot / len(Xtr)); hist["val"].append(vloss)
        v, _ = rmse_orig(model, Xva, val["units"].values)
        if v < best_rmse:
            best_rmse = v
            best_state = {k: t.clone() for k, t in model.state_dict().items()}
    model.load_state_dict(best_state)
    return model, best_rmse, hist

# ---------- Optuna tuning ----------
def objective(trial):
    p = {
        "layers": trial.suggest_int("layers", 1, 4),
        "width": trial.suggest_categorical("width", [32, 64, 128, 256]),
        "dropout": trial.suggest_float("dropout", 0.0, 0.4),
        "lr": trial.suggest_float("lr", 1e-4, 1e-2, log=True),
        "l2": trial.suggest_float("l2", 1e-6, 1e-2, log=True),
        "act": trial.suggest_categorical("act", ["relu", "tanh", "gelu"]),
    }
    _, v, _ = fit(p, epochs=20)
    return v

print("Tuning with Optuna (20 trials)...")
start = time.time()
study = optuna.create_study(direction="minimize", sampler=optuna.samplers.TPESampler(seed=0))
study.optimize(objective, n_trials=20)
print(f"Tuning took {time.time() - start:.0f}s | best val RMSE {study.best_value:.3f}")
print("Best params:", study.best_params)
trials = study.trials_dataframe()
trials.to_csv("outputs/tuning_trials.csv", index=False)
json.dump(study.best_params, open("outputs/best_params.json", "w"), indent=2)

# ---------- Final model ----------
model, _, hist = fit(study.best_params, epochs=60)
mlp_rmse, mlp_mae = rmse_orig(model, Xte, test["units"].values)

# ---------- Baseline: Random Forest ----------
rf = RandomForestRegressor(n_estimators=200, min_samples_leaf=3, n_jobs=-1, random_state=0)
rf.fit(train[FEATS], train["units"])
rf_pred = rf.predict(test[FEATS])
rf_rmse = float(np.sqrt(mean_squared_error(test["units"], rf_pred)))
rf_mae = float(mean_absolute_error(test["units"], rf_pred))

# untuned MLP for comparison
default_p = {"layers": 2, "width": 64, "dropout": 0.1, "lr": 1e-3, "l2": 1e-5, "act": "relu"}
dm, _, _ = fit(default_p, epochs=60)
d_rmse, d_mae = rmse_orig(dm, Xte, test["units"].values)

res = pd.DataFrame({
    "RMSE": [rf_rmse, d_rmse, mlp_rmse],
    "MAE": [rf_mae, d_mae, mlp_mae],
}, index=["Random Forest baseline", "MLP default (untuned)", "MLP tuned (Optuna)"]).round(3)
print("\n=== Test set results (units/day) ===")
print(res)
res.to_csv("outputs/model_comparison.csv")

# ---------- Plots ----------
plt.figure(figsize=(6, 4))
plt.plot(hist["train"], label="train loss"); plt.plot(hist["val"], label="validation loss")
plt.xlabel("epoch"); plt.ylabel("MSE (log units)"); plt.legend(); plt.title("Tuned MLP loss curves")
plt.tight_layout(); plt.savefig("outputs/loss_curves.png", dpi=150); plt.close()

plt.figure(figsize=(6, 4))
vals = trials["value"]
plt.plot(vals, "o-", label="trial RMSE"); plt.plot(vals.cummin(), "r-", label="best so far")
plt.xlabel("trial"); plt.ylabel("validation RMSE"); plt.legend(); plt.title("Optuna convergence")
plt.tight_layout(); plt.savefig("outputs/optuna_convergence.png", dpi=150); plt.close()

res["RMSE"].plot.bar(title="Test RMSE (lower is better)", rot=15)
plt.tight_layout(); plt.savefig("outputs/model_comparison.png", dpi=150); plt.close()
print("\nSaved plots and tables in outputs/")
