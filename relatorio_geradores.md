# Relatório Técnico: Geração de Datasets Sintéticos de E-Recrutamento

Este documento detalha o funcionamento interno dos geradores de dados implementados no projeto. O nosso pipeline baseia-se em duas abordagens distintas para a síntese de dados de candidatos e pontuações de recomendação: um **Gerador Controlado Estatisticamente (Controlled Generator)**, que atua como o principal motor do projeto, e um **Gerador Adversarial (FairGAN Generator)**, oferecido como um baseline experimental.

Abaixo, explicamos detalhadamente a engenharia e a matemática por trás de cada um.

---

## 1. O Gerador Principal: Controlled Generator (`controlled_generator.py`)

O **Controlled Generator** é o núcleo do nosso _Dataset Showcase_. Ele usa uma abordagem top-down (de cima para baixo), onde as distribuições demográficas e as correlações com a variável alvo são rigidamente definidas por matrizes de probabilidade e funções matemáticas. Isso garante alta interpretabilidade e controle absoluto sobre o nível de viés inserido.

O funcionamento deste gerador é dividido nas seguintes etapas:

### A. Geração de Features Objetivas (Não-Sensíveis)
O gerador inicia criando atributos que afetam diretamente o desempenho do candidato, utilizando distribuições estatísticas clássicas:
* **Anos de Experiência (`years_experience`) e Habilidades (`skills`)**: São gerados através de uma Distribuição Normal Gaussiana. Os valores extraídos são clipados (limitados a um mínimo e máximo predefinidos) para evitar dados irreais (ex: anos de experiência negativos).
* **Nível de Educação, Modalidade de Trabalho e Localização**: São gerados de forma categórica utilizando um amostrador multinomial (`np.random.choice`), que seleciona as categorias com base nos pesos estipulados no arquivo YAML de configuração (ex: 60% para Capitais, 30% para Região Metropolitana, 10% para Interior).

### B. Distribuição de Atributos Sensíveis
Os atributos demográficos sensíveis (`gender` e `race`) mudam de acordo com o cenário:
* **Cenário Debiased (Sem Viés)**: Força-se uma distribuição puramente uniforme (igualitária). Assim, todos os gêneros e raças (Branca, Preta, Parda, Amarela, Indígena) têm a mesma probabilidade de ocorrência.
* **Cenários Biased/Extreme Bias**: As demografias são selecionadas baseando-se em probabilidades desiguais (espelhando assimetrias do mundo real), definidas diretamente nas configurações.

### C. O Cálculo Matemático do `suitability_score`
Esta é a parte mais importante. O "Score de Adequação" simula a avaliação final do algoritmo de RH. 
1. **Score Base (Mérito Puro)**: Inicialmente, constrói-se um score variando de 0 a 1 apenas com características objetivas. Ele é composto ponderando a experiência (até 40%), as habilidades (até 40%) e o nível educacional (até 25%).
2. **A Injeção de Viés (Bias Injection)**: Se o cenário for `biased` ou `extreme_bias`, o gerador atua penalizando ou bonificando candidatos. Um mapeamento predefinido nas configurações injeta valores (positivos ou negativos) baseados na raça, gênero e localidade do candidato. Por exemplo, a injeção artificial pode diminuir o score de minorias em -0.15 pontos ou aumentá-lo em 0.1 para maiorias. No cenário `extreme_bias`, estes deltas são ainda mais agressivos.
3. **Ruído Final**: Para imitar a variância do mundo real e a subjetividade humana/algorítmica, um leve ruído Gaussiano é adicionado antes de limitar a nota final ao teto de `[0, 1]`.

---

## 2. O Gerador Experimental: FairGAN (`fairgan_generator.py`)

Diferente do gerador controlado, o **FairGAN** utiliza *Deep Learning*, especificamente uma *Generative Adversarial Network* (GAN). O objetivo não é aplicar regras manuais predefinidas, mas sim aprender os padrões latentes e correlações de dados já existentes (dados semente) e simular candidatos plausíveis a partir do nada.

### A. A Arquitetura da Rede (PyTorch)
A rede é dividida em dois componentes competindo entre si:
* **Generator (O Falsificador)**: Uma rede neural MLP (*Multi-Layer Perceptron*) que recebe como entrada um vetor de ruído aleatório (espaço latente - `latent_dim = 64`) e cospe os atributos de um "candidato fantasma". Possui duas camadas ocultas de tamanho 128 e 256, utilizando ativações ReLU e *Batch Normalization* para estabilidade do treino. A última camada utiliza uma ativação *Sigmoid*, garantindo que as saídas numéricas estejam na escala de 0 a 1.
* **Discriminator (O Inspetor)**: Outra MLP cujo papel é olhar para candidatos (tanto reais advindos do dataset semente quanto falsos criados pelo Generator) e dizer "este candidato é real (1)" ou "este candidato é falso (0)". Ele usa *LeakyReLU* para permitir o fluxo de gradiente mesmo em valores negativos, culminando em uma saída escalar *Sigmoid*.

### B. Pré-Processamento
Antes da GAN enxergar os dados, o script aplica um `ColumnTransformer` (via Scikit-Learn). As colunas numéricas (experiência, skills, score) são normalizadas (*StandardScaler*) e as colunas categóricas (raça, gênero, localização) são transformadas em arrays binários através de um *One-Hot Encoding*.

### C. Fluxo de Treinamento Adversarial
O treinamento (`fit`) segue o clássico jogo *Min-Max* das GANs:
1. **Fase do Discriminador**: Ele é treinado em dois lotes. Primeiro, consome amostras reais e tenta prever um vetor de '1's. Em seguida, consome amostras sintéticas do Gerador e tenta prever '0's. Seu erro global (Loss) é minimizado via Entropia Cruzada Binária (BCE).
2. **Fase do Gerador**: Agora é o Gerador que é treinado. Ele gera novos dados falsos, passa pelo Discriminador e calcula o Loss de Entropia Cruzada tendo como rótulo alvo o valor '1'. Ou seja, os pesos do Gerador são ajustados matematicamente exatamente na direção contrária que facilite a rede a "enganar" o Discriminador no futuro.

### D. Geração (Inverse Transform)
Na hora de criar o dataset efetivamente (`generate`), nós simplesmente congelamos os pesos (`eval()`), extraímos novas matrizes de vetores aleatórios de ruído e passamos pelo Generator treinado. 
Como os dados saem da rede normalizados e em forma de One-Hot Encoding, o gerador conta com um passo final de *Inverse Transform* (via Scikit-Learn) para trazer os numéricos de volta à sua escala natural e re-categorizar as arrays binárias em strings (ex: "Capitais", "Preta", "Masculino").

---

## 3. Considerações e Comparativo

* **Interpretabilidade**: O *Controlled Generator* ganha aqui. O projeto acadêmico focado em *Fairness* exige que saibamos *exatamente* quanto de viés foi injetado (ex: -0.15 pontos para a raça X). No FairGAN, o viés emerge naturalmente da base de dados e de instabilidades da rede, o que dificulta o rastreamento linear de causa e efeito.
* **Realismo Holístico**: O *FairGAN* pode aprender interações cruzadas complexas (ex: como uma interseção muito específica entre localização e educação afeta o score na vida real), algo que exigiria milhares de regras condicionais (if-else) no gerador manual para replicar com perfeição.

Ambos os artefatos se complementam dentro da infraestrutura, servindo propósitos complementares para avaliação de métodos de recrutamento algorítmico.
