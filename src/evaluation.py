from pathlib import Path
import json
import pandas as pd
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from .forecasting import train_and_evaluate,walk_forward,XGBRegressor
from .explainability import explain
from .feature_engineering import FEATURES,ROOT

def run(data):
    tables=ROOT/"outputs/tables"; forecasts=ROOT/"outputs/forecasts"; figures=ROOT/"outputs/figures"
    for p in (tables,forecasts,figures): p.mkdir(parents=True,exist_ok=True)
    labeled=data.dropna(subset=["target_inflow","target_outflow"]).reset_index(drop=True)
    metrics,pred,fitted,test_start=train_and_evaluate(data)
    for target in ("inflow","outflow"):
        wf=walk_forward(labeled,"target_"+target)
        if not wf.empty:
            wf["MAE"]=(wf.actual-wf.predicted).abs()
            wf.to_csv(tables/f"walk_forward_{target}.csv",index=False)
    metrics["Rank"]=metrics.groupby("Target")["MAE"].rank(method="min").astype(int)
    metrics.rename(columns={"R2":"R²"}).to_csv(tables/"model_comparison.csv",index=False)
    (ROOT/"models").mkdir(parents=True,exist_ok=True)
    model_meta={}
    for target in ("inflow","outflow"):
        name,model=fitted["target_"+target]
        model_meta[target]={"selected_model":name,"selection_metric":"validation MAE","features":FEATURES}
        if model is not None: joblib.dump(model,ROOT/"models"/f"{target}_model.joblib")
    (ROOT/"models"/"model_metadata.json").write_text(json.dumps(model_meta,indent=2),encoding="utf-8")
    if not pred.empty:
        pivot=pred.pivot(index="target_month",columns="target",values="predicted").reset_index()
        pivot["net_flow"]=pivot.inflow-pivot.outflow
        pivot.to_csv(forecasts/"test_predictions.csv",index=False)
        actual=pred.pivot(index="target_month",columns="target",values="actual").reset_index()
        actual["net_flow"]=actual.inflow-actual.outflow
        net_test=pd.DataFrame({"target_month":pivot.target_month,"actual_net_flow":actual.net_flow,"predicted_net_flow":pivot.net_flow})
        net_test.to_csv(forecasts/"test_net_actual_vs_predicted.csv",index=False)
    pred.to_csv(forecasts/"test_actual_vs_predicted.csv",index=False)
    flow=data.iloc[-1]
    inflow=fitted["target_inflow_latest"]; outflow=fitted["target_outflow_latest"]
    latest={"as_of_month":flow.month.strftime("%Y-%m"),"forecast_month":(flow.month+pd.offsets.MonthBegin(1)).strftime("%Y-%m"),
            "current_aum":float(flow.equity_aum),"latest_inflow":float(flow.equity_inflow),"latest_outflow":float(flow.equity_outflow),"latest_net_flow":float(flow.net_flow),
            "forecast_inflow":inflow,"forecast_outflow":outflow,"forecast_net_flow":inflow-outflow,
            "inflow_model":fitted["target_inflow"][0],"outflow_model":fitted["target_outflow"][0],"observations":len(data)}
    latest["inflow_explanation"]=(f"Persistence baseline: next-month inflow carries forward the latest observed inflow from {latest['as_of_month']}." if latest["inflow_model"]=="Naive" else "See the model contribution output for the selected inflow estimator.")
    latest["outflow_explanation"]=(f"Persistence baseline: next-month outflow carries forward the latest observed outflow from {latest['as_of_month']}." if latest["outflow_model"]=="Naive" else "See the model contribution output for the selected outflow estimator.")
    (forecasts/"latest_forecast.json").write_text(json.dumps(latest,indent=2),encoding="utf-8")
    for target in ("inflow","outflow"):
        name,model=fitted["target_"+target]
        expl,desc=explain(model,labeled[FEATURES].iloc[:test_start],labeled["target_"+target].iloc[:test_start],data[FEATURES].iloc[[-1]],name,ROOT/"outputs/tables"/f"explain_{target}")
        if name!="Naive": latest[target+"_explanation"]=desc
    # SHAP applies to fitted tree models. If a persistence/linear estimator wins selection,
    # also publish a clearly labeled tree-candidate explanation without implying it drives the forecast.
    if XGBRegressor is not None:
        for target in ("inflow","outflow"):
            candidate=XGBRegressor(n_estimators=250,max_depth=2,learning_rate=.03,subsample=.85,colsample_bytree=.9,reg_lambda=5,objective="reg:squarederror",random_state=42,n_jobs=1)
            candidate.fit(labeled[FEATURES],labeled["target_"+target])
            explain(candidate,labeled[FEATURES],labeled["target_"+target],data[FEATURES].iloc[[-1]],"XGBoost",tables/f"explain_candidate_xgboost_{target}")
    latest["tree_candidate_note"]="SHAP summaries describe the fitted XGBoost model. They explain the dashboard forecast only when XGBoost is the validation-selected estimator; otherwise they describe a comparison candidate. SHAP values are model contributions, not causal effects."
    (forecasts/"latest_forecast.json").write_text(json.dumps(latest,indent=2),encoding="utf-8")
    data.to_csv(ROOT/"data/processed/master_dataset.csv",index=False)
    source=pd.read_csv(ROOT/"data/processed/monthly_flows.csv",parse_dates=["month"])
    source.set_index("month")[["equity_inflow","equity_outflow","net_flow","equity_aum"]].describe().T.assign(
        median=source.set_index("month")[["equity_inflow","equity_outflow","net_flow","equity_aum"]].median(),
        skew=source.set_index("month")[["equity_inflow","equity_outflow","net_flow","equity_aum"]].skew(),
        kurtosis=source.set_index("month")[["equity_inflow","equity_outflow","net_flow","equity_aum"]].kurt()).to_csv(tables/"summary_statistics.csv")
    sns.set_theme(style="whitegrid")
    for col,title in [("equity_inflow","Historical equity inflows"),("equity_outflow","Historical equity outflows"),("net_flow","Historical net flow"),("equity_aum","Equity-oriented AUM")]:
        fig,ax=plt.subplots(figsize=(11,4)); ax.plot(source.month,source[col],color="#1b6b73",lw=1.8); ax.set(title=title,xlabel="Month",ylabel="INR crore"); fig.tight_layout(); fig.savefig(figures/f"{col}.png",dpi=160); plt.close(fig)
    fig,ax=plt.subplots(figsize=(7,6)); sns.heatmap(source[["equity_inflow","equity_outflow","net_flow","equity_aum"]].corr(),annot=True,cmap="vlag",center=0,ax=ax); ax.set_title("Correlation matrix — observed series"); fig.tight_layout(); fig.savefig(figures/"correlation_matrix.png",dpi=160); plt.close(fig)
    if not pred.empty:
        fig,axes=plt.subplots(2,1,figsize=(11,8),sharex=True)
        for ax,target in zip(axes,["inflow","outflow"]):
            q=pred[pred.target==target]; ax.plot(q.target_month,q.actual,label="Actual",lw=1.8); ax.plot(q.target_month,q.predicted,label="Predicted",lw=1.6); ax.set_title(f"Out-of-sample {target}"); ax.set_ylabel("INR crore"); ax.legend()
        fig.tight_layout(); fig.savefig(figures/"test_actual_vs_predicted.png",dpi=160); plt.close(fig)
        fig,ax=plt.subplots(figsize=(11,4)); ax.plot(net_test.target_month,net_test.actual_net_flow,label="Actual net flow",lw=1.8); ax.plot(net_test.target_month,net_test.predicted_net_flow,label="Predicted net flow",lw=1.6); ax.set(title="Held-out actual vs predicted net flow",ylabel="INR crore",xlabel="Target month"); ax.legend(); fig.tight_layout(); fig.savefig(figures/"test_net_actual_vs_predicted.png",dpi=160); plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,5)); sns.barplot(data=metrics,x="Model",y="RMSE",hue="Target",ax=ax); ax.set_title("Held-out test RMSE by model and target"); ax.set_ylabel("INR crore"); ax.tick_params(axis="x",rotation=15); fig.tight_layout(); fig.savefig(figures/"model_comparison_rmse.png",dpi=160); plt.close(fig)
    return metrics,pred,latest
