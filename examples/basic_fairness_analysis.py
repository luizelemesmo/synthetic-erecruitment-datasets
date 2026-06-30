import pandas as pd
from pathlib import Path

def evaluate_fairness(df: pd.DataFrame, sensitive_col: str, target_col: str):
    """
    Computes Demographic Parity (max absolute difference between group mean scores).
    """
    means = df.groupby(sensitive_col)[target_col].mean()
    max_mean = means.max()
    min_mean = means.min()
    dp_diff = max_mean - min_mean
    
    print(f"\n--- Fairness Analysis for {sensitive_col.capitalize()} ---")
    print(f"Group Means:\n{means.to_string()}")
    print(f"\nDemographic Parity Difference: {dp_diff:.4f}")
    
    if dp_diff > 0.1:
        print("Result: High bias detected.")
    elif dp_diff > 0.05:
        print("Result: Moderate bias detected.")
    else:
        print("Result: Low bias / Fair.")

def main():
    paths = [
        "data/final/biased_10k.csv",
        "data/final/debiased_10k.csv",
        "data/final/extreme_bias_10k.csv"
    ]
    
    for p in paths:
        path = Path(p)
        if not path.exists():
            print(f"Skipping {p} (file not found).")
            continue
            
        print(f"\n{'='*40}\nEvaluating Scenario: {path.stem}\n{'='*40}")
        df = pd.read_csv(path)
        evaluate_fairness(df, "gender", "suitability_score")
        evaluate_fairness(df, "race", "suitability_score")

if __name__ == "__main__":
    main()
