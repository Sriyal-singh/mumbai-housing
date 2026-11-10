# %%
# # Mumbai Housing Price Analysis
# Cleaning, outlier removal, correlation analysis and a baseline price-prediction model.
# Dataset: Kaggle "Mumbai House Prices" -> save as `data/mumbai_house_prices.csv` (synthetic sample used if missing).

# %%
import os
import pandas as pd, numpy as np
import matplotlib.pyplot as plt, seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
sns.set_theme(style="whitegrid")
os.makedirs("images", exist_ok=True)
PATH = "data/mumbai_house_prices.csv"
if not os.path.exists(PATH):
    from generate_data import generate
    generate(PATH)
df = pd.read_csv(PATH)
print(df.shape); df.head()

# %%
# ## 1. Cleaning
# - Convert price to a single unit (Rs) using `price_unit` (L = lakh = 1e5, Cr = crore = 1e7)
# - Drop rows with no area; trim whitespace in text columns; remove duplicates
for c in df.select_dtypes(include=["object", "string"]):
    df[c] = df[c].str.strip()
df = df.drop_duplicates().dropna(subset=["area", "price"]).copy()
df["price_inr"] = df["price"] * df["price_unit"].map({"L": 1e5, "Cr": 1e7})
df["price_lakh"] = df["price_inr"] / 1e5
df["price_per_sqft"] = df["price_inr"] / df["area"]
print(df[["area", "price_lakh", "price_per_sqft"]].describe().round(0))

# %%
# ## 2. Outlier removal (IQR method on price per sq ft, applied per locality)
def iqr_filter(g, col="price_per_sqft", k=1.5):
    q1, q3 = g[col].quantile([.25, .75]); i = q3 - q1
    return g[(g[col] >= q1 - k * i) & (g[col] <= q3 + k * i)]
before = len(df)
clean = df.groupby("locality", group_keys=False)[df.columns.tolist()].apply(iqr_filter)
clean = clean[(clean["area"].between(150, 5000))].copy()
print(f"Removed {before - len(clean)} outliers ({(before - len(clean)) / before:.1%})")
fig, ax = plt.subplots(1, 2, figsize=(11, 4))
sns.boxplot(x=df["price_per_sqft"], ax=ax[0], color="#f4a261").set_title("Before outlier removal")
sns.boxplot(x=clean["price_per_sqft"], ax=ax[1], color="#2a9d8f").set_title("After outlier removal")
plt.tight_layout(); plt.savefig("images/outliers.png", dpi=150); plt.show()
clean.to_csv("cleaned_dataset.csv", index=False)

# %%
# ## 3. Which locality is most expensive?
loc = clean.groupby("locality").agg(listings=("price_lakh", "size"), median_price_lakh=("price_lakh", "median"),
                                    median_ppsf=("price_per_sqft", "median")).sort_values("median_ppsf", ascending=False)
top = loc.head(10).iloc[::-1]
plt.figure(figsize=(9, 5)); plt.barh(top.index, top["median_ppsf"], color="#264653")
plt.title("Top 10 most expensive localities (median Rs / sq ft)"); plt.xlabel("Rs per sq ft")
plt.tight_layout(); plt.savefig("images/expensive_localities.png", dpi=150); plt.show()
loc.head(5)

# %%
# ## 4. BHK vs Price
plt.figure(figsize=(8, 5))
sns.boxplot(data=clean, x="bhk", y="price_lakh", color="#8ecae6"); plt.yscale("log")
plt.title("Price by BHK (log scale)"); plt.ylabel("Price (Rs lakh)")
plt.tight_layout(); plt.savefig("images/bhk_vs_price.png", dpi=150); plt.show()

# %%
# ## 5. Area vs Price
plt.figure(figsize=(8, 5))
sns.scatterplot(data=clean.sample(min(2000, len(clean)), random_state=1), x="area", y="price_lakh", hue="region", alpha=.6)
plt.title("Area vs Price"); plt.xlabel("Area (sq ft)"); plt.ylabel("Price (Rs lakh)")
plt.tight_layout(); plt.savefig("images/area_vs_price.png", dpi=150); plt.show()

# %%
# ## 6. Correlation analysis
corr = clean[["bhk", "area", "price_lakh", "price_per_sqft"]].corr()
plt.figure(figsize=(5.5, 4.5)); sns.heatmap(corr, annot=True, cmap="coolwarm", vmin=-1, vmax=1)
plt.title("Correlation matrix"); plt.tight_layout(); plt.savefig("images/correlation.png", dpi=150); plt.show()

# %%
# ## 7. Best-value localities
# "Value" = cheapest price per sq ft among localities with enough listings, shown with the typical size you get.
value = loc[loc["listings"] >= 30].sort_values("median_ppsf").head(8)
value["typical_area"] = clean.groupby("locality")["area"].median()
print(value.round(0))

# %%
# ## 8. Price prediction (baseline)
X = pd.get_dummies(clean[["bhk", "area", "locality", "status", "age", "type"]], drop_first=True)
y = np.log1p(clean["price_lakh"])
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=.2, random_state=42)
for name, m in {"Linear Regression": LinearRegression(),
                "Random Forest": RandomForestRegressor(200, random_state=42, n_jobs=-1)}.items():
    m.fit(Xtr, ytr); p = m.predict(Xte)
    print(f"{name}: R2 = {r2_score(yte, p):.3f} | MAE = Rs {mean_absolute_error(np.expm1(yte), np.expm1(p)):,.0f} lakh")

# %%
# ## 9. Export for Power BI
clean[["locality", "region", "bhk", "type", "status", "age", "area", "price_lakh", "price_per_sqft"]].to_csv(
    "powerbi/powerbi_data.csv", index=False)
print("Insights:")
print(f"1. Most expensive locality: {loc.index[0]} (median Rs {loc.iloc[0]['median_ppsf']:,.0f}/sq ft)")
print(f"2. Cheapest locality: {loc.index[-1]} (Rs {loc.iloc[-1]['median_ppsf']:,.0f}/sq ft)")
print(f"3. Area-price correlation: {corr.loc['area', 'price_lakh']:.2f}")
print(f"4. Best value (with 30+ listings): {value.index[0]}")
