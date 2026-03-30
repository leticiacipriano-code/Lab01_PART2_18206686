# Relatório da Camada Gold - Análises de Negócio

## Análises de Negócio

| Métrica | Valor |
|---------|-------|
| **Data de Análise** | 2026-03-23 |
| **Total de Pacientes** | 1.000.000 |
| **Taxa de Diagnóstico Alterado (Infertilidade)** | 50.0% |
| **Registros Processados** | 1.000.000 |
| **Banco de Dados** | PostgreSQL (Star Schema) |

---

## Arquitetura do Data Warehouse

### Star Schema Implementado

```
                    dim_age
                      |
       dim_season --- fact_fertility --- dim_diagnosis
                      |
                   [Métricas]
```

### Tabelas Criadas

**Tabela Fato (fact_fertility)**
- patient_id: Identificador único
- age, season, diagnosis: FK para dimensões
- Variables: childish_diseases, accidents, surgeries, fevers, alcohol, smoking, hours_sitting

**Dimensões**
- dim_age: 10 grupos etários (27-36)
- dim_season: 4 estações
- dim_diagnosis: 2 categorias (Normal/Altered)

---

## ANÁLISE 1: Impacto do Fumo na Fertilidade

### Pergunta de Negócio
*"Qual é o impacto do hábito de fumar sobre a taxa de diagnóstico alterado?"*

### Dados Agregados

| Categoria | Total de Pacientes | Diagnóstico Alterado | Taxa de Alteração | Percentual na População |
|-----------|-------------------|---------------------|------------------|------------------------|
| Never (Nunca) | 500.000 | 250.000 | 50.0% | 50% |
| Occasional (Ocasionalmente) | 333.334 | 166.667 | 50.0% | 33% |
| Daily (Diariamente) | 166.666 | 83.333 | 50.0% | 17% |
| **TOTAL** | **1.000.000** | **500.000** | **50.0%** | **100%** |

![Taxa de alteração por hábito de fumar](analise1_fumo.png)

### Insights Principais
 O fumo não mostra correlação isolada com infertilidade, pois todos os grupos apresentam ~50% de alteração. Pode haver interações com outras variáveis.

### Recomendações
- Investigar correlações com múltiplos fatores de risco
- Dados sugerem necessidade de análise multivariada
- O fumo isoladamente não é determinante único

---

## ANÁLISE 2: Impacto do Sedentarismo na Fertilidade

### Pergunta de Negócio
*"Qual é a relação entre sedentarismo diário e diagnóstico de infertilidade?"*

### Dados Agregados

| Categoria de Sedentarismo | Horas Médias/Dia | Total de Pacientes | Diagnóstico Alterado | Taxa de Alteração |
|---------------------------|------------------|--------------------|----------------------|-------------------|
| Baixo (0-5h) | 3.5 | 200.000 | 100.000 | 50.0% |
| Médio (5-10h) | 7.5 | 500.000 | 250.000 | 50.0% |
| Alto (10-15h) | 12.5 | 250.000 | 125.000 | 50.0% |
| Crítico (15+h) | 18.0 | 50.000 | 25.000 | 50.0% |
| **TOTAL** | **10.8** | **1.000.000** | **500.000** | **50.0%** |

![Impacto do Sedentarismo na Fertilidade](analise2_sedentarismo.png)

### Insights Principais

Sedentarismo não é fator isolado determinante, pois existe 50% de alteração em todos os grupos. A população é bem distribuída em intervalos de sedentarismo.

### Recomendações
- Não parece ser fator causal primário para infertilidade nesta população
- Manter monitoramento para possíveis interações com outros fatores

---

## ANÁLISE 3: Sazonalidade e Diagnósticos

### Pergunta de Negócio
*"Há variação sazonal na prevalência de infertilidade?"*

### Dados Agregados

| Estação | Total de Pacientes | Diagnóstico Alterado | Taxa de Alteração | Percentual na População |
|---------|-------------------|---------------------|------------------|------------------------|
| Winter (Inverno) | 250.000 | 125.000 | 50.0% | 25% |
| Spring (Primavera) | 250.000 | 125.000 | 50.0% | 25% |
| Summer (Verão) | 250.000 | 125.000 | 50.0% | 25% |
| Fall (Outono) | 250.000 | 125.000 | 50.0% | 25% |
| **TOTAL** | **1.000.000** | **500.000** | **50.0%** | **100%** |

![Sazonalidade e Diagnósticos](analise3_sazonalidade.png)

### Insights Principais
Sazonalidade não é fator determinante em si, os dados estão equilibrados entre as 4 estações. Indica coleta bem balanceada.

### Recomendações
- Dados não mostram efeito sazonal clara na população
- Continuar monitoramento para variações em períodos mais longos
- Clima não parece ser fator primário

---

## ANÁLISE 4: Carga Acumulada de Fatores de Risco

### Pergunta de Negócio
*"Como múltiplos fatores de risco se combinam para impactar a fertilidade?"*

### Metodologia
Score de risco calculado pela contagem de fatores presentes:
- Childish diseases = yes
- Accident or serious trauma = yes
- Surgical intervention = yes
- High fevers in the last year (recente)
- Frequency of alcohol consumption (frequent)
- Smoking habit (occasional/daily)

### Distribuição por Score de Risco

| Score de Risco | Total de Pacientes | Diagnóstico Alterado | Taxa de Alteração | Principais Fatores |
|---|---|---|---|---|
| 0-1 fatores | 200.000 | 100.000 | 50.0% | Nenhum apresenta risco |
| 2-3 fatores | 400.000 | 200.000 | 50.0% | Moderado risco |
| 4-5 fatores | 350.000 | 175.000 | 50.0% | Risco elevado |
| 6+ fatores | 50.000 | 25.000 | 50.0% | Risco crítico |
| **TOTAL** | **1.000.000** | **500.000** | **50.0%** | - |

![Carga Acumulada de Fatores de Risco](analise4_risco_acumulado.png)

### Insights Principais
Nenhum fator isolado ou combinação prediz diagnóstico, a infertilidade nesta população é multifatorial. 

### Recomendações
- Infertilidade pode ter etiologia biológica/genética primária
- Manter abordagem holística mesmo em pacientes de baixo risco
- Investigar fatores não-detectáveis nas variáveis listadas

---

## ANÁLISE 5: Perfil Demográfico de Risco

### Pergunta de Negócio
*"Qual é o perfil etário e comportamental dos pacientes? Há grupos de risco específicos?"*

### Distribuição por Faixa Etária

| Faixa Etária | Total de Pacientes | Diagnóstico Alterado | Taxa de Alteração | % Fumantes | % Doenças Infantis | % Cirurgias |
|---|---|---|---|---|---|---|
| 27-28 anos | 100.000 | 50.000 | 50.0% | 25% | 25% | 25% |
| 29-30 anos | 250.000 | 125.000 | 50.0% | 30% | 30% | 30% |
| 31-32 anos | 350.000 | 175.000 | 50.0% | 35% | 35% | 35% |
| 33-36 anos | 300.000 | 150.000 | 50.0% | 40% | 40% | 40% |
| **TOTAL** | **1.000.000** | **500.000** | **50.0%** | **32%** | **32%** | **32%** |

![Perfil Demográfico de Risco](analise5_perfil_demografico.png)

### Insights Principais
Existem mais pacientes nas faixas maiores, com um padrão similar em todas as idades.

### Fatores por Faixa Etária
| Fator | 27-28 | 29-30 | 31-32 | 33-36 |
|-------|-------|-------|-------|-------|
| Fumantes | 50.0K | 75.0K | 122.5K | 120.0K |
| Doenças infantis | 25.0K | 75.0K | 122.5K | 120.0K |
| Cirurgias | 25.0K | 75.0K | 122.5K | 120.0K |

### Recomendações
- Todos os grupos etários requerem atenção similar
- Não há grupo etário de risco predominante
- Orientar para cuidados preventivos em todas as idades

---

## Visualizações Geradas

Todos os gráficos foram salvos em `data_gold/`:

- **analise1_fumo.png** - Taxa de alteração por hábito de fumar
- **analise2_sedentarismo.png** - Distribuição por horas sedentárias diárias
- **analise3_sazonalidade.png** - Variação por Estação do ano
- **analise4_risco_acumulado.png** - Correlação entre score de risco e diagnóstico
- **analise5_perfil_demografico.png** - 4 sub-gráficos por faixa etária

## Artefatos Gerados

### Banco de Dados PostgreSQL
- **Schema**: Star Schema Medallion
- **Tabelas Criadas**:
  - `fact_fertility` - 1.000.000 registros
  - `dim_age` - 10 grupos etários
  - `dim_season` - 4 estações
  - `dim_diagnosis` - 2 categorias

### Relatórios e Documentação
- `relatorio_gold.md` - Este documento (análises completas)
- `relatorio_silver.md` - Qualidade de dados da camada anterior
- `README.md` - Documentação do projeto completo

## Achados Principais

### Padrão Observado
A análise revela uma **taxa consistente de 50% de infertilidade em TODAS as subpopulações**:

| Categoria | Taxa de Infertilidade |
|-----------|----------------------|
| Fumantes | 50.0% |
| Sedentários | 50.0% |
| Todas as estações | 50.0% |
| Todos os grupos etários | 50.0% |
| Qualquer combinação de fatores | 50.0% |

### Interpretação
1. **Dataset Estruturado**: A uniformidade indica dados bem balanceados
2. **Padrão Simulado**: Suggests dados gerados com proporção fixa 50/50
3. **Implicação Prática**: Infertilidade nesta população pode ser:
   - Determinada por fatores genéticos/biológicos primários
   - Ou relacionada a variáveis não capturadas neste dataset


## Qualidade da Análise

| Aspecto | Status | Observação |
|--------|--------|-----------|
| Completude de Dados | ✓ | 100% de registros | 
| Integridade Referencial | ✓ | Foreign keys válidas |
| Performance de Query | ✓ | <2s para todas análises |
| Cobertura de Dimensões | ✓ | Todas as estações e idades |
| Validade Estatística | ⚠ | Distribuição uniforme susp eita |
| Relevância Clínica | ⚠ | Necessário validação especialista |

---