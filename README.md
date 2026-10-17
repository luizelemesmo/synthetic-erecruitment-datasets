# Synthetic E-Recruitment Datasets Generator

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Institution](https://img.shields.io/badge/UFOP-DECOM-red.svg)](https://decom.ufop.br/)
[![Conference](https://img.shields.io/badge/SBBD--DSW-2026-green.svg)](https://sbbd.org.br/)

Este repositório provê um **gerador estatístico controlado e artefatos de dados sintéticos para e-recrutamento (Dataset Showcase)**, concebidos especificamente para a pesquisa e avaliação empírica de **justiça algorítmica (*fairness*), diversidade e flexibilidade geográfica** em sistemas de recomendação e ranqueamento de candidatos.

O artefato integra a pesquisa de monografia em Ciência da Computação na **Universidade Federal de Ouro Preto (UFOP)** e foi aceito no **Simpósio Brasileiro de Banco de Dados — Dataset Showcase Workshop (SBBD DSW 2026)**.

---

## 📌 Contexto e Motivação

Sistemas automatizados de recomendação para triagem de currículos enfrentam regulamentações éticas crescentes (como o *EU AI Act* e a *NYC Local Law 144*), mas pesquisadores encontram barreiras severas de acesso a dados reais devido a legislações de proteção à privacidade (LGPD, GDPR). Além disso, dados corporativos reais possuem viés estático, impossibilitando a execução de *stress tests* sob magnitudes controladas de disparidade.

Para mitigar essas limitações, este projeto introduz um ecossistema com **9 partições controladas (3 cenários de viés × 3 escalas de tamanho)** com:
* **Ground Truth Matemático Perfeitamente Conhecido**: Permite saber a adequação técnica pura de cada candidato versus o impacto de penalidades demográficas.
* **Calibração Demográfica para o Brasil**: Proporções e disparidades socioeconômicas calibradas segundo dados da PNAD Contínua / IBGE (gênero e raça).
* **Flexibilidade Geográfica como Dimensão de Justiça**: Representação explícita de localizações (Capitais, Regiões Metropolitanas e Interior) e modalidades de trabalho (Presencial, Híbrido, Remoto).

---

## 🎯 Cenários e Partições

O repositório disponibiliza 9 conjuntos prontos em `data/final/` e pipelines para regeneração paramétrica:

| Cenário | Descrição | Parâmetros de Penalização Demográfica | Ruído ($\sigma$) |
|---|---|---|---|
| **`debiased`** (Justo) | Distribuição demográfica uniforme. O escore depende estritamente das métricas técnicas, sem penalidades de atributos sensíveis. Serve como **Ground Truth**. | $B_{\text{attr}} = 0$ | $\sigma = 0.05$ |
| **`biased`** (Realista) | Distribuição assimétrica espelhando o setor de TI brasileiro, com injeção aditiva de penalidades em grupos minoritários/marginalizados. | Gênero: $-0.10$<br>Raça (Preta/Parda): $-0.10$ a $-0.15$<br>Local (Interior): $-0.05$ | $\sigma = 0.07$ |
| **`extreme_bias`** (Estresse) | Magnificação drástica das penalidades estruturais para avaliar os limites e quebras de algoritmos de mitigação e re-ranking. | Gênero: $-0.25$<br>Raça (Preta/Parda): $-0.20$ a $-0.30$<br>Local (Interior): $-0.15$ | $\sigma = 0.05$ |

### Escalas de Tamanho
* **1k (1.000 amostras)**: Prototipação rápida, pipelines de CI e testes com baixo custo computacional.
* **5k (5.000 amostras)**: Equilíbrio ideal entre estabilidade estatística e tempo de processamento.
* **10k (10.000 amostras)**: Escala para publicações científicas com métricas de paridade demográfica estabilizadas.

---

## 📐 Estrutura das Variáveis

O esquema detalhado dos dados (`data/data_dictionary.csv`) inclui:

### Features Técnicas (Objetivas)
* `years_experience` (float): Anos de experiência profissional (Normal truncada, $\mu=5.0, \sigma=3.0$, intervalo $[0, 20]$).
* `skills` (float): Pontuação quantitativa de habilidades técnicas (Normal truncada, $\mu=50.0, \sigma=15.0$, intervalo $[0, 100]$).
* `education_level` (categórica ordinal): Escolaridade (*Ensino Médio*, *Bacharelado*, *Mestrado*, *Doutorado*), modelando a pirâmide educacional de TI.
* `preferred_work_mode` (categórica nominal): Modalidade preferida (*Presencial*, *Híbrido*, *Remoto*).

### Atributos Sensíveis (Protegidos)
* `gender` (categórica): *Masculino*, *Feminino*, *Não-binário*.
* `race` (categórica): *Branca*, *Preta*, *Parda*, *Amarela*, *Indígena* (alinhado ao padrão IBGE).
* `location` (categórica ordinal): *Capitais*, *Região Metropolitana*, *Interior*.

### Variável-Alvo

`suitability_score` (float $[0, 1]$): Medida da adequação do candidato à vaga. No cenário base, resulta de uma combinação linear normalizada das variáveis técnicas:

```math
S_{\text{base}} = \alpha_1 \frac{\text{exp}}{\max(\text{exp})} + \alpha_2 \frac{\text{skills}}{\max(\text{skills})} + f_{\text{edu}}(\text{education\_level})
```

Nos cenários com viés, incorpora penalidades demográficas aditivas e ruído gaussiano:

```math
\text{suitability\_score} = \text{clip}\left(S_{\text{base}} + B_{\text{gênero}} + B_{\text{raça}} + B_{\text{local}} + \varepsilon,\ 0,\ 1\right)
```

---

## 🛠️ Tecnologias e Dependências

* **Linguagem**: Python 3.8+
* **Manipulação de Dados**: Pandas, NumPy
* **Visualização Científica**: Matplotlib, Seaborn
* **Modelos Adversariais (Baseline)**: PyTorch, Scikit-Learn
* **Configuração e Validação**: PyYAML, Pydantic

---

## 🚀 Instalação e Configuração

### 1. Clonar o Repositório
```bash
git clone https://github.com/luizelemesmo/synthetic-erecruitment-datasets.git
cd synthetic-erecruitment-datasets
```

### 2. Criar e Ativar o Ambiente Virtual
```bash
python3 -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate
```

### 3. Instalar Dependências
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente
```bash
cp .env.example .env
```

---

## ⚙️ Como Executar

### 1. Geração Automatizada dos Datasets
Para gerar as 9 partições e seus respectivos relatórios de avaliação estatística em lote:
```bash
python generate_dataset.py --config configs/data_config.yaml
```

### 2. Análises Comparativas e Testes Estatísticos
Para gerar relatórios comparativos entre cenários, matrizes de correlação, testes de hipótese não paramétricos (Mann-Whitney) e gráficos consolidados:
```bash
python -m src.evaluation.advanced_analysis
```
Os resultados consolidados serão salvos em `reports/comparative/`.

### 3. Scripts de Demonstração e Uso Rápido
Consulte o diretório `examples/` para scripts demonstrativos:
```bash
# Carregar e inspecionar partições
python examples/load_dataset.py

# Comparar estabilidade entre tamanhos de partição (1k vs 5k vs 10k)
python examples/compare_dataset_sizes.py

# Análise básica de métricas de fairness (Paridade Demográfica, Disparate Impact)
python examples/basic_fairness_analysis.py
```

---

## 📁 Estrutura do Repositório

```text
synthetic-erecruitment-datasets/
├── configs/
│   ├── data_config.yaml         # Parâmetros de distribuição, penalidades e sementes
│   └── fairgan_config.yaml      # Hiperparâmetros do baseline gerador FairGAN
├── data/
│   ├── final/                   # Partições geradas em CSV (1k, 5k, 10k x 3 cenários)
│   ├── processed/               # Dados processados intermediários
│   ├── raw/                     # Dados sementes de referência
│   ├── data_dictionary.csv      # Dicionário formal de atributos
│   └── README.md                # Guia detalhado dos dados e uso de fairness
├── docs/
│   ├── data_dictionary.md       # Documentação textual dos campos
│   ├── methodology.md           # Metodologia matemática de síntese
│   └── relatorio_tecnico.md     # Relatório técnico completo de arquitetura
├── examples/                    # Scripts prontos para demonstração e análise rápida
├── notebooks/                   # Notebooks Jupyter para exploração visual interativa
├── reports/
│   ├── {scenario}_{size}/       # Relatório individual de cada partição (summary.md + plots)
│   └── comparative/             # Análises cross-cenário, violins e testes estatísticos
├── src/
│   ├── evaluation/              # Cálculo de fairness, paridade, dispersão e relatórios
│   ├── generators/              # ControlledGenerator, FairGAN e schemas de validação
│   └── utils/                   # Gerenciamento de sementes e carregador de configs
├── .env.example                 # Exemplo de configuração de ambiente
├── .gitignore                   # Regras de exclusão de artefatos temporários
├── generate_dataset.py          # Entrypoint CLI do pipeline de geração
├── LICENSE                      # Licença MIT
├── README.md                    # Este documento
└── requirements.txt             # Dependências do projeto Python
```

---

## 📊 Relatórios e Métricas de Fairness

Para cada partição gerada, o diretório `reports/` inclui tabelas com métricas éticas fundamentais:
* **Demographic Parity Difference**: Diferença máxima entre taxas de seleção de grupos demográficos.
* **Disparate Impact Ratio**: Razão entre probabilidades de pontuação qualificada ($p \ge 0.8$ pela regra dos 4/5).
* **Entropia de Shannon**: Mensuração da diversidade demográfica na distribuição de candidatos.
* **Visualizações**: Gráficos de violino por grupo sensível, heatmaps de correlação e curvas de densidade (KDE).

---

## 👥 Equipe e Autoria

* **Autor / Pesquisador**: **Luiz H. Carvalho** ([luizhenrique910@gmail.com](mailto:luizhenrique910@gmail.com)) — Departamento de Computação, Universidade Federal de Ouro Preto (UFOP).
* **Orientador**: **Prof. Dr. Reinaldo Silva Fortes** — Departamento de Computação, Universidade Federal de Ouro Preto (UFOP).

---

## 📖 Como Citar

Se este dataset ou metodologia for utilizado em sua pesquisa, por favor cite:

```bibtex
@inproceedings{carvalho2026dataset,
  author    = {Luiz H. Carvalho and Reinaldo Silva Fortes},
  title     = {Um dataset sintético multi-cenário para avaliação de fairness em sistemas de recomendação de recrutamento},
  booktitle = {Anais do XLI Simpósio Brasileiro de Banco de Dados — Dataset Showcase Workshop (SBBD DSW)},
  year      = {2026},
  location  = {Brasil},
  publisher = {SBC}
}
```

```bibtex
@monography{carvalho2026monografia,
  author    = {Luiz H. Carvalho},
  title     = {Um Sistema de Recomendação para E-Recrutamento com Foco em Fairness, Diversidade e Flexibilidade Geográfica},
  school    = {Universidade Federal de Ouro Preto (UFOP), Instituto de Ciências Exatas e Biológicas, Departamento de Computação},
  year      = {2026},
  type      = {Trabalho de Conclusão de Curso (Bacharelado em Ciência da Computação)},
  advisor   = {Reinaldo Silva Fortes}
}
```

---

## 📄 Licença

Este projeto está distribuído sob a licença **MIT**. Consulte o arquivo [LICENSE](LICENSE) para obter mais informações.
