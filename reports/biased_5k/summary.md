# Dataset Report: biased (5000 samples)

## Overview
- **Scenario**: biased
- **Size**: 5000
- **Overall Mean Score**: 0.5206

## Fairness & Diversity Metrics
| Metric | Gender | Race |
|---|---|---|
| Demographic Parity (Max Mean Diff) | 0.2480 | 0.2462 |
| Disparate Impact Ratio (Score > Mean) | 0.2597 | 0.2672 |
| Shannon Entropy (Diversity) | 0.8232 | 1.2000 |

## Descriptive Statistics by Group

### Gender
| gender | mean | std | min | 50% | max |
| --- | --- | --- | --- | --- | --- |
| Feminino | 0.4025 | 0.1770 | 0.0000 | 0.4096 | 0.9340 |
| Masculino | 0.6018 | 0.1783 | 0.0512 | 0.6094 | 1.0000 |
| Não-binário | 0.3537 | 0.1778 | 0.0000 | 0.3430 | 0.8108 |

### Race
| race | mean | std | min | 50% | max |
| --- | --- | --- | --- | --- | --- |
| Amarela | 0.3984 | 0.1695 | 0.0000 | 0.3993 | 0.8675 |
| Branca | 0.6051 | 0.1761 | 0.0000 | 0.6129 | 1.0000 |
| Indígena | 0.4675 | 0.1749 | 0.0000 | 0.4760 | 1.0000 |
| Parda | 0.4072 | 0.1712 | 0.0000 | 0.4147 | 0.9760 |
| Preta | 0.3589 | 0.1775 | 0.0000 | 0.3524 | 0.8467 |

## Visualizations

### 1. Demographic Distributions
![Demographic Distribution](plots/demographic_dist.png)

### 2. Continuous Feature Distributions
![Continuous Distributions](plots/continuous_dist.png)

### 3. Score Distribution by Demographic Group (Violin Plots)
![Score Violin Plots](plots/score_violin_plots.png)

### 4. Correlation Matrix
![Correlation Heatmap](plots/correlation_heatmap.png)

