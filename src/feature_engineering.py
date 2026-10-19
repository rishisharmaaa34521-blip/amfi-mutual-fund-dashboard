from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
FEATURES=["current_inflow","current_outflow","current_net_flow","lag_1_inflow","lag_1_outflow","lag_1_net_flow","rolling_3m_inflow","rolling_3m_outflow","rolling_3m_net_flow","rolling_6m_inflow","rolling_6m_outflow","rolling_6m_net_flow"]
def build_features(source=None):
    path=Path(source) if source else ROOT/"data/processed/monthly_flows.csv"
    d=pd.read_csv(path,parse_dates=["month"]).sort_values("month").drop_duplicates("month").set_index("month")
    expected=pd.date_range(d.index.min(),d.index.max(),freq="MS")
    if not d.index.equals(expected): raise ValueError("Monthly dates contain missing months or are not month-start dates; refusing to interpolate.")
    for target in ["equity_inflow","equity_outflow","net_flow"]:
        short=target.removeprefix("equity_") if target!="net_flow" else "net_flow"
        d[f"current_{short}"]=d[target]
        d[f"lag_1_{short}"]=d[target].shift(1)
        for w in (3,6): d[f"rolling_{w}m_{short}"]=d[target].rolling(w).mean()
    d["target_inflow"]=d.equity_inflow.shift(-1); d["target_outflow"]=d.equity_outflow.shift(-1)
    d["target_month"]=d.index.to_period("M").astype(str)
    # Keep the final month as a forecast-origin row; its next-month targets are unknown by design.
    result=d.dropna(subset=FEATURES).reset_index()
    out=ROOT/"data/processed/model_matrix.csv"; out.parent.mkdir(parents=True,exist_ok=True); result.to_csv(out,index=False)
    return result
