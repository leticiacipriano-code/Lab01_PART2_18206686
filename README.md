#  Lab01_PART2_18206686 

##  Visão Geral

Pipeline de dados completo seguindo o padrão **Medallion Architecture** (Raw → Silver → Gold → Warehouse) com:
-  **Camada Raw** (CSV bruto: 1M registros)
-  **Camada Silver** (Processamento e transformação em Parquet)
-  **Camada Warehouse** (PostgreSQL com schema `fertility_warehouse`)
-  **Camada Gold** (Análises e visualizações)
-  **Containerização Docker** (PostgreSQL 16 + Grafana 10)
-  **Validação de qualidade com Great Expectations** (5+ expectativas)
-  **Dashboard Grafana** com visualizações interativas
-  **Documentação reproduzível**

---

##  Início Rápido

### Pré-requisitos

```bash
# Sistema
- Docker Desktop 4.0+
- Python 3.9+
- Git

# Verificar versões
docker --version
docker-compose --version
python --version
```

### 1. Clone o Repositório

```bash
git clone https://github.com/seu-usuario/Lab01_PART2_18106686.git
cd Lab01_PART2_18106686
```

### 2. Configure o Ambiente Virtual

#### Opção A: Python venv (Recomendado)
```bash
# Windows
python -m venv .venv
.\.venv\Scripts\activate

# Linux/macOS
python3 -m venv .venv
source .venv/bin/activate
```

#### Opção B: UV (Mais rápido)
```bash
# Instalar UV
pip install uv

# Criar ambiente
uv venv
source .venv/bin/activate  # Linux/macOS
# ou
.\.venv\Scripts\activate  # Windows
```

### 3. Instale as Dependências

```bash
# Via requirements.txt
pip install -r requirements.txt

# Ou via pyproject.toml (recomendado)
pip install -e .

# Ou via uv (mais rápido com uv.lock)
uv pip install -r requirements.txt
```

### 4. Variáveis de Ambiente

Use as variáveis disponíveis em .env
---

##  Como Construir e Subir os Containers

### Passo 1: Construir a Imagem Docker

```bash
# Construir imagem da aplicação
docker build -t fertility-app:latest .

# Verificar
docker images | grep fertility
```

### Passo 2: Subir Containers com Docker Compose

```bash
# Subir todos os containers (PostgreSQL + Grafana)
docker-compose up -d

# Verificar status
docker-compose ps

# Logs em tempo real
docker-compose logs -f

# Logs de serviço específico
docker-compose logs -f postgres
docker-compose logs -f grafana
```

### Passo 3: Verificar Conectividade

```bash
# Teste 1: PostgreSQL está disponível
docker-compose exec postgres psql -U postgres -d fertility_gold -c "SELECT version();"

# Teste 2: Grafana (espere ~10-15s após inicialização)
curl http://localhost:3000/api/health

# Teste 3: Rede Docker
docker network ls | grep lab01
```

---

##  Como Executar o Pipeline de Dados

###  Fluxo Completo do Pipeline

```
CSV (1M registros) → Silver (Parquet) → Warehouse → Analytics (Grafana)
data_raw/fertility_1m.csv
         ↓
    silver.py (processa e salva em fertility_silver.parquet)
         ↓
   ingest_data.py (lê parquet e insere no warehouse)
         ↓
fertility_warehouse.fact_fertility (PostgreSQL)
         ↓
    gold.py (gera análises e visualizações)
         ↓
   Grafana Dashboard
```

### Passo 1: Processar Dados para Silver (Transformação)

```bash
# Ativar ambiente virtual
.\.venv\Scripts\activate  # Windows
# ou
source .venv/bin/activate  # Linux/macOS

# Executar transformação Silver
python data_silver/silver.py

# Saída esperada:
#  - fertility_silver.parquet criado
#  - Dados limpos e transformados
#  - Estatísticas de processamento
```

### Passo 2: Ingerir Dados no Warehouse

```bash
# Ingerir dados processados (Silver) para PostgreSQL
python src/ingest_data.py

# Ou usando main.py
python main.py ingest

# Saída esperada:
#  - Conexão ao PostgreSQL estabelecida
#  - 1M+ registros inseridos em fertility_warehouse.fact_fertility
#  - Integridade validada
```

### Passo 3: Gerar Análises Gold

```bash
# Executar análises e criar tabelas dimensionais
python data_gold/gold.py

# Saída esperada:
#  - fact_fertility e dimensões criadas em fertility_warehouse
#  - 5 análises executadas
#  - Visualizações salvas em data_gold/ (PNG)
```

### Pipeline Completo em Um Comando

```bash
# Executar validação + transformação + ingestão (tudo junto)
python main.py full

# Ou individuamente:
python main.py validate  # Apenas validação Great Expectations
```

### Verificar Dados Ingeridos

```bash
# Conectar ao PostgreSQL
docker-compose exec postgres psql -U postgres -d fertility_db

# No prompt psql:
-- Ver quantidade de registros
SELECT COUNT(*) FROM fertility_warehouse.fact_fertility;

-- Ver distribuição de diagnósticos
SELECT diagnosis, COUNT(*) FROM fertility_warehouse.fact_fertility 
GROUP BY diagnosis ORDER BY diagnosis;

-- Ver distribuição por estação
SELECT season, COUNT(*) FROM fertility_warehouse.fact_fertility 
GROUP BY season ORDER BY season;

-- Sair
\q
```

---

##  Dashboard Grafana

### Acessar Dashboard

1. **Abrir navegador**: http://localhost:3000
2. **Login**: 
   - Usuário: `admin`
   - Senha: `admin`
3. **Navegar para Dashboard**: "Fertility Data - Dashboard Simples"

### Visualizações Disponíveis

| # | Nome | Tipo | Descrição |
|---|------|------|-----------|
| 1 | **Total de Pacientes** | Stat/Card | Count total de registros |
| 2 | **Diagnóstico Alterado** | Stat/Card | Pacientes com diagnóstico alterado |
| 3 | **Diagnóstico Normal** | Stat/Card | Pacientes com diagnóstico normal |
| 4 | **Taxa de Alteração** | Stat/Card | Percentual de alterações |
| 5 | **Diagnósticos** | Pizza | Distribuição Normal vs Altered |
| 6 | **Estações** | Pizza | Distribuição por estação (Spring/Fall/Winter/Summer) |
| 7 | **Hábito de Fumo** | Pizza | Distribuição de fumantes |
| 8 | **Horas Sentado** | Barras | Distribuição de sedentarismo |
| 9 | **Resumo** | Tabela | Total e percentual por diagnóstico |

### Refresh Automático

- Intervalo padrão: **30 segundos**
- Clique **↻ Refresh** no canto superior direito para atualizar manualmente

### Filtros e Exploração

- Cada painel traz dados em tempo real do `fertility_warehouse.fact_fertility`
- Use tooltips (passar mouse) para ver detalhes exatos
- Dados são agregados automaticamente pelo Grafana

---

##  Estrutura do Projeto

```
Lab01_PART2_18206686/
├── src/                                # 📂 Código principal (Ingestão)
│   ├── __init__.py                     
│   ├── ingest_data.py                  # 📥 Lê Silver → Insere Warehouse
│   └── setup_great_expectations.py     # ✅ Validação de dados
├── main.py                             # 🚀 Script principal (orquestrador)
│
├── data_raw/                           # 📊 Camada Raw (Dados brutos)
│   └── fertility_1m.csv                # 1.000.000 registros originais
│
├── data_silver/                        # 🔄 Camada Silver (Transformação)
│   ├── silver.py                       # 🔧 Lê CSV → Processa → Salva Parquet
│   ├── fertility_silver.parquet        # Dados intermediários (transformados)
│   └── relatorio_silver.md             # 📋 Documentação de processamento
│
├── data_gold/                          # 🎯 Camada Gold (Análises)
│   ├── gold.py                         # 📊 Lê Silver → Cria Star Schema → Análises
│   ├── analise1_fumo.png               # Visualização: Fumo
│   ├── analise2_sedentarismo.png       # Visualização: Sedentarismo
│   ├── analise3_sazonalidade.png       # Visualização: Sazonalidade
│   ├── analise4_risco_acumulado.png    # Visualização: Risco
│   ├── analise5_perfil_demografico.png # Visualização: Perfil
│   └── relatorio_gold.md               # 📋 Documentação de análises
│
├── grafana/                            # 📈 Dashboard e Provisioning
│   ├── dashboards/
│   │   ├── fertility-main.json         # Dashboard principal (completo)
│   │   └── fertility-main-simple.json  # Dashboard simplificado
│   └── provisioning/
│       ├── dashboards/
│       │   └── dashboards.yaml         # Config automática dashboards
│       └── datasources/
│           └── postgresql.yaml         # Config PostgreSQL data source
│
├── gx_context/                         # ✅ Great Expectations
│   ├── great_expectations.yml          # Config GX
│   └── data_docs/
│       └── index.html                  # Relatório validação (HTML)
│
├── config/                             # ⚙️ Scripts auxiliares
│   ├── docker_commands.sh              # Comandos Docker
│   └── docker_commands.bat             # Comandos Docker (Windows)
│
├── docs/                               # 📖 Documentação técnica
│   ├── DOCKER_ARCHITECTURE.md          # Arquitetura Docker
│   ├── GRAFANA_ARQUITETURA.md          # Arquitetura Grafana
│   └── VALIDACAO_IMPLEMENTADA.md       # Detalhes de validação
│
├── docker-compose.yml                  # 🐳 Orquestração: PostgreSQL + Grafana
├── Dockerfile                          # 🔨 Imagem aplicação Python
├── init.sql                            # 🗄️ Schema: fertility_warehouse.fact_fertility
│
├── pyproject.toml                      # 📦 Dependências (moderno com Black/Pytest)
├── requirements.txt                    # 📦 Compatibilidade pip
├── dependencies_frozen.txt             # 📦 Versões congeladas (backup)
├── uv.lock.txt                         # 🔐 UV lock file (rápido)
│
├── .gitignore                          # 🚫 Git ignore (Python + Docker + Data)
├── README.md                           # 📖 Este arquivo
└── .env                                # 🔐 Variáveis ambiente
```

### Fluxo de Dados (Arquitetura)

```
Raw (CSV)
  ↓
silver.py → fertility_silver.parquet
  ↓
ingest_data.py → fertility_warehouse.fact_fertility (PostgreSQL)
  ↓
gold.py → Análises + Dimensões
  ↓
Grafana Dashboard (Visualizações)
```

### Tabelas PostgreSQL

**Schema**: `fertility_warehouse`

| Tabela | Tipo | Colunas | Descrição |
|--------|------|---------|-----------|
| `fact_fertility` | Fato | patient_id (PK), age, season, diagnosis, etc | Dados principais (1M+ registros) |
| `dim_age` | Dimensão | age_id (PK), age, age_group | Dimensão etária |
| `dim_season` | Dimensão | season_id (PK), season | Dimensão estação |
| `dim_diagnosis` | Dimensão | diagnosis_id (PK), diagnosis | Dimensão diagnóstico |

---

##  Validação de Dados com Great Expectations

### Expectativas Implementadas

| # | Expectativa | Coluna | Validação |
|---|-------------|--------|-----------|
| 1 | `expect_column_values_to_not_be_null` | age, season, diagnosis | Sem valores NULL |
| 2 | `expect_column_values_to_be_between` | age | 25 ≤ age ≤ 36 |
| 3 | `expect_column_distinct_values_to_be_in_set` | diagnosis | {Normal, Altered} |
| 4 | `expect_column_distinct_values_to_be_in_set` | season | {spring, summer, fall, winter} |
| 5 | `expect_no_duplicate_rows` | * | Sem linhas duplicadas |

### Executar Validação

```bash
# Validar dados com Great Expectations
python main.py validate

# Ou diretamente:
python src/setup_great_expectations.py

# Ver relatório HTML
# Windows:
start gx_context/data_docs/index.html

# Linux:
xdg-open gx_context/data_docs/index.html

# macOS:
open gx_context/data_docs/index.html
```

### Saída Esperada

```
✓ 5+ expectativas validadas
✓ Data Docs gerado em: gx_context/data_docs/index.html
✓ Relatório interativo com gráficos de validação
```

---

##  Análises Gold Geradas

### 5 Análises Executadas

1. **Análise 1: Impacto do Fumo na Fertilidade**
   - Taxa de diagnóstico alterado por hábito de fumo
   - Visualização: `data_gold/analise1_fumo.png`

2. **Análise 2: Impacto do Sedentarismo**
   - Correlação entre horas sentado e fertilidade
   - Visualização: `data_gold/analise2_sedentarismo.png`

3. **Análise 3: Sazonalidade e Diagnósticos**
   - Distribuição de diagnósticos por estação
   - Visualização: `data_gold/analise3_sazonalidade.png`

4. **Análise 4: Carga Acumulada de Risco**
   - Score de risco vs diagnóstico
   - Visualização: `data_gold/analise4_risco_acumulado.png`

5. **Análise 5: Perfil Demográfico**
   - Taxa de alteração por faixa etária + comorbidades
   - Visualização: `data_gold/analise5_perfil_demografico.png`

---

## 🛠️ Troubleshooting

### Limpar tudo e começar do zero

```bash
# Opção 1: Parar mantendo volumes (dados preservados)
docker-compose stop

# Opção 2: Remover tudo (⚠️ deleta dados)
docker-compose down -v

# Reconstruir imagem
docker build -t fertility-app:latest .

# Reiniciar
docker-compose up -d

# Executar pipeline novamente
python main.py full
```

### Ver Logs de Containers

```bash
# Todos os logs
docker-compose logs -f

# Apenas PostgreSQL
docker-compose logs -f postgres

# Apenas Grafana
docker-compose logs -f grafana

# Apenas aplicação
docker-compose logs -f app
```

### Verificar Saúde dos Containers

```bash
# Status geral
docker-compose ps

# Detalhes de um container
docker-compose inspect postgres

# Network
docker network ls
docker network inspect lab01_default
```
