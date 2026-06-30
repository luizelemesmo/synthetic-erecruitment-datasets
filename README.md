# Synthetic E-Recruitment Datasets Generator

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)

## 📌 Descrição do Projeto

Este repositório fornece **artefatos prontos para Dataset Showcase** gerados para sistemas de recomendação de recrutamento online (e-recrutamento). O objetivo principal é viabilizar pesquisas sobre justiça algorítmica (fairness), diversidade e robustez, fornecendo distribuições demográficas altamente controladas e injeções explícitas de viés. 

Ideal para pesquisadores e engenheiros de Machine Learning que desejam avaliar a mitigação de viés em algoritmos de ranqueamento e recomendação de candidatos.

## ✨ Funcionalidades

- **Geração Controlada:** Permite a geração top-down via regras estatísticas rigorosas, refletindo ou mitigando vieses explícitos no mercado de trabalho.
- **FairGAN (Opcional):** Um baseline alternativo baseado em Generative Adversarial Networks para síntese de dados baseados na distribuição original.
- **Cenários Variados:** Datasets gerados nos modos `biased`, `debiased` e `extreme_bias`.
- **Escalabilidade:** Geração pronta para volumes diferentes (ex: 1k, 5k, 10k amostras), ideais para testes de estresse em modelos.
- **Relatórios Automatizados:** Geração automática de gráficos e estatísticas comparativas entre os cenários.

## 🛠️ Stack Utilizada

- **Linguagem:** Python 3.8+
- **Processamento de Dados:** Pandas, NumPy
- **Machine Learning / Deep Learning:** Scikit-Learn, PyTorch (para FairGAN)
- **Visualização:** Matplotlib, Seaborn
- **Configuração:** PyYAML

## 🚀 Instalação e Configuração

### Pré-requisitos
- Python 3.8 ou superior
- Pip (gerenciador de pacotes do Python)

### Passo a Passo

1. Clone o repositório:
```bash
git clone https://github.com/usuario/synthetic-erecruitment-datasets.git
cd synthetic-erecruitment-datasets
```

2. Crie um ambiente virtual e ative-o (Recomendado):
```bash
python -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate
```

3. Instale as dependências do projeto:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
```bash
cp .env.example .env
```
*(Ajuste o `.env` conforme a necessidade de caminhos e parâmetros específicos).*

## ⚙️ Como Executar Localmente

### Gerando os Datasets
Para rodar o pipeline completo e gerar todos os datasets em todos os cenários e tamanhos, utilize o ponto de entrada principal:

```bash
python generate_dataset.py --config configs/data_config.yaml
```

Este comando irá:
1. Iterar sobre os tamanhos configurados (ex: 1k, 5k, 10k).
2. Gerar os dados para os três cenários: `biased`, `debiased`, e `extreme_bias`.
3. Salvar os arquivos CSV resultantes na pasta `data/final/`.
4. Gerar relatórios estatísticos e gráficos de distribuição na pasta `reports/`.

### Gerando Análises Avançadas e Comparativas

Para gerar análises cross-cenário, heatmaps interseccionais, testes estatísticos e tabelas-resumo, execute:

```bash
python -m src.evaluation.advanced_analysis
```

Este comando irá (a partir dos datasets já gerados em `data/final/`):
1. Regenerar todos os relatórios per-dataset no formato atualizado.
2. Gerar **12 gráficos comparativos** em `reports/comparative/`.
3. Gerar **3 tabelas markdown** com métricas, testes e estatísticas descritivas.

## 📁 Estrutura do Projeto

```text
project_root/
├── configs/                 # Arquivos de configuração YAML (ex: data_config.yaml)
├── data/                    
│   ├── final/               # Datasets gerados (CSV)
│   ├── raw/                 # Dados originais/semente
│   └── README.md            # Documentação específica dos datasets
├── docs/                    # Documentações adicionais (ex: artigos, paper.tex)
├── examples/                # Exemplos de uso prático dos dados
├── notebooks/               # Notebooks Jupyter para exploração de dados e prototipagem
├── reports/                 # Relatórios estatísticos e gráficos dos datasets gerados
│   ├── {scenario}_{size}k/  # Relatório individual por cenário/tamanho
│   │   ├── summary.md       # Métricas de fairness e estatísticas descritivas
│   │   └── plots/           # demographic_dist, continuous_dist, violin, heatmap
│   └── comparative/         # Análises cross-cenário (geradas por advanced_analysis.py)
├── src/                     # Código fonte do projeto
│   ├── evaluation/          # Scripts de avaliação de métricas de justiça (fairness)
│   │   ├── report_generator.py      # Gerador de relatórios por dataset
│   │   └── advanced_analysis.py     # Análises comparativas e testes estatísticos
│   ├── generators/          # Código dos geradores (Controlado, FairGAN)
│   └── pipeline/            # Orquestração do pipeline de dados
├── .env.example             # Exemplo de configuração de variáveis de ambiente
├── .gitignore               # Arquivos e pastas ignorados pelo Git
├── generate_dataset.py      # Script principal para rodar o pipeline de geração
├── LICENSE                  # Licença de uso
├── README.md                # Documentação principal
└── requirements.txt         # Dependências do projeto
```

## 💡 Exemplos de Uso

Acesse o diretório `examples/` para ver aplicações práticas dos datasets gerados:

- **Carregamento Básico:**
  ```bash
  python examples/load_dataset.py
  ```
- **Análise de Escalabilidade:**
  ```bash
  python examples/compare_dataset_sizes.py
  ```
- **Análise de Justiça (Fairness):**
  Calcula a paridade demográfica entre os cenários.
  ```bash
  python examples/basic_fairness_analysis.py
  ```

## 📊 Relatórios e Visualizações

Após rodar a geração, o diretório `reports/` é populado com um relatório estatístico completo (`summary.md`) e diversas análises avançadas no subdiretório `plots/`, incluindo:

- **Distribuições Demográficas e Contínuas** (Histogramas, KDE)
- **Comparação de Desempenho por Grupo** (Violin Plots)
- **Correlação entre Variáveis** (Heatmaps)
- **Métricas de Justiça e Diversidade** (Disparate Impact, Demographic Parity, Entropia de Shannon)

*(Abaixo, alguns exemplos de gráficos que são gerados na pasta `reports/`)*

```markdown
![Distribuições Contínuas](reports/biased_5k/plots/continuous_dist.png)
![Distribuição de Scores (Violin Plots)](reports/biased_5k/plots/score_violin_plots.png)
![Matriz de Correlação](reports/biased_5k/plots/correlation_heatmap.png)
```

## ☁️ Instruções de Deploy

O objetivo principal desta ferramenta é a **geração offline** de artefatos de dados. Caso deseje disponibilizar seus datasets publicamente ("deploy" dos dados):

1. **Hugging Face Datasets**:
   Utilize a biblioteca `datasets` do Hugging Face para fazer o upload dos CSVs gerados na pasta `data/final/` e torná-los públicos para a comunidade de pesquisa.
   
2. **Kaggle**:
   A pasta `data/final/` contém tudo o que é necessário para criar um Dataset no Kaggle, bastando anexar o `data/README.md` como descrição.

## ✍️ Autor

- **Luiz Henrique** - Pesquisa e Desenvolvimento.

## 📄 Licença

Este projeto está sob a licença **MIT**. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
