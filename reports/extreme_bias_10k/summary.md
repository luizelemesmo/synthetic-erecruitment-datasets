# Dataset Report: extreme_bias (10000 samples)

## Overview
- **Scenario**: extreme_bias
- **Size**: 10000
- **Overall Mean Score**: 0.5669

## Fairness & Diversity Metrics
| Metric | Gender | Race |
|---|---|---|
| Demographic Parity (Max Mean Diff) | 0.4518 | 0.4497 |
| Disparate Impact Ratio (Score > Mean) | 0.1279 | 0.1454 |
| Shannon Entropy (Diversity) | 0.8190 | 1.2066 |

## Descriptive Statistics by Group

### Gender
| gender | mean | std | min | 50% | max |
| --- | --- | --- | --- | --- | --- |
| Feminino | 0.3478 | 0.2390 | 0.0000 | 0.3732 | 0.9939 |
| Masculino | 0.7180 | 0.2452 | 0.0000 | 0.7682 | 1.0000 |
| Não-binário | 0.2662 | 0.2206 | 0.0000 | 0.2722 | 0.7964 |

### Race
| race | mean | std | min | 50% | max |
| --- | --- | --- | --- | --- | --- |
| Amarela | 0.3686 | 0.2427 | 0.0000 | 0.3918 | 0.9778 |
| Branca | 0.7209 | 0.2400 | 0.0000 | 0.7671 | 1.0000 |
| Indígena | 0.4370 | 0.2577 | 0.0000 | 0.4645 | 0.9573 |
| Parda | 0.3566 | 0.2376 | 0.0000 | 0.3740 | 0.9976 |
| Preta | 0.2712 | 0.2225 | 0.0000 | 0.2683 | 0.9056 |

## Visualizations

### 1. Demographic Distributions
![Demographic Distribution](plots/demographic_dist.png)

### 2. Continuous Feature Distributions
![Continuous Distributions](plots/continuous_dist.png)

### 3. Score Distribution by Demographic Group (Violin Plots)
![Score Violin Plots](plots/score_violin_plots.png)

### 4. Correlation Matrix
![Correlation Heatmap](plots/correlation_heatmap.png)

