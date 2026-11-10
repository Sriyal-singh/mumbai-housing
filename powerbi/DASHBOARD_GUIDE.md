# Power BI dashboard guide (Mumbai Housing)

1. **Get Data -> Text/CSV -> `powerbi_data.csv`** (created by the notebook). Click *Transform Data* and confirm types
   (`area`, `price_lakh`, `price_per_sqft` = decimal; text columns = text).
2. **Add these measures** (Modeling -> New measure):

```DAX
Avg Price (Lakh)   = AVERAGE ( powerbi_data[price_lakh] )
Median Price/SqFt  = MEDIAN ( powerbi_data[price_per_sqft] )
Listings           = COUNTROWS ( powerbi_data )
Avg Area           = AVERAGE ( powerbi_data[area] )
Premium vs City %  = DIVIDE ( [Median Price/SqFt], CALCULATE ( [Median Price/SqFt], ALL ( powerbi_data ) ) ) - 1
```
3. **Page layout (16:9)**
   - Top row: 4 KPI cards -> Listings, Avg Price (Lakh), Median Price/SqFt, Avg Area
   - Left: Bar chart - `locality` x `Median Price/SqFt` (Top N filter = 10)
   - Middle: Clustered column - `bhk` x `Avg Price (Lakh)`
   - Right: Scatter - X `area`, Y `price_lakh`, Legend `region`
   - Bottom: Matrix `locality` x `bhk` with `Median Price/SqFt`, conditional-format background colour
4. **Slicers:** region, bhk, status, age, type.
5. Publish to Power BI Service -> *File -> Embed report -> Publish to web* -> paste link + a screenshot in the README.
