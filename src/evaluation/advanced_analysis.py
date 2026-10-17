"""
Advanced cross-scenario analysis for synthetic e-recruitment datasets.

Generates comparative plots and statistical summary tables in reports/comparative/.
Run from the project root: python -m src.evaluation.advanced_analysis
"""

import os
import sys
import logging
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy import stats
from typing import Dict

# Ensure project root is on sys.path when running as a module
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.generators.schema import (
    GENDER, RACE, SUITABILITY_SCORE, SKILLS, YEARS_EXPERIENCE,
    EDUCATION_LEVEL, LOCATION,
    GENDERS, RACES, EDUCATION_LEVELS, LOCATIONS,
)
from src.evaluation.report_generator import evaluate_and_report, calculate_shannon_entropy

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DATA_DIR = Path("data/final")
REPORTS_DIR = Path("reports")
COMPARATIVE_DIR = REPORTS_DIR / "comparative"

SCENARIOS = ["biased", "debiased", "extreme_bias"]
SIZES = [1000, 5000, 10000]
SIZE_LABELS = ["1k", "5k", "10k"]

SCENARIO_LABELS = {
    "biased": "Biased",
    "debiased": "Debiased",
    "extreme_bias": "Extreme Bias",
}
SCENARIO_COLORS = {
    "biased": "#e07b54",
    "debiased": "#5b9dbd",
    "extreme_bias": "#c0392b",
}


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_all_datasets() -> Dict[str, pd.DataFrame]:
    datasets = {}
    for scenario in SCENARIOS:
        for size, label in zip(SIZES, SIZE_LABELS):
            key = f"{scenario}_{label}"
            path = DATA_DIR / f"{key}.csv"
            if path.exists():
                datasets[key] = pd.read_csv(path)
    return datasets


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def compute_fairness_metrics(df: pd.DataFrame) -> dict:
    df = df.copy()
    threshold = df[SUITABILITY_SCORE].mean()
    df["selected"] = df[SUITABILITY_SCORE] > threshold

    metrics: dict = {"overall_mean": threshold, "overall_std": df[SUITABILITY_SCORE].std()}

    for attr, attr_name in [(GENDER, "gender"), (RACE, "race")]:
        group_means = df.groupby(attr)[SUITABILITY_SCORE].mean()
        group_stds = df.groupby(attr)[SUITABILITY_SCORE].std()
        group_sr = df.groupby(attr)["selected"].mean()

        dp = group_means.max() - group_means.min()
        di = group_sr.min() / (group_sr.max() + 1e-9)
        counts = df[attr].value_counts(normalize=True)
        entropy = -np.sum(counts * np.log(counts + 1e-9))

        metrics[f"{attr_name}_dp"] = dp
        metrics[f"{attr_name}_di"] = di
        metrics[f"{attr_name}_entropy"] = entropy
        metrics[f"{attr_name}_means"] = group_means.to_dict()
        metrics[f"{attr_name}_stds"] = group_stds.to_dict()
        metrics[f"{attr_name}_sr"] = group_sr.to_dict()

    return metrics


def _cohens_d(a: pd.Series, b: pd.Series) -> float:
    pooled_std = np.sqrt((a.std() ** 2 + b.std() ** 2) / 2)
    return (a.mean() - b.mean()) / (pooled_std + 1e-9)


def _df_to_markdown(df: pd.DataFrame, include_index: bool = True) -> str:
    if include_index:
        cols = [df.index.name or ""] + list(df.columns)
    else:
        cols = list(df.columns)
    header = "| " + " | ".join(str(c) for c in cols) + " |"
    sep = "| " + " | ".join(["---"] * len(cols)) + " |"
    rows = []
    for idx, row in df.iterrows():
        if include_index:
            cells = [str(idx)] + [f"{v:.4f}" if isinstance(v, float) else str(v) for v in row]
        else:
            cells = [f"{v:.4f}" if isinstance(v, float) else str(v) for v in row]
        rows.append("| " + " | ".join(cells) + " |")
    return "\n".join([header, sep] + rows)


# ---------------------------------------------------------------------------
# Plot 1 — KDE overlay: score distribution across scenarios (10k)
# ---------------------------------------------------------------------------

def plot_scenario_score_distributions(datasets: dict, out: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))
    for scenario in SCENARIOS:
        key = f"{scenario}_10k"
        if key not in datasets:
            continue
        datasets[key][SUITABILITY_SCORE].plot.kde(
            ax=ax,
            label=SCENARIO_LABELS[scenario],
            color=SCENARIO_COLORS[scenario],
            linewidth=2.5,
        )
    ax.set_xlabel("Suitability Score", fontsize=13)
    ax.set_ylabel("Density", fontsize=13)
    ax.set_title("Score Distribution Across Scenarios (10 k samples)", fontsize=14)
    ax.legend(fontsize=11)
    ax.set_xlim(0, 1)
    plt.tight_layout()
    plt.savefig(out / "scenario_score_distribution.png", dpi=150, bbox_inches="tight")
    plt.close()


# ---------------------------------------------------------------------------
# Plot 2 — Grouped bar: Demographic Parity and Disparate Impact (10k)
# ---------------------------------------------------------------------------

def plot_fairness_metrics_comparison(all_metrics: dict, out: Path) -> None:
    x = np.arange(len(SCENARIOS))
    width = 0.35

    gender_dp = [all_metrics[f"{s}_10k"]["gender_dp"] for s in SCENARIOS]
    race_dp   = [all_metrics[f"{s}_10k"]["race_dp"]   for s in SCENARIOS]
    gender_di = [all_metrics[f"{s}_10k"]["gender_di"] for s in SCENARIOS]
    race_di   = [all_metrics[f"{s}_10k"]["race_di"]   for s in SCENARIOS]

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    labels = [SCENARIO_LABELS[s] for s in SCENARIOS]

    axes[0].bar(x - width / 2, gender_dp, width, label="Gender", color="#5b9dbd", alpha=0.85)
    axes[0].bar(x + width / 2, race_dp,   width, label="Race",   color="#e07b54", alpha=0.85)
    axes[0].axhline(0.1, color="red",   linestyle="--", linewidth=1.2, label="Bias threshold (0.10)")
    axes[0].set_xticks(x); axes[0].set_xticklabels(labels)
    axes[0].set_title("Demographic Parity Difference (↓ = fairer)", fontsize=13)
    axes[0].set_ylabel("Max Mean Score Difference"); axes[0].legend()

    axes[1].bar(x - width / 2, gender_di, width, label="Gender", color="#5b9dbd", alpha=0.85)
    axes[1].bar(x + width / 2, race_di,   width, label="Race",   color="#e07b54", alpha=0.85)
    axes[1].axhline(0.8, color="green", linestyle="--", linewidth=1.2, label="Legal threshold (0.80)")
    axes[1].set_xticks(x); axes[1].set_xticklabels(labels)
    axes[1].set_title("Disparate Impact Ratio (↑ = fairer)", fontsize=13)
    axes[1].set_ylabel("Min/Max Selection Rate Ratio"); axes[1].legend()

    fig.suptitle("Fairness Metrics Across Scenarios (10 k)", fontsize=14)
    plt.tight_layout()
    plt.savefig(out / "fairness_metrics_comparison.png", dpi=150, bbox_inches="tight")
    plt.close()


# ---------------------------------------------------------------------------
# Plot 3 — Faceted boxplots: score by gender/race for each scenario (10k)
# ---------------------------------------------------------------------------

def plot_boxplot_by_group_all_scenarios(datasets: dict, out: Path) -> None:
    for attr, attr_label, fname in [
        (GENDER, "Gender",         "score_by_gender_all_scenarios.png"),
        (RACE,   "Race/Ethnicity", "score_by_race_all_scenarios.png"),
    ]:
        fig, axes = plt.subplots(1, 3, figsize=(20, 7), sharey=True)
        for i, scenario in enumerate(SCENARIOS):
            key = f"{scenario}_10k"
            if key not in datasets:
                continue
            sns.boxplot(data=datasets[key], x=attr, y=SUITABILITY_SCORE,
                        ax=axes[i], palette="muted")
            axes[i].set_title(SCENARIO_LABELS[scenario], fontsize=13)
            axes[i].set_xlabel(attr_label)
            axes[i].tick_params(axis="x", rotation=30)
            axes[i].set_ylabel("Suitability Score" if i == 0 else "")
        fig.suptitle(f"Suitability Score by {attr_label} — All Scenarios (10 k)",
                     fontsize=14, y=1.02)
        plt.tight_layout()
        plt.savefig(out / fname, dpi=150, bbox_inches="tight")
        plt.close()


# ---------------------------------------------------------------------------
# Plot 4 — Intersectional heatmaps: mean score for gender × race (10k)
# ---------------------------------------------------------------------------

def plot_intersectional_heatmaps(datasets: dict, out: Path) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(22, 5))
    for i, scenario in enumerate(SCENARIOS):
        key = f"{scenario}_10k"
        if key not in datasets:
            continue
        pivot = datasets[key].pivot_table(
            values=SUITABILITY_SCORE, index=GENDER, columns=RACE, aggfunc="mean"
        )
        sns.heatmap(
            pivot, ax=axes[i], annot=True, fmt=".3f",
            cmap="RdYlGn", vmin=0.3, vmax=0.75,
            linewidths=0.5, cbar=(i == 2),
        )
        axes[i].set_title(SCENARIO_LABELS[scenario], fontsize=13)
        axes[i].set_xlabel("Race/Ethnicity")
        axes[i].set_ylabel("Gender" if i == 0 else "")
    fig.suptitle("Intersectional Analysis: Mean Score (Gender × Race, 10 k)", fontsize=14, y=1.02)
    plt.tight_layout()
    plt.savefig(out / "intersectional_heatmaps.png", dpi=150, bbox_inches="tight")
    plt.close()


# ---------------------------------------------------------------------------
# Plot 5 — Effect sizes (Cohen's d) vs. privileged group (10k)
# ---------------------------------------------------------------------------

def plot_bias_effect_sizes(datasets: dict, out: Path) -> None:
    ref_gender, ref_race = "Masculino", "Branca"
    other_genders = [g for g in GENDERS if g != ref_gender]
    other_races   = [r for r in RACES   if r != ref_race]

    width = 0.25
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    for j, scenario in enumerate(SCENARIOS):
        key = f"{scenario}_10k"
        if key not in datasets:
            continue
        df = datasets[key]
        ref_g = df[df[GENDER] == ref_gender][SUITABILITY_SCORE]
        ref_r = df[df[RACE]   == ref_race  ][SUITABILITY_SCORE]

        g_vals = [_cohens_d(ref_g, df[df[GENDER] == g][SUITABILITY_SCORE]) for g in other_genders]
        r_vals = [_cohens_d(ref_r, df[df[RACE]   == r][SUITABILITY_SCORE]) for r in other_races]

        xg = np.arange(len(other_genders))
        xr = np.arange(len(other_races))
        off = (j - 1) * width

        axes[0].bar(xg + off, g_vals, width,
                    label=SCENARIO_LABELS[scenario],
                    color=SCENARIO_COLORS[scenario], alpha=0.85)
        axes[1].bar(xr + off, r_vals, width,
                    label=SCENARIO_LABELS[scenario],
                    color=SCENARIO_COLORS[scenario], alpha=0.85)

    for ax, groups, ref_label, x_label in [
        (axes[0], other_genders, ref_gender, "Gender"),
        (axes[1], other_races,   ref_race,   "Race/Ethnicity"),
    ]:
        ax.set_xticks(np.arange(len(groups)))
        ax.set_xticklabels(groups, rotation=20)
        ax.axhline(0,   color="black", linewidth=0.8)
        ax.axhline(0.8, color="orange", linestyle="--", linewidth=1, alpha=0.7)
        ax.set_title(f"Cohen's d vs. {ref_label} — {x_label}", fontsize=12)
        ax.set_ylabel("Cohen's d (positive = privileged advantage)")
        ax.legend()

    fig.suptitle("Bias Effect Sizes (Privileged vs. Marginalized Groups)", fontsize=14)
    plt.tight_layout()
    plt.savefig(out / "bias_effect_sizes.png", dpi=150, bbox_inches="tight")
    plt.close()


# ---------------------------------------------------------------------------
# Plot 6 — Fairness metric stability across dataset sizes
# ---------------------------------------------------------------------------

def plot_dataset_size_stability(all_metrics: dict, out: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    for scenario in SCENARIOS:
        color = SCENARIO_COLORS[scenario]
        label = SCENARIO_LABELS[scenario]
        gdps = [all_metrics[f"{scenario}_{s}"]["gender_dp"] for s in SIZE_LABELS]
        rdps = [all_metrics[f"{scenario}_{s}"]["race_dp"]   for s in SIZE_LABELS]
        axes[0].plot(SIZE_LABELS, gdps, marker="o", color=color, label=label, linewidth=2)
        axes[1].plot(SIZE_LABELS, rdps, marker="o", color=color, label=label, linewidth=2)

    for ax, title in [
        (axes[0], "Demographic Parity (Gender) vs. Dataset Size"),
        (axes[1], "Demographic Parity (Race) vs. Dataset Size"),
    ]:
        ax.set_title(title, fontsize=13)
        ax.set_xlabel("Dataset Size"); ax.set_ylabel("Max Mean Difference")
        ax.legend(); ax.grid(True, alpha=0.3)

    fig.suptitle("Fairness Metric Stability Across Dataset Sizes", fontsize=14)
    plt.tight_layout()
    plt.savefig(out / "dataset_size_stability.png", dpi=150, bbox_inches="tight")
    plt.close()


# ---------------------------------------------------------------------------
# Plot 7 — Selection rate by education level (10k)
# ---------------------------------------------------------------------------

def plot_education_selection_rate(datasets: dict, out: Path) -> None:
    width = 0.25
    x = np.arange(len(EDUCATION_LEVELS))
    fig, ax = plt.subplots(figsize=(12, 6))

    for j, scenario in enumerate(SCENARIOS):
        key = f"{scenario}_10k"
        if key not in datasets:
            continue
        df = datasets[key].copy()
        df["selected"] = df[SUITABILITY_SCORE] > df[SUITABILITY_SCORE].mean()
        sr = df.groupby(EDUCATION_LEVEL)["selected"].mean()
        vals = [sr.get(edu, 0) for edu in EDUCATION_LEVELS]
        ax.bar(x + (j - 1) * width, vals, width,
               label=SCENARIO_LABELS[scenario],
               color=SCENARIO_COLORS[scenario], alpha=0.85)

    ax.set_xticks(x); ax.set_xticklabels(EDUCATION_LEVELS)
    ax.set_title("Selection Rate by Education Level Across Scenarios (10 k)", fontsize=13)
    ax.set_ylabel("Proportion Selected (score > mean)"); ax.set_ylim(0, 1)
    ax.legend()
    plt.tight_layout()
    plt.savefig(out / "education_selection_rate.png", dpi=150, bbox_inches="tight")
    plt.close()


# ---------------------------------------------------------------------------
# Plot 8 — Violin plots by location (10k)
# ---------------------------------------------------------------------------

def plot_location_score_violins(datasets: dict, out: Path) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(18, 6), sharey=True)
    for i, scenario in enumerate(SCENARIOS):
        key = f"{scenario}_10k"
        if key not in datasets:
            continue
        sns.violinplot(data=datasets[key], x=LOCATION, y=SUITABILITY_SCORE,
                       ax=axes[i], inner="quartile", palette="Set2")
        axes[i].set_title(SCENARIO_LABELS[scenario], fontsize=13)
        axes[i].set_xlabel("Location"); axes[i].tick_params(axis="x", rotation=20)
        axes[i].set_ylabel("Suitability Score" if i == 0 else "")
    fig.suptitle("Suitability Score by Location — All Scenarios (10 k)", fontsize=14, y=1.02)
    plt.tight_layout()
    plt.savefig(out / "location_score_violins.png", dpi=150, bbox_inches="tight")
    plt.close()


# ---------------------------------------------------------------------------
# Plot 9 — Shannon entropy (diversity) by scenario
# ---------------------------------------------------------------------------

def plot_shannon_entropy_comparison(all_metrics: dict, out: Path) -> None:
    x = np.arange(len(SCENARIOS))
    gender_ents = [all_metrics[f"{s}_10k"]["gender_entropy"] for s in SCENARIOS]
    race_ents   = [all_metrics[f"{s}_10k"]["race_entropy"]   for s in SCENARIOS]

    fig, axes = plt.subplots(1, 2, figsize=(13, 6))
    colors = [SCENARIO_COLORS[s] for s in SCENARIOS]
    labels = [SCENARIO_LABELS[s] for s in SCENARIOS]

    for ax, ents, max_ent, title in [
        (axes[0], gender_ents, np.log(3), "Shannon Entropy — Gender"),
        (axes[1], race_ents,   np.log(5), "Shannon Entropy — Race"),
    ]:
        bars = ax.bar(x, ents, color=colors, alpha=0.85)
        ax.axhline(max_ent, color="green", linestyle="--", linewidth=1.5,
                   label="Max entropy (uniform)")
        ax.set_xticks(x); ax.set_xticklabels(labels)
        ax.set_title(title, fontsize=13); ax.set_ylabel("Entropy")
        ax.set_ylim(0, max_ent * 1.2); ax.legend()
        for bar, val in zip(bars, ents):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                    f"{val:.3f}", ha="center", va="bottom", fontsize=10)

    fig.suptitle("Shannon Entropy (Demographic Diversity) by Scenario", fontsize=14)
    plt.tight_layout()
    plt.savefig(out / "shannon_entropy_comparison.png", dpi=150, bbox_inches="tight")
    plt.close()


# ---------------------------------------------------------------------------
# Plot 10 — Heatmap: mean score by scenario × size
# ---------------------------------------------------------------------------

def plot_mean_score_heatmap(all_metrics: dict, out: Path) -> None:
    data = {
        SCENARIO_LABELS[s]: {sz: all_metrics[f"{s}_{sz}"]["overall_mean"]
                              for sz in SIZE_LABELS}
        for s in SCENARIOS
    }
    df = pd.DataFrame(data).T

    fig, ax = plt.subplots(figsize=(8, 4))
    sns.heatmap(df, annot=True, fmt=".4f", cmap="YlOrRd",
                ax=ax, linewidths=0.5, vmin=0.40, vmax=0.65)
    ax.set_title("Mean Suitability Score by Scenario and Dataset Size", fontsize=13)
    ax.set_xlabel("Dataset Size"); ax.set_ylabel("Scenario")
    plt.tight_layout()
    plt.savefig(out / "mean_score_heatmap.png", dpi=150, bbox_inches="tight")
    plt.close()


# ---------------------------------------------------------------------------
# Plot 11 — Grouped bar: mean score by group across scenarios (10k)
# ---------------------------------------------------------------------------

def plot_group_means_comparison(datasets: dict, out: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    colors = [SCENARIO_COLORS[s] for s in SCENARIOS]

    for ax, attr, attr_label in [
        (axes[0], GENDER, "Gender"),
        (axes[1], RACE,   "Race/Ethnicity"),
    ]:
        data = {}
        for scenario in SCENARIOS:
            key = f"{scenario}_10k"
            if key not in datasets:
                continue
            data[SCENARIO_LABELS[scenario]] = (
                datasets[key].groupby(attr)[SUITABILITY_SCORE].mean()
            )
        pd.DataFrame(data).plot(kind="bar", ax=ax, color=colors, alpha=0.85)
        ax.set_title(f"Mean Score by {attr_label} & Scenario (10 k)", fontsize=12)
        ax.set_xlabel(attr_label); ax.set_ylabel("Mean Suitability Score")
        ax.legend(title="Scenario"); ax.tick_params(axis="x", rotation=20)

    plt.tight_layout()
    plt.savefig(out / "group_means_comparison.png", dpi=150, bbox_inches="tight")
    plt.close()


# ---------------------------------------------------------------------------
# Plot 12 — Scatter: skills vs. experience coloured by gender (sample 2k, 10k)
# ---------------------------------------------------------------------------

def plot_skills_vs_experience(datasets: dict, out: Path) -> None:
    gender_palette = {"Masculino": "#4c72b0", "Feminino": "#dd8452", "Não-binário": "#55a868"}
    fig, axes = plt.subplots(1, 3, figsize=(20, 6))

    for i, scenario in enumerate(SCENARIOS):
        key = f"{scenario}_10k"
        if key not in datasets:
            continue
        sample = datasets[key].sample(min(2000, len(datasets[key])), random_state=42)
        for gender, grp in sample.groupby(GENDER):
            axes[i].scatter(grp[YEARS_EXPERIENCE], grp[SKILLS],
                            alpha=0.3, s=12,
                            color=gender_palette.get(gender, "grey"),
                            label=gender)
        axes[i].set_title(SCENARIO_LABELS[scenario], fontsize=13)
        axes[i].set_xlabel("Years of Experience")
        if i == 0:
            axes[i].set_ylabel("Skills Score")
            axes[i].legend(title="Gender", markerscale=3)

    fig.suptitle("Skills vs. Experience by Gender (sample 2 k per scenario)", fontsize=14, y=1.02)
    plt.tight_layout()
    plt.savefig(out / "skills_vs_experience_by_gender.png", dpi=150, bbox_inches="tight")
    plt.close()


# ---------------------------------------------------------------------------
# Table 1 — Master fairness metrics table (all 9 datasets)
# ---------------------------------------------------------------------------

def generate_master_fairness_table(all_metrics: dict, out: Path) -> Path:
    rows = []
    for scenario in SCENARIOS:
        for sz in SIZE_LABELS:
            m = all_metrics[f"{scenario}_{sz}"]
            rows.append({
                "Scenario":       SCENARIO_LABELS[scenario],
                "Size":           sz,
                "Mean Score":     round(m["overall_mean"], 4),
                "Std Score":      round(m["overall_std"],  4),
                "Gender DP":      round(m["gender_dp"],    4),
                "Race DP":        round(m["race_dp"],      4),
                "Gender DI":      round(m["gender_di"],    4),
                "Race DI":        round(m["race_di"],      4),
                "Gender Entropy": round(m["gender_entropy"], 4),
                "Race Entropy":   round(m["race_entropy"],   4),
            })

    df = pd.DataFrame(rows)

    path = out / "master_fairness_table.md"
    with open(path, "w") as f:
        f.write("# Master Fairness Metrics Table\n\n")
        f.write("All 9 generated datasets (3 scenarios × 3 sizes).\n\n")
        f.write("**Metric definitions:**\n")
        f.write("- **DP** — Demographic Parity: max difference in mean scores between groups. Lower = fairer.\n")
        f.write("- **DI** — Disparate Impact Ratio: min/max selection rate. ≥ 0.80 = 4/5ths legal threshold.\n")
        f.write("- **Entropy** — Shannon entropy of demographic distribution. Higher = more diverse.\n\n")
        f.write(_df_to_markdown(df, include_index=False))
        f.write("\n")
    return path


# ---------------------------------------------------------------------------
# Table 2 — Mann-Whitney U test results (10k)
# ---------------------------------------------------------------------------

def generate_statistical_tests_table(datasets: dict, out: Path) -> Path:
    rows = []
    for scenario in SCENARIOS:
        key = f"{scenario}_10k"
        if key not in datasets:
            continue
        df = datasets[key]

        ref_g = df[df[GENDER] == "Masculino"][SUITABILITY_SCORE]
        for g in ["Feminino", "Não-binário"]:
            grp = df[df[GENDER] == g][SUITABILITY_SCORE]
            u, p = stats.mannwhitneyu(ref_g, grp, alternative="greater")
            rows.append({
                "Scenario":   SCENARIO_LABELS[scenario],
                "Attribute":  "Gender",
                "Comparison": f"Masculino vs {g}",
                "U-statistic": int(u),
                "p-value":    f"{p:.2e}",
                "p < 0.05":   "Yes" if p < 0.05 else "No",
            })

        ref_r = df[df[RACE] == "Branca"][SUITABILITY_SCORE]
        for r in ["Preta", "Parda", "Amarela", "Indígena"]:
            grp = df[df[RACE] == r][SUITABILITY_SCORE]
            u, p = stats.mannwhitneyu(ref_r, grp, alternative="greater")
            rows.append({
                "Scenario":   SCENARIO_LABELS[scenario],
                "Attribute":  "Race",
                "Comparison": f"Branca vs {r}",
                "U-statistic": int(u),
                "p-value":    f"{p:.2e}",
                "p < 0.05":   "Yes" if p < 0.05 else "No",
            })

    df_res = pd.DataFrame(rows)
    path = out / "statistical_tests_mannwhitney.md"
    with open(path, "w") as f:
        f.write("# Mann-Whitney U Test Results (Privileged > Marginalized)\n\n")
        f.write("One-sided test on 10 k samples per scenario.\n\n")
        f.write(_df_to_markdown(df_res, include_index=False))
        f.write("\n")
    return path


# ---------------------------------------------------------------------------
# Table 3 — Descriptive stats for all numeric features (10k)
# ---------------------------------------------------------------------------

def generate_descriptive_stats_table(datasets: dict, out: Path) -> Path:
    path = out / "descriptive_statistics.md"
    numeric_cols = [SUITABILITY_SCORE, SKILLS, YEARS_EXPERIENCE]

    with open(path, "w") as f:
        f.write("# Descriptive Statistics — Numeric Features (10 k)\n\n")
        for scenario in SCENARIOS:
            key = f"{scenario}_10k"
            if key not in datasets:
                continue
            desc = datasets[key][numeric_cols].describe().T
            desc.index.name = "Feature"
            f.write(f"## {SCENARIO_LABELS[scenario]}\n\n")
            f.write(_df_to_markdown(desc))
            f.write("\n\n")
    return path


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------

def main() -> None:
    sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)
    os.makedirs(COMPARATIVE_DIR, exist_ok=True)

    log.info("Loading all datasets …")
    datasets = load_all_datasets()
    log.info("Loaded %d datasets: %s", len(datasets), list(datasets.keys()))

    # Regenerate per-dataset reports using updated report_generator
    log.info("Regenerating per-dataset reports …")
    for key, df in datasets.items():
        scenario, size_label = key.rsplit("_", 1)
        size = int(size_label.replace("k", "")) * 1000
        log.info("  %s …", key)
        evaluate_and_report(df, scenario, size, str(REPORTS_DIR))

    # Compute all metrics
    log.info("Computing fairness metrics …")
    all_metrics = {key: compute_fairness_metrics(df) for key, df in datasets.items()}

    # ---- Plots ----
    steps = [
        ("scenario_score_distribution",    lambda: plot_scenario_score_distributions(datasets, COMPARATIVE_DIR)),
        ("fairness_metrics_comparison",     lambda: plot_fairness_metrics_comparison(all_metrics, COMPARATIVE_DIR)),
        ("score_by_group_all_scenarios",    lambda: plot_boxplot_by_group_all_scenarios(datasets, COMPARATIVE_DIR)),
        ("intersectional_heatmaps",         lambda: plot_intersectional_heatmaps(datasets, COMPARATIVE_DIR)),
        ("bias_effect_sizes",               lambda: plot_bias_effect_sizes(datasets, COMPARATIVE_DIR)),
        ("dataset_size_stability",          lambda: plot_dataset_size_stability(all_metrics, COMPARATIVE_DIR)),
        ("education_selection_rate",        lambda: plot_education_selection_rate(datasets, COMPARATIVE_DIR)),
        ("location_score_violins",          lambda: plot_location_score_violins(datasets, COMPARATIVE_DIR)),
        ("shannon_entropy_comparison",      lambda: plot_shannon_entropy_comparison(all_metrics, COMPARATIVE_DIR)),
        ("mean_score_heatmap",              lambda: plot_mean_score_heatmap(all_metrics, COMPARATIVE_DIR)),
        ("group_means_comparison",          lambda: plot_group_means_comparison(datasets, COMPARATIVE_DIR)),
        ("skills_vs_experience_by_gender",  lambda: plot_skills_vs_experience(datasets, COMPARATIVE_DIR)),
    ]

    for i, (name, fn) in enumerate(steps, 1):
        log.info("  [%d/%d] %s …", i, len(steps), name)
        fn()

    # ---- Tables ----
    log.info("Generating summary tables …")
    generate_master_fairness_table(all_metrics, COMPARATIVE_DIR)
    log.info("  master_fairness_table.md")
    generate_statistical_tests_table(datasets, COMPARATIVE_DIR)
    log.info("  statistical_tests_mannwhitney.md")
    generate_descriptive_stats_table(datasets, COMPARATIVE_DIR)
    log.info("  descriptive_statistics.md")

    log.info("All done. Outputs in: %s", COMPARATIVE_DIR)


if __name__ == "__main__":
    main()
