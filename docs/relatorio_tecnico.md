# Relatório Técnico: Geração de Dados Sintéticos para E-Recruitment

## 1. Introdução

A adoção de Inteligência Artificial nos processos seletivos mudou a forma como lidamos com grandes volumes de currículos. No entanto, os sistemas de recomendação em recrutamento digital muitas vezes acabam reproduzindo vieses históricos que já existem nos dados reais. Isso pode acabar favorecendo certos grupos demográficos e prejudicando outros. Para garantir que esses sistemas sejam mais justos (*fairness*), não basta apenas identificar o problema; é preciso criar formas ativas de mitigar a discriminação baseada em atributos sensíveis, como gênero e raça.

Um dos maiores desafios para desenvolver e avaliar sistemas éticos é a falta de bases de dados reais que tenham esses atributos sensíveis bem mapeados. Na maioria das vezes, esses dados são protegidos por leis de privacidade, como a LGPD. Para contornar isso e criar um ambiente seguro e controlado para testes, desenvolvemos um pipeline de geração de dados sintéticos. O uso de dados gerados artificialmente permite controlar as distribuições estatísticas. Com isso, podemos simular desde cenários com viés extremo (para testar os limites das métricas) até cenários perfeitamente justos (para calibrar os algoritmos). No fim, essa abordagem serve como base para avaliarmos métricas de justiça, como paridade estatística (*statistical parity*) e impacto díspar (*disparate impact*).

## 2. Visão Geral da Arquitetura do Sistema

A arquitetura do sistema foi pensada para ser modular, fácil de reproduzir e escalável, o que é fundamental para qualquer experimento em Machine Learning. O repositório foi organizado de uma maneira que separa bem o código, os dados e as configurações.

O diretório `data/` funciona como o repositório principal de dados, dividido entre dados crus, processados e sintéticos. Isso ajuda a rastrear todo o ciclo de vida da informação. A lógica principal fica no diretório `src/`. Lá, o subdiretório `src/data/` guarda os geradores de dados e as definições de esquema, separando a lógica do projeto da execução. Funções utilitárias, como o carregamento de configurações e a fixação de sementes aleatórias (*seeds*), ficam em `src/utils/`. Além disso, criamos a camada `src/experiments/` para concentrar as rotinas de avaliação e o cálculo das métricas de justiça.

Para facilitar a experimentação, as configurações operacionais não ficam no código-fonte, mas sim em arquivos YAML dentro da pasta `configs/`. Isso é muito útil em pesquisas, pois permite rodar diferentes testes (como mudar a intensidade do viés ou hiperparâmetros) sem precisar mexer no código. Por fim, a pasta `notebooks/` contém os roteiros para análises visuais, o que é essencial para validar se o viés foi injetado ou mitigado corretamente.

## 3. Modelagem dos Dados Sintéticos

A estrutura dos dados foi baseada no que costumamos ver na literatura sobre sistemas de recrutamento. Criamos um esquema (`schema.py`) que divide os atributos do candidato em três grupos: informações objetivas, atributos sensíveis e a variável alvo.

As informações objetivas representam o histórico profissional do candidato. Os anos de experiência (`years_experience`) e o nível educacional (`education_level`) são indicadores clássicos de qualificação. Já a variável de habilidades (`skills`) resume a compatibilidade técnica para a vaga. Para refletir as mudanças recentes no mercado de trabalho, também incluímos a modalidade de trabalho preferida (`preferred_work_mode` – remoto, híbrido ou presencial) e a localização (`location`).

Os atributos sensíveis são aquelas características demográficas que, por razões legais e éticas, não devem prejudicar o candidato no processo seletivo. Aqui, focamos em gênero (`gender`) e raça (`race`).

A variável alvo é o `suitability_score`, que funciona como uma pontuação de adequação do candidato à vaga. Em um cenário real, essa nota seria dada por um recrutador ou estimada pelo modelo. No nosso gerador sintético, esse escore é calculado matematicamente a partir das informações objetivas. A adição de ruído e viés atua diretamente nessa pontuação para simular como o preconceito algorítmico ocorre na prática.

## 4. Abordagem 1: Geração com FairGAN

A primeira abordagem que desenvolvemos usa Redes Generativas Adversariais (GANs), especificamente inspirada no modelo FairGAN. A ideia do FairGAN é gerar um conjunto de dados sintético que mantenha as correlações e a estrutura estatística dos dados originais, mas que remova a capacidade de prever atributos sensíveis com base em outras variáveis.

Implementamos esse modelo no arquivo `fairgan_generator.py`, usando uma arquitetura comum para dados em tabelas. Construímos um Gerador e um Discriminador com PyTorch, junto com uma etapa de pré-processamento que lida automaticamente com variáveis categóricas e contínuas. O Gerador tenta criar perfis realistas a partir de ruído aleatório, enquanto o Discriminador tenta descobrir se os dados são reais ou sintéticos.

A questão da justiça algorítmica entra aqui como uma penalidade para o Gerador. Em uma implementação completa do FairGAN, além de enganar o discriminador normal, o gerador também precisa enganar um "Discriminador de Justiça". Isso significa que deve ser impossível adivinhar a raça ou o gênero de um candidato gerado apenas olhando para as habilidades e para a pontuação de adequação. A vantagem dessa abordagem é que ela consegue captar padrões bem complexos nos dados. Por outro lado, as GANs costumam ser difíceis de treinar, exigem mais custo computacional e o processo de mitigação de viés não é tão transparente.

## 5. Abordagem 2: Geração Controlada (Custom)

Para ter uma alternativa mais transparente e fácil de controlar, criamos a Geração Controlada (`controlled_generator.py`). Diferente da GAN, que aprende os padrões sozinha, este gerador cria os dados de forma explícita, usando distribuições de probabilidade do NumPy.

Nessa abordagem, o pesquisador define previamente as médias e desvios padrões para as variáveis contínuas, além das probabilidades para as categorias. O cálculo começa isolando a capacidade técnica do candidato para formar o *score base* ($S_{base}$). Isso é feito combinando experiência e habilidades, normalizadas pelos seus valores máximos:

$$ S_{base} = \left( \frac{\text{experiência}}{\max(\text{experiência})} \times 0.4 \right) + \left( \frac{\text{habilidades}}{\max(\text{habilidades})} \times 0.4 \right) + f(\text{educação}) $$

Aqui, a função $f(\text{educação})$ adiciona um bônus numérico de acordo com o nível acadêmico (por exemplo, 0.10 para Ensino Médio, 0.25 para Doutorado). Esse resultado representa o mérito puro do candidato.

O grande diferencial desse método é a forma como ele injeta viés. Se configurarmos o gerador para o modo `biased`, ele aplica bônus ou penalidades ao $S_{base}$ dependendo exclusivamente dos atributos demográficos do candidato. Esses valores de viés são definidos no arquivo YAML. Matematicamente, a nota final ($S_{final}$) fica assim:

$$ S_{final} = \min\left(1, \max\left(0, S_{base} + \text{Viés}_{G\text{ê}nero} + \text{Viés}_{Ra\text{ç}a} + \text{Viés}_{Localiza\text{ç}\text{ão}} + \epsilon \right)\right) $$

O $\epsilon \sim \mathcal{N}(0, \sigma^2)$ é um ruído aleatório gaussiano (ex: $\sigma = 0.1$) que ajuda a dar uma variação natural às pontuações.

Para entender melhor como isso funciona na prática:
* **Exemplo de Bonificação (Viés Positivo)**: Um candidato Homem Branco Urbano recebe bônus positivos: $\text{Viés} = +0.10 (\text{Homem}) + 0.10 (\text{Branco}) + 0.05 (\text{Urbano}) = +0.25$. Isso infla o seu $S_{base}$, ajudando esse grupo a ficar acima da nota de corte com mais facilidade.
* **Exemplo de Penalização (Viés Negativo)**: Uma candidata Mulher Negra de área Rural sofre penalidades: $\text{Viés} = -0.10 (\text{Mulher}) - 0.15 (\text{Negra}) - 0.10 (\text{Rural}) = -0.35$. Na prática, mesmo que ela e o candidato anterior tivessem exatamente o mesmo $S_{base}$ de mérito técnico ($0.75$), a nota final dela cairia para $0.40$, enquanto a dele chegaria facilmente ao limite de $1.00$.

Essa forma de controle é essencial para conduzir testes. Como sabemos exatamente a quantidade e a direção do viés injetado, podemos avaliar se um sistema de recomendação consegue ou não corrigir essa desigualdade. Além disso, o gerador possui um modo `debiased` que desliga toda a injeção de viés e garante que todos os grupos demográficos tenham a mesma probabilidade, servindo como uma linha de base totalmente justa para comparações.

## 6. Configuração e Parametrização

Para manter o projeto organizado, todas as variáveis operacionais ficam em arquivos YAML na pasta `configs/`. O arquivo `data_config.yaml` controla a geração estatística, definindo as probabilidades para as categorias (como etnias e gêneros) e direcionando as funções do NumPy.

O `fairgan_config.yaml` guarda as configurações do aprendizado da rede neural, como taxas de aprendizado, número de épocas e arquitetura do modelo.

Um ponto muito importante para a pesquisa científica é a reprodutibilidade. O módulo `seed.py` gerencia as sementes aleatórias do Python, NumPy e PyTorch. Isso garante que, com a mesma configuração e a mesma *seed*, qualquer pesquisador consiga gerar uma base de dados exatamente igual à nossa.

## 7. Pipeline de Geração de Dados

Para facilitar o uso, todo o processo foi unificado em um script que pode ser rodado pelo terminal. O arquivo `generate_synthetic.py` carrega as configurações e decide qual método usar com base no argumento `--method` passado pelo usuário.

Se a escolha for a geração controlada, o sistema aplica as regras matemáticas e salva o resultado na pasta `data/synthetic/`. Caso a escolha seja a GAN, o pipeline usa a geração controlada para criar uma base inicial (com viés) que servirá de exemplo para a rede neural. O PyTorch então treina o modelo `FairGANGenerator` e, em seguida, gera os perfis sintéticos finais.

Essa automação torna o processo muito mais prático, conectando a configuração, a geração dos dados e a preparação para os testes do modelo de recomendação de forma simples e direta.

## 8. Relação com os Objetivos do Projeto

Toda a estrutura que construímos está diretamente ligada aos objetivos do projeto de e-recrutamento:

1. **Justiça (Fairness)**: Ao conseguir gerar dados intencionalmente enviesados, criamos o ambiente perfeito para testar algoritmos de mitigação. O script `data_generation_experiment.py` calcula métricas como a Paridade Estatística e o Impacto Díspar. Sem esses dados sintéticos, seria muito difícil medir se uma intervenção está realmente tornando o sistema mais justo.
2. **Diversidade**: A parametrização no YAML força o algoritmo a lidar com uma força de trabalho diversa. Conseguimos medir como as recomendações finais estão distribuídas e se estamos garantindo variedade nos perfis selecionados.
3. **Flexibilidade Geográfica**: Incluir variáveis como modalidade de trabalho e localização reflete os novos desafios do mercado. Com esses dados, podemos analisar como a flexibilidade remota, que não depende de distância física, pode ser um fator ético para incluir talentos de diversas regiões.

## 9. Possíveis Extensões e Melhorias

Este módulo é um ponto de partida robusto, mas ainda existem várias possibilidades para o futuro:

* **Injeção de Padrões Mais Complexos:** A lógica atual adiciona viés de forma linear. No futuro, seria interessante simular efeitos onde os vieses se cruzam de forma mais complexa (por exemplo, os desafios enfrentados especificamente por mulheres negras), usando distribuições mais avançadas.
* **Dados Textuais:** O recrutamento do mundo real usa muito texto. Usar modelos de linguagem (LLMs) para gerar pequenos resumos ou descrições de projetos para os candidatos sintéticos expandiria muito as possibilidades de teste do sistema.
* **Dinâmicas de Longo Prazo:** Pode ser interessante adicionar uma camada de tempo para simular como as decisões do sistema afetam o mercado a longo prazo. Por exemplo, como as recomendações atuais podem influenciar as qualificações que os candidatos buscarão no futuro.
