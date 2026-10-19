# Validation log

Run completed with the collected AMFI archive on 19 October 2026.

- 90 consecutive source months verified (2019-04 through 2026-09); 102 original AMFI Excel files are retained locally, including earlier out-of-scope reports.
- Collection checks the published subtotal and reconciles net flow as inflow minus outflow.
- Feature checks confirmed current-month values, rolling six-month values, one-step target alignment, and a final forecast-origin row without a target.
- Chronological model comparison produced 84 labeled observations, 58 train, 13 validation and 13 test; no random split.
- Eight candidate/target rows generated; XGBoost selected for both targets by validation MAE.
- Held-out prediction file contains 13 test months for each of two targets (26 rows), with separate derived net-flow forecasts.
- SHAP global summaries and latest-prediction contributions generated for both selected tree models.
- Liquidity scenario checks confirmed 25% and 50% outflow multipliers and net-flow arithmetic.
- Streamlit `AppTest` rendered the dashboard with zero exceptions and seven KPI metrics both before and after a liquidity buffer was entered; missing buffer remains unassessed.
- Python source syntax, notebook JSON, source CSV, and the full collection/training/evaluation/output pipeline were checked.

The held-out R² values were negative for all candidates. This is disclosed in the report and dashboard context; the project does not claim strong forecast accuracy.
