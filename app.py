from pathlib import Path
import json
import pandas as pd
import plotly.express as px
import streamlit as st
from src.liquidity import scenarios,actions

ROOT=Path(__file__).resolve().parent
st.set_page_config(page_title="Fund Flow & Liquidity Early Warning",page_icon="◈",layout="wide")
st.markdown("<style>.block-container{padding-top:1.8rem}.metric-card{border:1px solid #26364b;border-radius:12px;padding:12px}</style>",unsafe_allow_html=True)
st.title("AI-Powered Mutual Fund Flow & Liquidity Early-Warning Dashboard")
st.caption("Indian open-ended equity-oriented schemes · monthly industry aggregate · INR crore")
forecast_path=ROOT/"outputs/forecasts/latest_forecast.json"; data_path=ROOT/"data/processed/master_dataset.csv"
if not forecast_path.exists() or not data_path.exists():
    st.warning("No verified dataset and trained forecast are available yet. Run `python run_project.py --collect` from the project folder after installing requirements.")
    st.stop()
f=json.loads(forecast_path.read_text()); d=pd.read_csv(data_path,parse_dates=["month"])
st.subheader("Executive summary")
cols=st.columns(4)
for c,label,val in zip(cols,["Current AUM","Latest net flow","Forecast net flow",f"Forecast · {f['forecast_month']}"],[f["current_aum"],f["latest_net_flow"],f["forecast_net_flow"],f["forecast_outflow"]]):
    c.metric(label,f"₹{val:,.0f} Cr")
st.caption(f"Separate models: inflow — {f['inflow_model']}; outflow — {f['outflow_model']}. Forecasts are estimates, not certainty.")
st.sidebar.header("Decision inputs")
lo,hi=d.month.min().date(),d.month.max().date()
dates=st.sidebar.date_input("Historical range",(lo,hi),min_value=lo,max_value=hi)
buffer=st.sidebar.number_input("Illustrative available liquidity buffer (₹ Cr)",min_value=0.0,value=None,step=100.0,placeholder="Enter buffer")
moderate=st.sidebar.slider("Moderate stress increase (%)",0,100,25)
severe=st.sidebar.slider("Severe stress increase (%)",0,200,50)
forecast_target=st.sidebar.selectbox("Forecast target view",["Inflow","Outflow","Net flow"])
stress_view=st.sidebar.selectbox("Stress scenario",["Base","Moderate stress","Severe stress"],index=0)
st.markdown("## What happened? — Historical fund flow analysis")
filtered=d
if isinstance(dates,tuple) and len(dates)==2: filtered=d[(d.month.dt.date>=dates[0])&(d.month.dt.date<=dates[1])]
c1,c2=st.columns(2)
c1.plotly_chart(px.line(filtered,x="month",y=["equity_inflow","equity_outflow"],title="Inflow and outflow (₹ Cr)",labels={"value":"₹ Cr","variable":"Series"}),use_container_width=True)
c2.plotly_chart(px.line(filtered,x="month",y="net_flow",title="Net flow (₹ Cr)"),use_container_width=True)
st.plotly_chart(px.line(filtered,x="month",y="equity_aum",title="Month-end equity-oriented AUM (₹ Cr)"),use_container_width=True)
st.markdown("## What will happen? — Next-month forecast")
fc=st.columns(3)
for c,label,key in zip(fc,["Expected inflow","Expected outflow","Expected net flow"],["forecast_inflow","forecast_outflow","forecast_net_flow"]): c.metric(label,f"₹{f[key]:,.0f} Cr")
st.markdown("### Out-of-sample actual vs predicted")
p=ROOT/"outputs/forecasts/test_actual_vs_predicted.csv"
if p.exists():
    pred=pd.read_csv(p); pred["target_month"]=pd.to_datetime(pred.target_month)
    shown=pred[pred.target==forecast_target.lower().replace(" ","_")] if forecast_target!="Net flow" else None
    if forecast_target!="Net flow":
        st.plotly_chart(px.line(shown,x="target_month",y=["actual","predicted"],title=f"Out-of-sample actual vs predicted {forecast_target.lower()}",labels={"value":"INR crore","variable":"Series"}),use_container_width=True)
    else:
        net=pred.pivot(index="target_month",columns="target",values=["actual","predicted"])
        net["net_actual"]=net[("actual","inflow")]-net[("actual","outflow")]
        net["net_predicted"]=net[("predicted","inflow")]-net[("predicted","outflow")]
        net=net[["net_actual","net_predicted"]].reset_index()
        net.columns=["target_month","actual","predicted"]
        st.plotly_chart(px.line(net,x="target_month",y=["actual","predicted"],title="Out-of-sample actual vs predicted net flow",labels={"value":"INR crore","variable":"Series"}),use_container_width=True)
st.markdown("## Why? — Explainable AI")
st.write("Selected models:",f"inflow **{f['inflow_model']}**; outflow **{f['outflow_model']}**. SHAP/permutation outputs describe model reliance, not causality.")
st.write("**Forecast logic:**",f["inflow_explanation"],f["outflow_explanation"])
st.caption(f.get("tree_candidate_note",""))
for target in ("inflow","outflow"):
    folder=ROOT/"outputs/tables"/f"explain_candidate_xgboost_{target}"
    global_file=folder/"global_shap_importance.csv"
    if not global_file.exists(): global_file=folder/"permutation_importance.csv"
    if global_file.exists():
        is_selected=f.get(target+"_model")=="XGBoost"
        label="selected model" if is_selected else "comparison candidate"
        st.markdown(f"**XGBoost {label} — {target.title()} global drivers**")
        st.dataframe(pd.read_csv(global_file),use_container_width=True,hide_index=True)
        summary_image=folder/"shap_summary.png"
        if summary_image.exists(): st.image(str(summary_image),caption=f"SHAP summary — {target} model")
        local=folder/"latest_shap_contributions.csv"
        if local.exists():
            st.caption("Latest candidate prediction contributions")
            st.dataframe(pd.read_csv(local),use_container_width=True,hide_index=True)
st.markdown("## Liquidity stress testing")
buffer_missing=buffer is None
sc=scenarios(f["forecast_inflow"],f["forecast_outflow"],0 if buffer_missing else buffer,moderate,severe)
if buffer_missing:
    sc["Buffer"]=None; sc["Gap"]=None; sc["Risk"]="UNASSESSED"
money_fmt=lambda x:"—" if pd.isna(x) else f"₹{x:,.0f}"
st.dataframe(sc[["Scenario","Outflow","Net Flow","Liquidity Requirement","Buffer","Gap","Risk"]].style.format({c:money_fmt for c in ["Outflow","Net Flow","Liquidity Requirement","Buffer","Gap"]}),use_container_width=True,hide_index=True)
risk=sc.iloc[-1].Risk
selected_row=sc[sc.Scenario==stress_view].iloc[0]
st.info(f"Selected scenario: {stress_view} · liquidity requirement ₹{selected_row['Liquidity Requirement']:,.0f} Cr · project classification {selected_row.Risk}.")
st.markdown(f"### Project Liquidity Risk Classification Framework: **{risk}**")
st.caption("Project-level illustrative comparison only. Flow pressure is not a liquidity crisis; the buffer is a user input and AMFI category AUM is not liquid-asset data.")
st.markdown("## Fund manager decision support")
if buffer_missing: st.info("Enter an illustrative liquidity buffer to calculate a project risk level and associated monitoring considerations.")
else:
    for action in actions(risk): st.write("• "+action)
st.caption("Analytical monitoring considerations; not personalized investment advice or an official regulatory classification.")
with st.expander("Model comparison and methodology"):
    table=ROOT/"outputs/tables/model_comparison.csv"
    if table.exists():
        comparison=pd.read_csv(table); st.dataframe(comparison,use_container_width=True,hide_index=True)
        existing=sorted(comparison.Model.unique())
        model_view=st.selectbox("Model comparison filter",existing)
        chosen=comparison[comparison.Model==model_view]
        st.plotly_chart(px.bar(chosen,x="Target",y="RMSE",title=f"Held-out RMSE — {model_view}",color="Target"),use_container_width=True)
    st.write("Chronological 70/15/15 split; validation MAE selects models; final metrics are measured on the held-out test segment. Separate inflow and outflow forecasts; net flow is their difference.")
