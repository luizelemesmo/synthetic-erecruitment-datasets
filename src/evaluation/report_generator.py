import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

from src.generators.schema import (
    GENDER, RACE, SUITABILITY_SCORE, SKILLS, YEARS_EXPERIENCE, EDUCATION_LEVEL, LOCATION
)

def _df_to_markdown(df: pd.DataFrame) -> str:
    """Formats a DataFrame as a markdown table without requiring tabulate."""
    cols = [df.index.name or ""] + list(df.columns)
    header = "| " + " | ".join(str(c) for c in cols) + " |"
    sep = "| " + " | ".join(["---"] * len(cols)) + " |"
    rows = []
    for idx, row in df.iterrows():
        cells = [str(idx)] + [f"{v:.4f}" if isinstance(v, float) else str(v) for v in row]
        rows.append("| " + " | ".join(cells) + " |")
    return "\n".join([header, sep] + rows)


def calculate_shannon_entropy(series: pd.Series) -> float:
    """Calculates Shannon Entropy for a categorical series."""
    counts = series.value_counts(normalize=True)
    return -np.sum(counts * np.log(counts + 1e-9))

def evaluate_and_report(df: pd.DataFrame, scenario: str, size: int, report_dir: str):
    """
    Generates advanced statistical reports and plots for a given dataset.
    """
    out_dir = Path(report_dir) / f"{scenario}_{size // 1000}k"
    plots_dir = out_dir / "plots"
    os.makedirs(plots_dir, exist_ok=True)
    
    # Set seaborn style for better aesthetics
    sns.set_theme(style="whitegrid", palette="muted")
    
    # ---------------------------------------------------------
    # 1. Distribution plots (Categorical)
    # ---------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    sns.countplot(data=df, x=GENDER, ax=axes[0])
    axes[0].set_title(f"Gender Distribution ({scenario} - {size}k)")
    
    sns.countplot(data=df, x=RACE, ax=axes[1])
    axes[1].set_title(f"Race Distribution ({scenario} - {size}k)")
    axes[1].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig(plots_dir / "demographic_dist.png")
    plt.close()
    
    # ---------------------------------------------------------
    # 2. Continuous Distributions (Histograms & KDE)
    # ---------------------------------------------------------
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    sns.histplot(data=df, x=SUITABILITY_SCORE, kde=True, ax=axes[0], color="skyblue")
    axes[0].set_title("Suitability Score Distribution")
    
    sns.histplot(data=df, x=SKILLS, kde=True, ax=axes[1], color="salmon")
    axes[1].set_title("Skills Distribution")
    
    sns.histplot(data=df, x=YEARS_EXPERIENCE, kde=True, ax=axes[2], color="lightgreen")
    axes[2].set_title("Years of Experience Distribution")
    
    plt.tight_layout()
    plt.savefig(plots_dir / "continuous_dist.png")
    plt.close()

    # ---------------------------------------------------------
    # 3. Violin Plots (Score Distribution by Group)
    # ---------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    sns.violinplot(data=df, x=GENDER, y=SUITABILITY_SCORE, ax=axes[0], inner="quartile")
    axes[0].set_title("Score Distribution by Gender")
    
    sns.violinplot(data=df, x=RACE, y=SUITABILITY_SCORE, ax=axes[1], inner="quartile")
    axes[1].set_title("Score Distribution by Race")
    axes[1].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig(plots_dir / "score_violin_plots.png")
    plt.close()

    # ---------------------------------------------------------
    # 4. Correlation Heatmap
    # ---------------------------------------------------------
    plt.figure(figsize=(8, 6))
    # Map education to ordinal for correlation
    ed_map = {"Ensino Médio": 1, "Bacharelado": 2, "Mestrado": 3, "Doutorado": 4}
    df_corr = df[[SKILLS, YEARS_EXPERIENCE, SUITABILITY_SCORE]].copy()
    df_corr['Education_Numeric'] = df[EDUCATION_LEVEL].map(ed_map)
    
    corr_matrix = df_corr.corr()
    sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", vmin=-1, vmax=1)
    plt.title(f"Feature Correlation Matrix ({scenario})")
    plt.tight_layout()
    plt.savefig(plots_dir / "correlation_heatmap.png")
    plt.close()

    # ---------------------------------------------------------
    # 5. Statistical and Fairness Metrics Calculations
    # ---------------------------------------------------------
    gender_stats = df.groupby(GENDER)[SUITABILITY_SCORE].describe()
    race_stats = df.groupby(RACE)[SUITABILITY_SCORE].describe()
    
    gender_mean = gender_stats['mean']
    race_mean = race_stats['mean']
    
    # Demographic Parity: max difference in mean scores across groups
    gender_dp = gender_mean.max() - gender_mean.min()
    race_dp = race_mean.max() - race_mean.min()
    
    # Disparate Impact (Ratio of selection rate, assuming threshold > overall mean)
    threshold = df[SUITABILITY_SCORE].mean()
    df['selected'] = df[SUITABILITY_SCORE] > threshold
    
    gender_sr = df.groupby(GENDER)['selected'].mean()
    race_sr = df.groupby(RACE)['selected'].mean()
    
    gender_di = gender_sr.min() / (gender_sr.max() + 1e-9)
    race_di = race_sr.min() / (race_sr.max() + 1e-9)
    
    # Diversity (Shannon Entropy)
    gender_entropy = calculate_shannon_entropy(df[GENDER])
    race_entropy = calculate_shannon_entropy(df[RACE])

    # ---------------------------------------------------------
    # 6. Write summary.md
    # ---------------------------------------------------------
    summary_path = out_dir / "summary.md"
    with open(summary_path, "w") as f:
        f.write(f"# Dataset Report: {scenario} ({size} samples)\n\n")
        f.write("## Overview\n")
        f.write(f"- **Scenario**: {scenario}\n")
        f.write(f"- **Size**: {size}\n")
        f.write(f"- **Overall Mean Score**: {threshold:.4f}\n\n")
        
        f.write("## Fairness & Diversity Metrics\n")
        f.write("| Metric | Gender | Race |\n")
        f.write("|---|---|---|\n")
        f.write(f"| Demographic Parity (Max Mean Diff) | {gender_dp:.4f} | {race_dp:.4f} |\n")
        f.write(f"| Disparate Impact Ratio (Score > Mean) | {gender_di:.4f} | {race_di:.4f} |\n")
        f.write(f"| Shannon Entropy (Diversity) | {gender_entropy:.4f} | {race_entropy:.4f} |\n\n")
        
        f.write("## Descriptive Statistics by Group\n\n")
        
        f.write("### Gender\n")
        f.write(_df_to_markdown(gender_stats[['mean', 'std', 'min', '50%', 'max']]))
        f.write("\n\n")

        f.write("### Race\n")
        f.write(_df_to_markdown(race_stats[['mean', 'std', 'min', '50%', 'max']]))
        f.write("\n\n")
        
        f.write("## Visualizations\n\n")
        f.write("### 1. Demographic Distributions\n")
        f.write("![Demographic Distribution](plots/demographic_dist.png)\n\n")
        
        f.write("### 2. Continuous Feature Distributions\n")
        f.write("![Continuous Distributions](plots/continuous_dist.png)\n\n")
        
        f.write("### 3. Score Distribution by Demographic Group (Violin Plots)\n")
        f.write("![Score Violin Plots](plots/score_violin_plots.png)\n\n")
        
        f.write("### 4. Correlation Matrix\n")
        f.write("![Correlation Heatmap](plots/correlation_heatmap.png)\n\n")
        
    # clean up tmp column
    df.drop(columns=['selected'], inplace=True)
        
    return summary_path
