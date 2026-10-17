# Dataset Report: biased (1000 samples)

## Overview
- **Scenario**: biased
- **Size**: 1000
- **Overall Mean Score**: 0.5289

## Fairness & Diversity Metrics
| Metric | Gender | Race |
|---|---|---|
| Demographic Parity (Max Mean Diff) | 0.2765 | 0.2358 |
| Disparate Impact Ratio (Score > Mean) | 0.1806 | 0.2778 |
| Shannon Entropy (Diversity) | 0.8361 | 1.1248 |

## Descriptive Statistics by Group

### Gender
| gender | mean | std | min | 50% | max |
| --- | --- | --- | --- | --- | --- |
| Feminino | 0.4122 | 0.1771 | 0.0000 | 0.4263 | 0.9008 |
| Masculino | 0.6142 | 0.1777 | 0.0998 | 0.6194 | 1.0000 |
| Não-binário | 0.3378 | 0.1664 | 0.0000 | 0.3674 | 0.6193 |

### Race
| race | mean | std | min | 50% | max |
| --- | --- | --- | --- | --- | --- |
| Amarela | 0.3900 | 0.1956 | 0.0000 | 0.3837 | 0.8315 |
| Branca | 0.6047 | 0.1752 | 0.0802 | 0.6048 | 1.0000 |
| Indígena | 0.4977 | 0.1799 | 0.1403 | 0.4895 | 0.8628 |
| Parda | 0.3688 | 0.1868 | 0.0000 | 0.3760 | 0.8366 |
| Preta | 0.3920 | 0.1749 | 0.0000 | 0.3921 | 0.8956 |

## Visualizations

### 1. Demographic Distributions
![Demographic Distribution](plots/demographic_dist.png)

### 2. Continuous Feature Distributions
![Continuous Distributions](plots/continuous_dist.png)

### 3. Score Distribution by Demographic Group (Violin Plots)
![Score Violin Plots](plots/score_violin_plots.png)

### 4. Correlation Matrix
![Correlation Heatmap](plots/correlation_heatmap.png)

