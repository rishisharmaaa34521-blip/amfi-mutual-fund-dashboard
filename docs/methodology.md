# Methodology

## Research question

Can past monthly aggregate equity-scheme flows provide useful forecasts of next-month investor subscriptions and redemptions, and can those forecasts inform a transparent monitoring exercise?

## Data and target definition

AMFI's open-ended Growth/Equity Oriented subtotal II is the scope. The outcome series are monthly funds mobilized and repurchase/redemption in INR crore. Net flow is derived as inflow less outflow and reconciled with the published subtotal. Aggregate flows describe subscriptions/redemptions at industry category level and do not reveal security-level sales, fund-specific liquidity buffers or the timing of cash movements within a month. The collected series spans April 2019 to September 2026.

## Features and estimators

Predictors use the current published month's flow, one-month lags and rolling 3/6-month means ending in that month. Separate regressors forecast inflows and outflows. Candidate models are persistence (current month's target), linear regression, random forest, and XGBoost. The best estimator for each target is selected by validation MAE, with test performance disclosed separately. If XGBoost is unavailable, the pipeline reports that explicitly and proceeds with installed estimators.

## Validation

Chronological 70/15/15 split, plus expanding-window one-step walk-forward results. Metrics: MAE, RMSE and R-squared. XGBoost was selected for both targets by validation MAE; held-out test R-squared was negative for both. R-squared can be negative out of sample. MAPE is omitted because flows may be near zero and the measure becomes unstable. Predicted net flow is the difference between the independently predicted inflow and outflow.

## Explainability

Tree SHAP is attempted for the selected tree model; otherwise permutation importance on validation data is used. These are descriptions of model reliance, not causal effects. Individual explanation is reported as model feature contributions only when SHAP is available.

## Liquidity interpretation

Base, moderate and severe scenarios apply configurable outflow multipliers (default 1.00, 1.25 and 1.50). These are illustrative project assumptions, not a prescribed regulatory test. A user-entered buffer is used only as an illustrative comparison; if the input is absent the risk is unassessed. See `docs/liquidity_risk_framework.md` for project classification rules.
