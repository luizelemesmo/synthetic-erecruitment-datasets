# Master Fairness Metrics Table

All 9 generated datasets (3 scenarios × 3 sizes).

**Metric definitions:**
- **DP** — Demographic Parity: max difference in mean scores between groups. Lower = fairer.
- **DI** — Disparate Impact Ratio: min/max selection rate. ≥ 0.80 = 4/5ths legal threshold.
- **Entropy** — Shannon entropy of demographic distribution. Higher = more diverse.

| Scenario | Size | Mean Score | Std Score | Gender DP | Race DP | Gender DI | Race DI | Gender Entropy | Race Entropy |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Biased | 1k | 0.5416 | 0.2001 | 0.2756 | 0.2146 | 0.1265 | 0.2792 | 0.8361 | 1.1248 |
| Biased | 5k | 0.5352 | 0.2012 | 0.2503 | 0.2462 | 0.2710 | 0.2415 | 0.8232 | 1.2000 |
| Biased | 10k | 0.5337 | 0.1985 | 0.2594 | 0.2454 | 0.2265 | 0.2356 | 0.8222 | 1.1787 |
| Debiased | 1k | 0.4724 | 0.1373 | 0.0108 | 0.0116 | 0.8827 | 0.8368 | 1.0985 | 1.6068 |
| Debiased | 5k | 0.4655 | 0.1347 | 0.0055 | 0.0070 | 0.9490 | 0.9433 | 1.0983 | 1.6083 |
| Debiased | 10k | 0.4637 | 0.1338 | 0.0016 | 0.0046 | 0.9946 | 0.9357 | 1.0986 | 1.6092 |
| Extreme Bias | 1k | 0.5857 | 0.2970 | 0.4720 | 0.4425 | 0.1012 | 0.1276 | 0.8594 | 1.1872 |
| Extreme Bias | 5k | 0.5979 | 0.2964 | 0.4423 | 0.4491 | 0.0844 | 0.0936 | 0.8210 | 1.1967 |
| Extreme Bias | 10k | 0.5949 | 0.2990 | 0.4618 | 0.4497 | 0.1032 | 0.1193 | 0.8190 | 1.2066 |
