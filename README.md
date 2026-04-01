#  Lab01_PART2_18106686 

##  Visão Geral

Pipeline de dados completo seguindo o padrão **Medallion Architecture** (Raw → Silver → Gold) com:
-  Containerização Docker (PostgreSQL + Grafana)
-  Validação de qualidade com Great Expectations (5+ expectativas)
-  Dashboard Grafana com 6+ visualizações
-  Documentação reproduzível

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

### Opção 1: Script Principal (Recomendado)

```bash
# Ativar ambiente virtual
.\.venv\Scripts\activate  # Windows
# ou
source .venv/bin/activate  # Linux/macOS

# Ver opções disponíveis
python main.py --help

# Executar validações apenas
python main.py validate

# Executar ingestão apenas
python main.py ingest

# Executar pipeline completo (validação + ingestão)
python main.py full
# ou simplesmente
python main.py
```

### Opção 2: Executar Validações com Great Expectations

```bash
# 1. Ativar ambiente virtual
source .venv/bin/activate  # Linux/macOS
# ou
.\.venv\Scripts\activate  # Windows

# 2. Executar validação
python src/setup_great_expectations.py

# Saída esperada:
#  5+ expectativas validadas
#  Data Docs gerado em: gx_context/data_docs/index.html
```

### Opção 3: Ver Relatório de Validação

```bash
# Abrir no navegador:
# Windows
start gx_context/data_docs/index.html

# Linux
xdg-open gx_context/data_docs/index.html

# macOS
open gx_context/data_docs/index.html
```

### 5+ Expectativas Implementadas

| # | Expectativa | Coluna | Validação |
|---|-------------|--------|-----------|
| 1 | `expect_column_values_to_not_be_null` | age, season, diagnosis | Sem valores nulos |
| 2 | `expect_column_values_to_be_between` | age | 25 ≤ age ≤ 36 |
| 3 | `expect_column_distinct_values_to_be_in_set` | diagnosis | {Normal, Altered} |
| 4 | `expect_column_distinct_values_to_be_in_set` | season | {spring, summer, fall, winter} |
| 5 | `expect_no_duplicate_rows` | * | Sem duplicatas |

---

##  Como Ingerir Dados

### Pipeline de Ingestão Automático

```bash
# Usando main.py
python main.py ingest

# Ou executar manualmente
python src/ingest_data.py
```

**O que faz o pipeline:**
1. Valida dados com Great Expectations
2. Carrega `data_raw/fertility_1m.csv`
3. Conecta ao PostgreSQL (container Docker)
4. Cria tabela `fertility_data` em `fertility_gold`
5. Insere 1.000.000+ registros em batches
6. Verifica integridade dos dados

### Verificar Dados Ingeridos

```bash
# Conectar ao PostgreSQL
docker-compose exec postgres psql -U postgres -d fertility_gold

# No prompt psql:
SELECT COUNT(*) FROM fertility_data;
SELECT diagnosis, COUNT(*) FROM fertility_data GROUP BY diagnosis;
SELECT season, COUNT(*) FROM fertility_data GROUP BY season;

# Sair
\q
```

---

##  Dashboard Grafana

### Acessar o Dashboard

1. **Abrir navegador**: http://localhost:3000
2. **Login**: 
   - Usuário: `admin`
   - Senha: `admin`
3. **Navegar para Dashboard**: "[Fertility Data - Gold Layer](http://localhost:3000/d/e72d2392-e785-4299-8792-b7cd32c30e63/)"

### Visualizações Disponíveis

| # | Tipo | Descrição | Dados |
|---|------|-----------|-------|
| 1 | **Stat** | Total de Registros | 1.000.000+ |
| 2 | **Gauge** | Taxa de Diagnósticos Alterados (%) | 12.5% |
| 3 | **Pizza** | Distribuição Diagnóstica | Normal vs Altered |
| 4 | **Barras** | Registros por Estação | Spring, Fall, Winter, Summer |
| 5 | **Histograma** | Distribuição Etária | Faixas 25-36 anos |
| 6 | **Tabela** | Diagnóstico × Estação | Análise cruzada |

### Atualizar Dashboard

- Clique **Refresh** (↻) no canto superior direito
- Intervalo automático: 10 segundos

---

##  Estrutura do Projeto

```
Lab01_PART2_18106686/
├── src/                                # 📂 Código principal
│   ├── __init__.py                     
│   ├── ingest_data.py                  # 📥 Pipeline de ingestão
│   └── setup_great_expectations.py     # ✅ Validação de dados
├── main.py                             # 🚀 Script principal (orquestrador)
│
├── data_raw/                           # 📊 Dados brutos
│   └── fertility_1m.csv                # 1.000.000 registros de entrada
│
├── data_silver/                        # 🔄 Dados processados
│   ├── silver.py                       # Transformações intermediárias
│   └── relatorio_silver.md             # 📋 Documentação de silver
│
├── data_gold/                          # 🎯 Dados refinados (análises)
│   ├── gold.py                         # Análises finais e agregações
│   └── relatorio_gold.md               # 📋 Documentação de gold
│
├── grafana/                            # 📈 Dashboard e provisioning
│   ├── dashboards/
│   │   └── fertility-main.json         # Dashboard Grafana
│   └── provisioning/
│       ├── dashboards/
│       │   └── dashboards.yaml         # Config automática dashboards
│       └── datasources/
│           └── postgresql.yaml         # Config PostgreSQL data source
│
├── gx_context/                         # ✅ Great Expectations
│   └── data_docs/
│       └── index.html                  # Relatório validação (HTML)
│
├── docker-compose.yml                  # 🐳 Orquestração: PostgreSQL + Grafana
├── Dockerfile                          # 🔨 Imagem aplicação Python
├── init.sql                            # 🗄️ Inicialização banco de dados
│
├── pyproject.toml                      # 📦 Dependências (formato moderno)
├── requirements.txt                    # 📦 Compatibilidade
├── dependencies_frozen.txt             # 📦 Lock dependencies
├── uv.lock.txt                         # 🔐 UV lock file
├── .gitignore                          # 🚫 Git ignore
│
└── README.md                           # 📖 Este arquivo
```

---

## 🛠️ Troubleshooting

### Limpar tudo e começar do zero

```bash
# Option 1: Parar containers mantendo volumes
docker-compose stop

# Option 2: Parar e remover containers + volumes (⚠️ deleta dados)
docker-compose down -v

# Reconstruir imagem
docker build -t fertility-app:latest .

# Reiniciar
docker-compose up -d
```