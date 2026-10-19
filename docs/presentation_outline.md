# 12-slide presentation outline

1. **Project Title** — AI-Based Mutual Fund Flow Forecasting and Liquidity Early-Warning System; student/program details.
2. **The Problem** — subscriptions and redemptions are uncertain; monthly aggregate flow is only a pressure indicator.
3. **Why Forecasting Matters** — monitoring demand, redemption patterns and liquidity planning.
4. **Data & Variables** — AMFI reports; open-ended equity-oriented aggregate; monthly flow and AUM; show coverage after collection.
5. **ML Methodology** — lagged predictors, separate targets, chronological split, persistence/linear/RF/XGBoost.
6. **Model Performance** — XGBoost selected for both targets by validation MAE; test R²: inflow −0.35 and outflow −0.29. Explain the limits of these scores.
7. **What Will Happen? — Forecast** — October 2026: inflow ₹72,519 Cr, outflow ₹36,422 Cr, net flow +₹36,097 Cr.
8. **Why? — Explainable AI** — trailing inflow history leads the latest inflow estimate; current outflow leads the outflow estimate. SHAP is model contribution, not causality.
9. **Liquidity Stress Testing** — 25%/50% outflow stress imply ₹45,527/₹54,632 Cr outflows. Compare with a user-entered illustrative buffer.
10. **Liquidity Early-Warning System** — transparent project classification and scenario result.
11. **Management Implications** — monitoring actions conditional on risk band; not official risk rating/advice.
12. **Conclusion** — evidence, limits, next steps; avoid certainty claims.

Keep slides visual. All values above are generated from the collected AMFI sample and trained models; refresh them after rerunning the pipeline. Never present the buffer or stress multipliers as official regulatory values.
