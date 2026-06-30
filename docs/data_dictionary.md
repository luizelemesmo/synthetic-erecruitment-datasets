# Dicionário de Dados (Data Dictionary)

Este documento descreve o esquema e os atributos contidos nos datasets gerados para o projeto.

| Atributo | Tipo | Descrição | Sensível? |
| :--- | :--- | :--- | :---: |
| `id` | String | Identificador único do candidato (ex: `CAND_00000`). | Não |
| `skills` | Inteiro | Medida quantitativa das habilidades técnicas do candidato (escala de 0 a 100). | Não |
| `years_experience` | Decimal (Float) | Quantidade de anos de experiência profissional do candidato. | Não |
| `education_level` | Categórico | Nível máximo de escolaridade atingido (`Ensino Médio`, `Bacharelado`, `Mestrado`, `Doutorado`). | Não |
| `location` | Categórico | Região geográfica do candidato (`Capitais`, `Região Metropolitana`, `Interior`). | Não |
| `preferred_work_mode` | Categórico | Preferência de modalidade de trabalho do candidato (`Presencial`, `Híbrido`, `Remoto`). | Não |
| `gender` | Categórico | Identidade de gênero declarada pelo candidato (`Masculino`, `Feminino`, `Não-binário`). | **Sim** |
| `race` | Categórico | Raça ou etnia autodeclarada pelo candidato (`Branca`, `Preta`, `Parda`, `Amarela`, `Indígena`). | **Sim** |
| `suitability_score` | Decimal (Float) | Pontuação contínua de adequabilidade (0 a 1) que reflete o alinhamento técnico do candidato à vaga. | Não |
