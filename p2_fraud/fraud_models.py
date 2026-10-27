import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (roc_auc_score, average_precision_score,
                             precision_score, recall_score, f1_score)

df = pd.read_csv("data/transactions.csv")
X, y = df.drop(columns="is_fraud"), df["is_fraud"]
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25, stratify=y, random_state=42)

models = {
    "Decision Tree (depth 4)": DecisionTreeClassifier(
        max_depth=4, class_weight="balanced", random_state=42),
    "Random Forest (300 trees)": RandomForestClassifier(
        n_estimators=300, max_depth=12, min_samples_leaf=5,
        class_weight="balanced_subsample", n_jobs=-1, random_state=42),
}

rows = {}
for name, m in models.items():
    m.fit(X_tr, y_tr)
    p = m.predict_proba(X_te)[:, 1]
    yhat = (p >= 0.5).astype(int)
    rows[name] = {
        "ROC-AUC": roc_auc_score(y_te, p),
        "PR-AUC": average_precision_score(y_te, p),
        "Precision": precision_score(y_te, yhat, zero_division=0),
        "Recall": recall_score(y_te, yhat),
        "F1": f1_score(y_te, yhat),
    }

comp = pd.DataFrame(rows).T.round(3)
print(comp)
comp.to_csv("outputs/comparison_matrix.csv")

rules = export_text(models["Decision Tree (depth 4)"], feature_names=list(X.columns))
open("outputs/decision_tree_rules.txt", "w").write(rules)
print("\n", rules)

rf = models["Random Forest (300 trees)"]
imp = pd.Series(rf.feature_importances_, index=X.columns).sort_values()
imp.plot.barh(title="Random Forest feature importance")
plt.tight_layout(); plt.savefig("outputs/rf_feature_importance.png", dpi=150); plt.close()
