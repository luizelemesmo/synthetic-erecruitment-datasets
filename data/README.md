# Datasets Sintéticos de E-Recrutamento

Este diretório contém os datasets sintéticos gerados pelo pipeline. Eles foram projetados para avaliar justiça (fairness), robustez e escalabilidade em sistemas de recomendação de e-recrutamento.

## Variantes do Dataset (Cenários)

1. **`biased`**: Datasets contendo viés estatístico explícito contra certos grupos demográficos. A variável alvo (`suitability_score`) é artificialmente reduzida para grupos marginalizados (ex: Mulheres, candidatos Pretos e Pardos).
2. **`extreme_bias`**: Semelhante ao cenário `biased`, mas a magnitude da penalidade/bônus de viés é significativamente maior, criando uma disparidade extrema projetada para testar os limites dos algoritmos de mitigação de viés (debiasing).
3. **`debiased`**: Datasets onde os atributos sensíveis seguem uma distribuição uniforme, e o `suitability_score` é calculado puramente com base em métricas objetivas (experiência, habilidades, escolaridade) sem qualquer influência demográfica.

## Tamanhos dos Datasets

Cada cenário é gerado em três tamanhos para facilitar a análise de escalabilidade:
- **1k (1.000 amostras)**: Ideal para prototipagem e testes rápidos.
- **5k (5.000 amostras)**: Um tamanho moderado para avaliações padrão.
- **10k (10.000 amostras)**: Para avaliar a robustez e escalabilidade de algoritmos em conjuntos maiores.

## Features e Atributos Sensíveis

Consulte `data_dictionary.csv` para descrições detalhadas das features.
- **Atributos Sensíveis**: `gender` e `race`.
- **Variável Alvo**: `suitability_score`.

### Explicação do Suitability Score
O `suitability_score` (variando de 0 a 1) é um proxy para medir o quanto um candidato se adequa a uma vaga. 
Ele é calculado pela combinação linear de features objetivas:
- `years_experience` (até 40% de peso)
- `skills` (até 40% de peso)
- `education_level` (até 25% de peso)

**Mecanismo de Injeção de Viés**:
Nos cenários com viés (`biased` e `extreme_bias`), uma penalidade ou bônus fixo é adicionado ao score base dependendo do `gender`, `race` e `location` do candidato. Finalmente, um ruído Gaussiano é adicionado ao score, que é então limitado ao intervalo `[0, 1]`.

## Casos de Uso Pretendidos
- Benchmarking de algoritmos de justiça/fairness (ex: Paridade Demográfica, Equalized Odds).
- Teste de escalabilidade de algoritmos de recomendação sensíveis à justiça.
- Pesquisa acadêmica em mitigação de viés algorítmico.
