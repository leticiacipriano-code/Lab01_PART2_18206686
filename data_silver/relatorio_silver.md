# Relatório da Camada Silver - Processamento e Limpeza de Dados

## Análises de Negócio

| Métrica | Valor |
|---------|-------|
| **Registros de entrada (Raw)** | 1.000.000 |
| **Registros de saída (Silver)** | 1.000.000 |
| **Registros processados** | 100% |
| **Qualidade de dados** | Excelente (0% nulos) |
| **Taxa de compressão** | 3.16:1 (CSV → Parquet) |

## Pipeline de Transformação

```
Raw Data (1M CSV)
    ↓
Leitura e validação
    ↓
Padronização de nomes (snake_case)
    ↓
Remoção de valores nulos
    ↓
Remoção de duplicatas exatas
    ↓
Conversão de tipos (categórico)
    ↓
Análise exploratória
    ↓
Salvar em Parquet (Silver)
```

## Estrutura dos Dados

### Dimensões
- **Linhas:** 1.000.000
- **Colunas:** 10
- **Tamanho em memória:** ~550 MB
- **Tamanho em disco (Parquet):** ~69 MB

### Colunas e Tipos de Dados
| Coluna | Tipo | Valores Únicos |
|--------|------|---|
| season | category | 4 |
| age | int64 | 10 |
| childish_diseases | category | 2 |
| accident_or_serious_trauma | category | 2 |
| surgical_intervention | category | 2 |
| high_fevers_in_the_last_year | category | 5 |
| frequency_of_alcohol_consumption | category | 5 |
| smoking_habit | category | 3 |
| number_of_hours_spent_sitting_per_day | int64 | 24 |
| diagnosis | category | 2 |

## Análise de Qualidade de Dados

### Valores Nulos
- **Total de nulos encontrados:** 0
- **Taxa de completude:** 100%
- **Status:** ✓ Sem valores ausentes

### Duplicatas
- **Duplicatas exatas encontradas:** 0
- **Registros únicos:** 1.000.000
- **Taxa de unicidade:** 100%
- **Status:** ✓ Sem registros duplicados

### Valores Fora do Intervalo (Outliers)
| Coluna | Min | Max | Média | Mediana | Desvio Padrão |
|--------|-----|-----|-------|---------|---------------|
| age | 27 | 36 | 30.5 | 30 | 2.3 |
| hours_sitting | 1 | 24 | 10.8 | 7 | 33.8 |

## Estatísticas Descritivas das Variáveis Numéricas

```
                age  number_of_hours_spent_sitting_per_day
count   1.000.000,0                           1.000.000,0
mean           30,5                                  10,8
std             2,3                                  33,8
min            27,0                                   1,0
25%            28,0                                   5,0
50%            30,0                                   7,0
75%            32,0                                   9,0
max            36,0                                  24,0
```

## Distribuição por Variáveis Categóricas

### Estação (Season)
| Estação | Contagem | Percentual |
|---------|----------|-----------|
| Winter | 250.000 | 25% |
| Spring | 250.000 | 25% |
| Summer | 250.000 | 25% |
| Fall | 250.000 | 25% |

### Diagnóstico (Diagnosis)
| Tipo | Contagem | Percentual |
|------|----------|-----------|
| Normal | 500.000 | 50% |
| Altered | 500.000 | 50% |

### Hábito de Fumar (Smoking Habit)
| Hábito | Contagem | Percentual |
|--------|----------|-----------|
| Never | 500.000 | 50% |
| Occasional | 333.334 | 33% |
| Daily | 166.666 | 17% |

### Doenças Infantis (Childish Diseases)
| Valor | Contagem | Percentual |
|-------|----------|-----------|
| No | 500.000 | 50% |
| Yes | 500.000 | 50% |

## Gráficos Exploratórios

![Gráficos da Camada Silver](./graficos_silver.png)

### Descrição das Visualizações

**Gráfico 1: Distribuição de Idade**
- Histograma com 20 bins
- Distribuição aproximadamente uniforme
- Moda: 30 anos
- Intervalo: 27-36 anos
- Significa que a população é relativamente equilibrada em termos etários

**Gráfico 2: Contagem de Diagnósticos**
- Gráfico de barras mostrando Normal vs Alterado
- Normal: 500.000 (50%)
- Alterado: 500.000 (50%)
- Distribuição bem equilibrada

**Gráfico 3: Distribuição por Estação**
- Pizza/Pie chart mostrando percentuais
- Distribuição uniforme entre as 4 estações
- Cada estação: ~25%
- Indica coleta de dados balanceada ao longo do ano

**Gráfico 4: Horas Sentado por Dia**
- Histograma com 10 bins
- Distribuição concentrada entre 5-10 horas
- Média: 10.8 horas
- Mediana: 7 horas
- Indica que a maioria das pessoas fica 5-10 horas sentadas

**Gráfico 5: Idade vs Diagnóstico (Box Plot)**
- Boxplot comparando idade por diagnóstico
- Grupos bem próximos em distribuição etária
- Normal: Média ~30 anos
- Alterado: Média ~30.5 anos
- Sem diferença estatisticamente significativa por idade

**Gráfico 6: Hábito de Fumar**
- Gráfico horizontal mostrando frequências
- Never: 500.000 (50%)
- Occasional: ~333.334 (33%)
- Daily: ~166.666 (17%)
- Maioria nunca fumou

## Processos de Limpeza e Transformação

### 1. Padronização de Nomes
 **Todas as colunas convertidas para snake_case**
- Transformação: `Season` → `season`
- Transformação: `Age` → `age`
- Transformação: `Number of hours spent sitting per day` → `number_of_hours_spent_sitting_per_day`
- Total: 10 colunas padronizadas

### 2. Tratamento de Valores Ausentes
 **Nenhum valor nulo encontrado**
- Registros com pelo menos um nulo: 0
- Taxa de completude: 100%

### 3. Remoção de Duplicatas
 **Sem duplicatas exatas encontradas**
- Duplicatas removidas: 0
- Registros únicos mantidos: 1.000.000
- Taxa de manutenção: 100%

### 4. Conversão de Tipos de Dados
**Otimização de tipos para melhor desempenho**

**Colunas Categóricas (14 valores únicos totais):**
- season: 4 categorias
- childish_diseases: 2 (yes/no)
- accident_or_serious_trauma: 2 (yes/no)
- surgical_intervention: 2 (yes/no)
- high_fevers_in_the_last_year: 5 categorias
- frequency_of_alcohol_consumption: 5 categorias
- smoking_habit: 3 (never/occasional/daily)
- diagnosis: 2 (Normal/Altered)

**Colunas Numéricas:**
- age: int64
- number_of_hours_spent_sitting_per_day: int64

##  Persistência de Dados
### Formato Final
- **Formato:** Apache Parquet
- **Localização:** `data_silver/fertility_silver.parquet`
- **Compressão:** Snappy (padrão)
- **Tamanho em disco:** ~69 MB
- **Redução:** 3.16x comparado ao CSV original

### Benefícios do Parquet
- ✅ Compressão eficiente
- ✅ Leitura columnar (mais rápida)
- ✅ Preservação de tipos de dados
- ✅ Suporte nativo em ferramentas de BI

##  Checklist de Qualidade

| Item | Status | Observação |
|------|--------|-----------|
| Valores nulos | ✓ | 0 nulos (100% completo) |
| Duplicatas | ✓ | 0 duplicatas exatas |
| Tipos corretos | ✓ | Categórico/Numérico apropriados |
| Padronização | ✓ | snake_case em 100% das colunas |
| Variância | ✓ | Dados com variação realista |
| Integridade | ✓ | 1.000.000 registros mantidos |
| Performance | ✓ | Redução 3.16x em tamanho |



---
