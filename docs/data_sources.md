# Data sources

## AMFI monthly reports

The Association of Mutual Funds in India (AMFI) publishes monthly reports with funds mobilized, redemptions, net flow and net assets by scheme category. The project uses the official downloadable Excel reports from April 2019 onward at <https://www.amfiindia.com/research-information/amfi-monthly> and retains each downloaded workbook under `data/raw/`. Earlier reports use a different layout and are outside this series.

The target population is AMFI's **open-ended Growth/Equity Oriented Schemes subtotal II**. This published subtotal avoids category taxonomy changes across years. Close-ended and unrelated scheme groups are excluded. The data are industry aggregate in INR crore. `Funds Mobilized` is operationalized as inflow; `Repurchase/Redemption` as outflow; net flow is derived as their difference and reconciled against AMFI's reported subtotal. The collector fails closed if the report layout or subtotal is not identified.

AMFI archive page: [AMFI Monthly](https://www.amfiindia.com/research-information/amfi-monthly). Dataset URLs and field transformations are also recorded in `data/data_sources.csv`.

## Excluded variables

NIFTY, India VIX, FX, gold and macroeconomic variables are not included in this baseline. Their inclusion requires a documented source, stable historical coverage and a defensible information-availability convention. No source series are silently substituted.
