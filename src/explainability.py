import pandas as pd
from sklearn.inspection import permutation_importance
from .feature_engineering import FEATURES

def explain(model, X_train, y_train, X_latest, name, out_dir):
    out_dir.mkdir(parents=True,exist_ok=True)
    if model is None: return None, "Persistence baseline selected; no fitted model features to explain."
    if name in {"Random Forest","XGBoost"}:
        try:
            import shap
            explainer=shap.TreeExplainer(model)
            values=explainer.shap_values(X_latest)
            train_values=explainer.shap_values(X_train)
            pd.DataFrame({"feature":FEATURES,"mean_abs_shap":abs(train_values).mean(axis=0)}).sort_values("mean_abs_shap",ascending=False).to_csv(out_dir/"global_shap_importance.csv",index=False)
            import matplotlib
            matplotlib.use("Agg",force=True)
            import matplotlib.pyplot as plt
            shap.summary_plot(train_values,X_train,plot_type="dot",show=False,max_display=10)
            plt.gcf().set_size_inches(10,6); plt.tight_layout(); plt.savefig(out_dir/"shap_summary.png",dpi=160,bbox_inches="tight"); plt.close()
            contribution=pd.DataFrame({"feature":FEATURES,"contribution":values[0]}).assign(abs_contribution=lambda x:x.contribution.abs()).sort_values("abs_contribution",ascending=False)
            contribution.to_csv(out_dir/"latest_shap_contributions.csv",index=False)
            return contribution,"Tree SHAP values describe model contributions, not causes."
        except Exception as exc:
            note=f"SHAP unavailable ({type(exc).__name__}); permutation importance used."
    else: note="Linear model selected; permutation importance used for comparable global diagnostics."
    imp=permutation_importance(model,X_train,y_train,n_repeats=20,random_state=42,scoring="neg_mean_absolute_error")
    frame=pd.DataFrame({"feature":FEATURES,"importance":imp.importances_mean}).sort_values("importance",ascending=False)
    frame.to_csv(out_dir/"permutation_importance.csv",index=False)
    return frame,note
