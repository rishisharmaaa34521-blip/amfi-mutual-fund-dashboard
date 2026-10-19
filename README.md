# AI-Based Mutual Fund Flow Forecasting and Liquidity Early-Warning System

An academic decision-support prototype using AMFI's monthly industry reports for Growth/Equity Oriented Schemes. The pipeline collects published monthly reports, validates the official open-ended equity subtotal, builds leakage-aware lag features, compares time-ordered models, and serves a Streamlit dashboard.

## Data integrity

No sample observations are bundled or invented. Run `python run_project.py --collect` to fetch reports from the AMFI archive. The collector stores original Excel files in `data/raw/` and writes verified totals to `data/processed/monthly_flows.csv`. The collected history runs from April 2019 through September 2026 with 90 continuous source months. Flow targets are aggregate category totals, not individual-fund cash positions. AMFI's published open-ended equity subtotal fields are used as inflow and outflow.

Market/macro series are excluded from the initial model because this build does not establish an audited, consistently aligned source history for them. This avoids pretending end-of-month market information was available at the forecasting decision time. Future additions must document source timestamps and publication lags.

## Quick start

```bash
python -m venv .venv
# activate the environment, then:
pip install -r requirements.txt
python run_project.py --collect
streamlit run app.py
```

`python run_project.py` trains the models and generates tables/figures/forecast files from existing collected data. `python run_project.py --collect` runs collection, cleaning, features, evaluation and output generation end-to-end. The dashboard requires a trained `outputs/forecasts/latest_forecast.json` and clearly explains when data have not yet been collected.

## Latest generated results

The current run covers 90 consecutive source months (April 2019–September 2026), with 84 labeled observations after rolling-window warm-up. XGBoost was selected by validation MAE for both inflow and outflow. Held-out test R² values were negative for both targets (−0.35 inflow, −0.29 outflow), so treat the estimates as a monitoring prototype with limited test fit. The October 2026 forecast is approximately ₹72,519 Cr inflow, ₹36,422 Cr outflow and +₹36,097 Cr net flow. Rerun the pipeline to refresh these figures when newer AMFI reports become available.

## Scope and interpretation

The forecast is a statistical estimate for next-month aggregate inflows and outflows. It is not a fund-specific liquidity forecast, causal finding, investment recommendation, regulatory risk rating, or guarantee. Stress multipliers are user-configurable illustrative assumptions. A liquidity buffer is entered by the dashboard user because AMFI aggregate AUM does not disclose liquid assets available to meet redemptions.

See `docs/` for sources, methods, leakage controls, limitations and presentation outline. Research notebooks are reproducible guides; the supported executable workflow is in `src/` and `run_project.py`.
