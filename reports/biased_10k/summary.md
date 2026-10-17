# Dataset Report: biased (10000 samples)

## Overview
- **Scenario**: biased
- **Size**: 10000
- **Overall Mean Score**: 0.5198

## Fairness & Diversity Metrics
| Metric | Gender | Race |
|---|---|---|
| Demographic Parity (Max Mean Diff) | 0.2592 | 0.2454 |
| Disparate Impact Ratio (Score > Mean) | 0.2490 | 0.2499 |
| Shannon Entropy (Diversity) | 0.8222 | 1.1787 |

## Descriptive Statistics by Group

### Gender
| gender | mean | std | min | 50% | max |
| --- | --- | --- | --- | --- | --- |
| Feminino | 0.4037 | 0.1750 | 0.0000 | 0.4064 | 1.0000 |
| Masculino | 0.6032 | 0.1746 | 0.0000 | 0.6097 | 1.0000 |
| Não-binário | 0.3440 | 0.1701 | 0.0000 | 0.3434 | 0.7927 |

### Race
| race | mean | std | min | 50% | max |
| --- | --- | --- | --- | --- | --- |
| Amarela | 0.4081 | 0.1695 | 0.0000 | 0.4120 | 0.8524 |
| Branca | 0.6026 | 0.1731 | 0.0470 | 0.6090 | 1.0000 |
| Indígena | 0.4436 | 0.1738 | 0.0000 | 0.4383 | 0.8765 |
| Parda | 0.3973 | 0.1731 | 0.0000 | 0.3980 | 0.9129 |
| Preta | 0.3573 | 0.1721 | 0.0000 | 0.3645 | 0.9264 |

## Visualizations

### 1. Demographic Distributions
![Demographic Distribution](plots/demographic_dist.png)

### 2. Continuous Feature Distributions
![Continuous Distributions](plots/continuous_dist.png)

### 3. Score Distribution by Demographic Group (Violin Plots)
![Score Violin Plots](plots/score_violin_plots.png)

### 4. Correlation Matrix
![Correlation Heatmap](plots/correlation_heatmap.png)

