import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

cust = pd.read_csv("data/customers.csv")
X = StandardScaler().fit_transform(cust)

ks = list(range(2, 11))
inertia, sil = [], []
for k in ks:
    km = KMeans(n_clusters=k, n_init=10, random_state=42).fit(X)
    inertia.append(km.inertia_)
    sil.append(silhouette_score(X, km.labels_))

best_k = ks[sil.index(max(sil))]
print("Silhouette by K:", {k: round(s, 3) for k, s in zip(ks, sil)})
print("Best K by silhouette:", best_k)

km = KMeans(n_clusters=best_k, n_init=10, random_state=42).fit(X)
cust["cluster"] = km.labels_
profile = cust.groupby("cluster").mean().round(2)
profile["size"] = cust["cluster"].value_counts().sort_index()
print(profile)
profile.to_csv("outputs/cluster_profiles.csv")

fig, ax = plt.subplots(2, 2, figsize=(11, 8))
ax[0, 0].plot(ks, inertia, "o-"); ax[0, 0].set_title("Elbow method"); ax[0, 0].set_xlabel("K")
ax[0, 1].plot(ks, sil, "o-"); ax[0, 1].axvline(best_k, color="r", ls="--")
ax[0, 1].set_title("Silhouette score"); ax[0, 1].set_xlabel("K")
profile["size"].plot.bar(ax=ax[1, 0], title="Customers per cluster")
ax[1, 1].scatter(cust["avg_spend"], cust["txns_per_month"], c=cust["cluster"], s=6, cmap="tab10")
ax[1, 1].set_xlabel("avg_spend"); ax[1, 1].set_ylabel("txns_per_month"); ax[1, 1].set_title("Segments")
plt.tight_layout(); plt.savefig("outputs/cluster_dashboard.png", dpi=150)
