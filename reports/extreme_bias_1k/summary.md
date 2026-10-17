# Dataset Report: extreme_bias (1000 samples)

## Overview
- **Scenario**: extreme_bias
- **Size**: 1000
- **Overall Mean Score**: 0.5587

## Fairness & Diversity Metrics
| Metric | Gender | Race |
|---|---|---|
| Demographic Parity (Max Mean Diff) | 0.4775 | 0.4425 |
| Disparate Impact Ratio (Score > Mean) | 0.1046 | 0.1676 |
| Shannon Entropy (Diversity) | 0.8594 | 1.1872 |

## Descriptive Statistics by Group

### Gender
| gender | mean | std | min | 50% | max |
| --- | --- | --- | --- | --- | --- |
| Feminino | 0.3528 | 0.2328 | 0.0000 | 0.3785 | 0.8988 |
| Masculino | 0.7149 | 0.2450 | 0.0731 | 0.7581 | 1.0000 |
| Não-binário | 0.2374 | 0.2275 | 0.0000 | 0.2102 | 0.8037 |

### Race
| race | mean | std | min | 50% | max |
| --- | --- | --- | --- | --- | --- |
| Amarela | 0.3492 | 0.2476 | 0.0000 | 0.4038 | 0.8584 |
| Branca | 0.7135 | 0.2390 | 0.0000 | 0.7430 | 1.0000 |
| Indígena | 0.4236 | 0.2212 | 0.0000 | 0.3918 | 0.7734 |
| Parda | 0.3194 | 0.2388 | 0.0000 | 0.2986 | 0.8188 |
| Preta | 0.2711 | 0.2171 | 0.0000 | 0.2626 | 0.8226 |

## Visualizations

### 1. Demographic Distributions
![Demographic Distribution](plots/demographic_dist.png)

### 2. Continuous Feature Distributions
![Continuous Distributions](plots/continuous_dist.png)

### 3. Score Distribution by Demographic Group (Violin Plots)
![Score Violin Plots](plots/score_violin_plots.png)

### 4. Correlation Matrix
![Correlation Heatmap](plots/correlation_heatmap.png)

