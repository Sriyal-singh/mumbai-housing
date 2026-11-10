"""Synthetic data with the same columns as Kaggle 'Mumbai House Prices' (bhk, type, locality, area,
price, price_unit, region, status, age). Replace data/mumbai_house_prices.csv with the real file."""
import numpy as np, pandas as pd, os

LOCALITIES = {  # locality: (region, typical Rs per sq ft)
    "Worli": ("South Mumbai", 45000), "Dadar": ("Central Mumbai", 33000), "Bandra West": ("Western Suburbs", 42000),
    "Juhu": ("Western Suburbs", 40000), "Andheri West": ("Western Suburbs", 24000), "Andheri East": ("Western Suburbs", 18000),
    "Goregaon East": ("Western Suburbs", 17000), "Malad West": ("Western Suburbs", 16000), "Kandivali East": ("Western Suburbs", 14000),
    "Borivali West": ("Western Suburbs", 15000), "Powai": ("Central Suburbs", 21000), "Chembur": ("Central Suburbs", 20000),
    "Ghatkopar East": ("Central Suburbs", 19000), "Mulund West": ("Central Suburbs", 15500), "Kurla": ("Central Suburbs", 14500),
    "Bhandup West": ("Central Suburbs", 13500), "Thane West": ("Thane", 11000), "Kharghar": ("Navi Mumbai", 8500),
    "Vashi": ("Navi Mumbai", 13000), "Mira Road East": ("Mira Road", 9500)}
BASE = {1: 480, 2: 760, 3: 1100, 4: 1700}

def generate(path="data/mumbai_house_prices.csv", n=6000, seed=7):
    rng = np.random.default_rng(seed)
    locs = list(LOCALITIES)
    rows = []
    for _ in range(n):
        loc = rng.choice(locs); region, ppsf = LOCALITIES[loc]
        bhk = int(rng.choice([1, 2, 3, 4], p=[.28, .45, .22, .05]))
        area = max(250, rng.normal(BASE[bhk], BASE[bhk] * .18))
        status = rng.choice(["Ready to move", "Under construction"], p=[.6, .4])
        age = rng.choice(["New", "Resale", "Unknown"], p=[.45, .45, .1])
        price = area * ppsf * rng.lognormal(0, .12) * (0.95 if age == "Resale" else 1.0)
        if rng.random() < .01: price *= rng.uniform(3, 6)          # planted outliers
        unit = "Cr" if price >= 1e7 else "L"
        value = price / 1e7 if unit == "Cr" else price / 1e5
        rows.append({"bhk": bhk, "type": rng.choice(["Apartment", "Studio Apartment", "Villa", "Penthouse"], p=[.9, .04, .03, .03]),
                     "locality": loc, "area": round(area), "price": round(value, 2), "price_unit": unit,
                     "region": region, "status": status, "age": age})
    df = pd.DataFrame(rows)
    df.loc[rng.choice(n, 40, replace=False), "area"] = np.nan   # missing values
    os.makedirs(os.path.dirname(path), exist_ok=True); df.to_csv(path, index=False)
    return df

if __name__ == "__main__":
    generate(); print("Sample data written.")
