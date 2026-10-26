import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.model_selection import GroupShuffleSplit, GroupKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (mean_squared_error, mean_absolute_error,
                             precision_recall_curve, precision_score,
                             recall_score, confusion_matrix)

lines = []
def log(s=""):
    print(s)
    lines.append(s)

# ---------- 1. Load and clean ----------
FEATURES = ["vibration", "temperature", "voltage", "noise"]
df = pd.read_csv("data/telemetry.csv", parse_dates=["timestamp"])
df = df.sort_values(["machine_id", "timestamp"]).reset_index(drop=True)

# fill missing values by interpolating within each machine's own time series
df[FEATURES] = df.groupby("machine_id")[FEATURES].transform(
    lambda s: s.interpolate(limit_direction="both"))

# clip extreme spikes (0.5th - 99.5th percentile)
for c in FEATURES:
    lo, hi = df[c].quantile([0.005, 0.995])
    df[c] = df[c].clip(lo, hi)

# ---------- 2. Split by MACHINE (prevents leakage between train and test) ----------
gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
tr_idx, te_idx = next(gss.split(df, groups=df["machine_id"]))
train, test = df.iloc[tr_idx], df.iloc[te_idx]
log(f"Train rows: {len(train)} | Test rows: {len(test)}")

# ---------- 3. Linear Regression for RUL ----------
def make_reg(degree):
    return Pipeline([
        ("poly", PolynomialFeatures(degree=degree, include_bias=False)),
        ("scale", StandardScaler()),
        ("model", LinearRegression()),
    ])

log("\n=== RUL regression (test set) ===")
best = None
for degree in [1, 2, 3]:
    reg = make_reg(degree).fit(train[FEATURES], train["rul_hours"])
    pred = reg.predict(test[FEATURES])
    rmse = np.sqrt(mean_squared_error(test["rul_hours"], pred))
    mae = mean_absolute_error(test["rul_hours"], pred)
    log(f"degree={degree}  RMSE={rmse:.2f} h  MAE={mae:.2f} h")
    if best is None or rmse < best[0]:
        best = (rmse, degree, pred)

_, best_deg, best_pred = best
log(f"Best polynomial degree: {best_deg}")

plt.figure(figsize=(5, 5))
plt.scatter(test["rul_hours"], best_pred, s=3, alpha=0.3)
lim = [0, test["rul_hours"].max()]
plt.plot(lim, lim, "r--")
plt.xlabel("Actual RUL (h)"); plt.ylabel("Predicted RUL (h)")
plt.title(f"RUL: predicted vs actual (degree {best_deg})")
plt.tight_layout(); plt.savefig("outputs/rul_pred_vs_actual.png", dpi=150); plt.close()

# ---------- 4. Logistic Regression for 24h failure ----------
def make_clf():
    return Pipeline([
        ("poly", PolynomialFeatures(degree=2, include_bias=False)),
        ("scale", StandardScaler()),
        ("model", LogisticRegression(class_weight="balanced", max_iter=2000)),
    ])

X_tr, y_tr = train[FEATURES], train["failure_24h"]
X_te, y_te = test[FEATURES], test["failure_24h"]

# choose the threshold using out-of-fold predictions on TRAIN only (not the test set)
oof = cross_val_predict(make_clf(), X_tr, y_tr, cv=GroupKFold(n_splits=5),
                        groups=train["machine_id"], method="predict_proba")[:, 1]
prec, rec, thr = precision_recall_curve(y_tr, oof)
TARGET_RECALL = 0.90
ok = rec[:-1] >= TARGET_RECALL
chosen = float(thr[ok].max()) if ok.any() else 0.5   # highest threshold that keeps recall >= 90%

clf = make_clf().fit(X_tr, y_tr)
proba = clf.predict_proba(X_te)[:, 1]

log("\n=== Failure classification (test set) ===")
for name, t in [("default 0.50", 0.5), (f"tuned {chosen:.3f}", chosen)]:
    y_hat = (proba >= t).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_te, y_hat).ravel()
    log(f"threshold {name}: recall={recall_score(y_te, y_hat):.3f} "
        f"precision={precision_score(y_te, y_hat):.3f} | TP={tp} FP={fp} FN={fn} TN={tn}")

DOWNTIME_COST = 45_000   # $ per hour of unplanned downtime
log(f"\nMissed failures (FN) at tuned threshold are the expensive errors: "
    f"each one risks ~${DOWNTIME_COST:,}/hour of downtime.")

plt.figure(figsize=(5, 4))
plt.plot(rec[:-1], prec[:-1])
plt.axvline(TARGET_RECALL, color="r", ls="--", label=f"target recall {TARGET_RECALL}")
plt.xlabel("Recall"); plt.ylabel("Precision"); plt.legend()
plt.title("Precision-Recall (cross-validated on train)")
plt.tight_layout(); plt.savefig("outputs/precision_recall_curve.png", dpi=150); plt.close()

# ---------- 5. Save the deliverable report ----------
with open("outputs/threshold_report.txt", "w") as f:
    f.write("\n".join(lines))
json.dump({"best_poly_degree": best_deg, "threshold": chosen},
          open("outputs/config.json", "w"))
print("\nSaved: outputs/threshold_report.txt and 2 plots")
