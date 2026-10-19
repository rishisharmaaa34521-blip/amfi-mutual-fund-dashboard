# Academic Research Report — Project Draft

## Chapter 1 — Introduction

Open-ended equity mutual funds face uncertainty in subscriptions and redemptions. This study develops a monthly industry-level forecasting and monitoring prototype using published AMFI category data. The objective is a decision-support signal, not a claim that monthly net flow alone measures fund liquidity.

## Chapter 2 — Industry and Financial Context

AMFI reports monthly mobilization, redemption, net flow and net assets by scheme category. Equity-oriented schemes hold assets subject to market liquidity, but aggregate flow reports do not reveal individual portfolio holdings, cash balances, settlement timing or liquidity management actions. Therefore, the project forecasts industry flow pressure and uses an explicitly user-supplied illustrative buffer for scenarios.

## Chapter 3 — Literature Review

Forecasting research emphasizes empirical comparison with simple benchmarks and chronological out-of-sample evaluation. Bergmeir, Hyndman and Koo (2018) discuss when cross-validation can be appropriate for autoregressive prediction, while this project uses a conservative chronological holdout and expanding-window checks. The M4 forecasting competition documents that performance varies across series and methods, which supports comparing models rather than assuming a complex estimator will win. Lundberg and Lee (2017) frame SHAP as additive feature attribution for model predictions; here it is used to explain the fitted XGBoost output, not to infer causes. The literature supports these methods, but does not directly establish predictability of AMFI equity flows. See `docs/references.md`.

## Chapter 4 — Data and Methodology

The study uses AMFI monthly reports for its open-ended Growth/Equity Oriented subtotal II, with monthly funds mobilized and repurchase/redemption in INR crore. The collection workflow retains source workbooks, validates the published subtotal and reconciles net flow. Inputs include current-month and lagged flows plus trailing means ending in the forecast origin month. Separate inflow and outflow models are trained using chronological 70/15/15 splits. See `docs/data_sources.md`, `docs/methodology.md` and `docs/data_leakage_controls.md`.

## Chapter 5 — Exploratory Analysis

The collected sample contains 90 consecutive observations from April 2019 through September 2026. Mean monthly inflow was ₹41,674 crore and mean outflow was ₹25,015 crore; mean net flow was ₹16,659 crore and median net flow ₹15,517 crore. Net flows were negative in 8 of 90 months. Month-end AUM grew from ₹578,508 crore to ₹3,754,275 crore over the sample. These are industry aggregate statistics; AUM is not liquid assets. Figures and detailed descriptive statistics are under `outputs/figures/` and `outputs/tables/summary_statistics.csv`.

## Chapter 6 — ML Model Development

Compare persistence, linear regression, random forest and XGBoost. Models are separate for inflow and outflow; net flow is calculated as forecast inflow less forecast outflow. There are 84 labeled observations after feature warm-up, divided chronologically into 58 training, 13 validation and 13 test records. Validation MAE selects the estimator for each target.

## Chapter 7 — Model Results

XGBoost was selected for both targets by validation MAE. On the held-out test segment, inflow MAE was ₹6,198 crore, RMSE ₹7,332 crore and R² −0.35. Outflow MAE was ₹3,865 crore, RMSE ₹4,487 crore and R² −0.29. All candidate models had negative test R², indicating weak fit against a test-mean benchmark; results require caution and do not support a high-accuracy claim. Full metrics are in `outputs/tables/model_comparison.csv`.

## Chapter 8 — Explainable AI

XGBoost is the selected model for both targets, and Tree SHAP ran successfully. For the latest inflow estimate, the largest positive local contributions were trailing six-month inflow (about ₹10,756 crore), trailing three-month inflow (₹4,706 crore), and current-month inflow (₹4,076 crore). For outflow, the leading contributions were current-month outflow (₹6,069 crore), trailing six-month inflow (₹2,036 crore), and trailing three-month outflow (₹1,303 crore). These are local model contributions relative to the model base value, not causal drivers. Global and local results are in `outputs/tables/explain_inflow/` and `outputs/tables/explain_outflow/`.

## Chapter 9 — Liquidity Stress Testing

For October 2026, forecast inflow is ₹72,519 crore and outflow ₹36,422 crore, producing forecast net flow +₹36,097 crore. Holding inflow constant, illustrative 25% and 50% outflow increases imply outflows of ₹45,527 crore and ₹54,632 crore and net flows of +₹26,992 crore and +₹17,886 crore. The dashboard compares these with a user-entered buffer. AMFI AUM is not available liquid assets, and these stress multipliers are not a regulatory framework.

## Chapter 10 — Liquidity Management Implications

Discuss monitoring considerations conditional on the project risk label. High indicates that the chosen scenario exceeds the entered buffer; it does not establish an actual crisis. Consider more frequent monitoring, reviewing redemption patterns and assessing less-liquid exposures.

## Chapter 11 — Conclusion

The project generates reproducible next-month estimates and a scenario monitor from aggregate AMFI equity flows. XGBoost was selected by validation MAE, although test R² is negative for both flow targets. The result supports an analytical monitoring demonstration, not a claim of strong predictive skill or fund-level liquidity risk. The limited monthly sample, weak test fit, and industry aggregate scope require independent revalidation before operational use.

## Chapter 12 — Limitations and Future Scope

See `docs/limitations.md`. Potential extensions include audited market/macro inputs with publication-time lags, fund-level holdings and liquid-asset data, uncertainty intervals, regime-aware validation, and an expanded sample after independent source checks.
