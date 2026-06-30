import argparse
import os
import logging
import sys
from pathlib import Path

# Add the directory containing this script to sys.path to enable local imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import load_config
from seed import set_seed
from controlled_generator import ControlledGenerator

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def main():
    parser = argparse.ArgumentParser(description="Generate synthetic e-recruitment datasets.")
    parser.add_argument("--config", type=str, default="scripts/preprocessing/data_config.yaml",
                        help="Path to data config.")
    parser.add_argument("--out_dir", type=str, default="data/final",
                        help="Output directory for datasets.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed.")
    
    args = parser.parse_args()
    set_seed(args.seed)
    
    os.makedirs(args.out_dir, exist_ok=True)
    
    config = load_config(args.config)
    
    dataset_cfg = config.get("dataset", {})
    sizes = dataset_cfg.get("sizes", [1000, 5000, 10000])
    scenarios = dataset_cfg.get("scenarios", ["biased", "debiased", "extreme_bias"])
    
    logging.info(f"Will generate datasets for scenarios: {scenarios} and sizes: {sizes}")
    
    generator = ControlledGenerator(config)
    
    for scenario in scenarios:
        for size in sizes:
            logging.info(f"Generating -> Scenario: {scenario}, Size: {size}")
            df = generator.generate(n_samples=size, mode=scenario)
            
            file_name = f"{scenario}_{size // 1000}k.csv"
            out_path = Path(args.out_dir) / file_name
            df.to_csv(out_path, index=False)
            
            logging.info(f"Saved to {out_path}.")

    logging.info("All datasets generated successfully.")

if __name__ == "__main__":
    main()
