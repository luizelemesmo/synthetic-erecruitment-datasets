import pandas as pd
from pathlib import Path
import time

def compare_loading_time(path_1k: str, path_10k: str):
    if not Path(path_1k).exists() or not Path(path_10k).exists():
        print("Datasets missing. Please run `python generate_dataset.py` first.")
        return

    # Load 1k
    start = time.time()
    df_1k = pd.read_csv(path_1k)
    time_1k = time.time() - start
    
    # Load 10k
    start = time.time()
    df_10k = pd.read_csv(path_10k)
    time_10k = time.time() - start
    
    print(f"Loaded 1k dataset in {time_1k:.4f} seconds.")
    print(f"Loaded 10k dataset in {time_10k:.4f} seconds.")
    print(f"The 10k dataset is {len(df_10k)/len(df_1k)}x larger and took {time_10k/time_1k:.2f}x more time to load.")
    
    print("\nMean Suitability Score (1k vs 10k):")
    print(f"1k Dataset: {df_1k['suitability_score'].mean():.4f}")
    print(f"10k Dataset: {df_10k['suitability_score'].mean():.4f}")

if __name__ == "__main__":
    compare_loading_time("data/final/biased_1k.csv", "data/final/biased_10k.csv")
