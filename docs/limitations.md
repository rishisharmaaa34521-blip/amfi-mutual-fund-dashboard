# Limitations

1. Results depend on retrieval and successful parsing of AMFI's historical monthly files; no data are fabricated or substituted.
2. Aggregated category flows cannot establish the liquidity position of any individual fund or its holdings.
3. Flow forecast relationships are predictive associations, not causal effects.
4. The monthly sample is small for flexible ML models. A simpler baseline may outperform and must be retained in the comparison.
5. The archive's workbook structure can change. Collection validates the schema and stops instead of silently scraping a different field.
6. No external market/macro variables are used in the baseline because availability timing and complete source histories have not been established here.
7. Stress multipliers and user buffer are illustrative assumptions. They do not represent an official risk classification or guarantee liquidity.
8. Model performance can change across regimes; periodic monitoring and revalidation are required before operational use.
