import pandas as pd

def scenarios(inflow,outflow,buffer,moderate_pct=25,severe_pct=50):
    rows=[]
    for name,mult in [("Base",1.0),("Moderate stress",1+moderate_pct/100),("Severe stress",1+severe_pct/100)]:
        stressed_out=outflow*mult; net=inflow-stressed_out; gap=stressed_out-buffer
        risk="HIGH" if gap>0 else ("MODERATE" if (stressed_out >= 0.8*buffer or net < 0) else "LOW")
        rows.append({"Scenario":name,"Inflow":inflow,"Outflow":stressed_out,"Net Flow":net,"Liquidity Requirement":stressed_out,"Buffer":buffer,"Gap":gap,"Risk":risk})
    return pd.DataFrame(rows)

def actions(risk):
    return {"LOW":["Maintain normal liquidity monitoring and buffer reviews."],
            "MODERATE":["Increase monitoring frequency.","Review redemption trends, buffer adequacy and portfolio liquidity concentration."],
            "HIGH":["Conduct additional stress testing.","Review the buffer, redemption activity and less-liquid exposures; prepare contingency liquidity measures."]}[risk]
