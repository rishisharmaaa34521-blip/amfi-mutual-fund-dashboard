from __future__ import annotations
import warnings
import numpy as np
import pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
try:
    from xgboost import XGBRegressor
except Exception: XGBRegressor=None
from .feature_engineering import FEATURES

def _models():
    m={"Linear Regression":make_pipeline(StandardScaler(),LinearRegression()),
       "Random Forest":RandomForestRegressor(n_estimators=400,min_samples_leaf=2,max_features=0.9,random_state=42,n_jobs=-1)}
    if XGBRegressor is not None:
        m["XGBoost"]=XGBRegressor(n_estimators=250,max_depth=2,learning_rate=.03,subsample=.85,colsample_bytree=.9,reg_lambda=5,objective="reg:squarederror",random_state=42,n_jobs=1)
    return m

def train_and_evaluate(data):
    labeled=data.dropna(subset=["target_inflow","target_outflow"]).reset_index(drop=True)
    n=len(labeled); a=int(n*.70); b=int(n*.85)
    if a<24 or n-b<8: raise ValueError("Not enough clean observations for 70/15/15 chronological training/validation/test.")
    X=labeled[FEATURES]; X_latest=data[FEATURES].iloc[[-1]]; results=[]; predictions=[]; fitted={}
    for target, lag in [("target_inflow","current_inflow"),("target_outflow","current_outflow")]:
        y=labeled[target].astype(float)
        candidates={"Naive":None,**_models()}
        val_scores={}
        for name,model in candidates.items():
            if name=="Naive": val_pred=labeled[lag].iloc[a:b].to_numpy()
            else:
                model.fit(X.iloc[:a],y.iloc[:a]); val_pred=model.predict(X.iloc[a:b])
            val_scores[name]=mean_absolute_error(y.iloc[a:b],val_pred)
        winner=min(val_scores,key=val_scores.get)
        for name,model in candidates.items():
            if name=="Naive": pred_test=labeled[lag].iloc[b:].to_numpy()
            else:
                model.fit(X.iloc[:b],y.iloc[:b]); pred_test=model.predict(X.iloc[b:])
            truth=y.iloc[b:].to_numpy()
            results.append({"Model":name,"Target":target.replace("target_",""),"MAE":mean_absolute_error(truth,pred_test),"RMSE":mean_squared_error(truth,pred_test)**.5,"R2":r2_score(truth,pred_test),"Validation_MAE":val_scores[name],"Selected":name==winner})
            if name==winner:
                fitted[target]=(name,model)
                # refit selected model on all available labeled records for current next-month estimate
                if model is not None: model.fit(X,y)
                last_pred=float(data[lag].iloc[-1]) if model is None else float(model.predict(X_latest)[0])
                fitted[target+"_latest"]=last_pred
                test_pred=labeled[lag].iloc[b:].to_numpy() if model is None else model.predict(X.iloc[b:])
                for i,(actual,pred) in enumerate(zip(truth,test_pred)):
                    predictions.append({"target_month":labeled.target_month.iloc[b+i],"target":target.replace("target_",""),"actual":actual,"predicted":float(pred),"model":name})
    return pd.DataFrame(results),pd.DataFrame(predictions),fitted,b

def walk_forward(data,target="target_outflow",min_train=48):
    y=data[target].astype(float); out=[]
    for i in range(max(min_train,1),len(data)):
        model=RandomForestRegressor(n_estimators=250,min_samples_leaf=2,random_state=42,n_jobs=-1)
        model.fit(data[FEATURES].iloc[:i],y.iloc[:i]); p=float(model.predict(data[FEATURES].iloc[[i]])[0])
        out.append({"target_month":data.target_month.iloc[i],"actual":y.iloc[i],"predicted":p})
    return pd.DataFrame(out)
