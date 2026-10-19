import argparse
from pathlib import Path
from src.data_collection import collect
from src.feature_engineering import build_features,ROOT
from src.evaluation import run

def main():
    parser=argparse.ArgumentParser(description="Collect verified AMFI reports and run the forecasting workflow")
    parser.add_argument("--collect",action="store_true",help="Fetch and validate the AMFI monthly archive")
    args=parser.parse_args()
    if args.collect: collect()
    source=ROOT/"data/processed/monthly_flows.csv"
    if not source.exists(): raise SystemExit("No verified source data. Run with --collect; no demo data are supplied.")
    matrix=build_features(source)
    metrics,pred,latest=run(matrix)
    print(f"Completed with {latest['observations']} usable months; forecast month {latest['forecast_month']}.")
    print(metrics.to_string(index=False))

if __name__=="__main__": main()
