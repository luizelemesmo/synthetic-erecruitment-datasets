import pandas as pd
from pathlib import Path

def main():
    dataset_path = Path("data/final/biased_1k.csv")
    
    if not dataset_path.exists():
        print(f"Dataset not found at {dataset_path}. Did you run generate_dataset.py?")
        return

    print(f"Loading {dataset_path}...")
    df = pd.read_csv(dataset_path)
    
    print("\nDataset Info:")
    df.info()
    
    print("\nFirst 5 rows:")
    print(df.head())
    
    print("\nSummary Statistics:")
    print(df.describe())

if __name__ == "__main__":
    main()
