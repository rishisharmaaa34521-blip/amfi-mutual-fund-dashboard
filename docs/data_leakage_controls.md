# Data leakage controls

- Each row represents a published calendar month. Predictors include observed flow through month t, prior-month flow, and trailing 3- and 6-month averages ending at t. Month-end AUM and future values are excluded.
- Targets are next-month inflow and outflow (`shift(-1)`). Forecasts are made from the latest fully observed and published AMFI month.
- Chronological 70%/15%/15% train/validation/test partitions are used; no shuffled split is used. Model selection uses validation MAE. Final scores are calculated on the untouched final chronological test segment.
- Scaling and model fitting occur inside sklearn pipelines fitted only on training observations.
- Walk-forward evaluation refits using earlier months and predicts the next month, never using later observations.
- Market data are omitted in this version, avoiding ambiguous close/publication timing. Any future market inputs need a documented lag based on when each observation was available.
- The forecast month is the next calendar month after the latest fully observed month; it is not represented as realized data.
- Aggregation arithmetic is validated; missing months and duplicate months are flagged. No interpolation is used for targets.
