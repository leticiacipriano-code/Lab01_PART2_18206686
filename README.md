# 🧬 Fertility Data Pipeline - Lab01_B

## 📋 Visão Geral

Pipeline de dados completo seguindo o padrão **Medallion Architecture** (Raw → Silver → Gold) com:
- ✅ Containerização Docker (PostgreSQL + Grafana)
- ✅ Validação de qualidade com Great Expectations (5+ expectativas)
- ✅ Dashboard Grafana com 6+ visualizações
- ✅ Documentação reproduzível

---

## 🚀 Início Rápido

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
git clone https://github.com/seu-usuario/Lab01_PART2_NUSP.git
cd Lab01_PART2_NUSP
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

# Ou via pyproject.toml
pip install -e .
```

### 4. Configure Variáveis de Ambiente

```bash
# Copiar exemplo
cp .env.example .env

# Editar .env com credenciais
# DB_HOST=postgres (dentro Docker) ou localhost (fora)
# DB_PASSWORD=senha
```

---

## 🐳 Como Construir e Subir os Containers

### Passo 1: Construir a Imagem Docker

```bash
# Construir imagem da aplicação
docker build -t fertility-app:latest .

# Verificar
docker images | grep fertility
```

### Passo 2: Subir Containers com Docker Compose

```bash
# Subir todos os containers
docker-compose up -d

# Verificar status
docker-compose ps

# Logs em tempo real
docker-compose logs -f postgres
docker-compose logs -f grafana
```

### Passo 3: Verificar Conectividade

```bash
# Teste 1: PostgreSQL
docker exec fertility_postgres psql -U postgres -d fertility_gold -c "SELECT version();"

# Teste 2: Grafana (espere ~10s)
curl http://localhost:3000/api/health

# Teste 3: Rede Docker
docker network ls | grep fertility
```

---

## ✅ Como Executar as Validações do Great Expectations

### Executar Validações

```bash
# 1. Ativar ambiente virtual
.\.venv\Scripts\activate  # Windows
# ou
source .venv/bin/activate  # Linux/macOS

# 2. Executar validação
python src/setup_great_expectations.py

# Saída esperada:
# ✅ 5 expectativas validadas
# ✅ Data Docs gerado em: gx_context/data_docs/index.html
```

### Ver Relatório de Validação

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

## 📥 Como Ingerir Dados

### Pipeline de Ingestão Automático

```bash
# 1. Ativar ambiente
.\.venv\Scripts\activate

# 2. Executar pipeline
python src/ingest_data.py

# Passos executados:
# 1. Valida dados com Great Expectations
# 2. Carrega fertility_1m.csv
# 3. Conecta ao PostgreSQL (via Docker)
# 4. Cria tabela fertility_data
# 5. Insere 1.000.000 registros em batches
# 6. Verifica integridade
```

### Verificar Dados Ingeridos

```bash
# Conectar ao PostgreSQL
docker exec -it fertility_postgres psql -U postgres -d fertility_gold

# No prompt psql:
SELECT COUNT(*) FROM fertility_data;
SELECT diagnosis, COUNT(*) FROM fertility_data GROUP BY diagnosis;
SELECT season, COUNT(*) FROM fertility_data GROUP BY season;
```

---

## 📈 Dashboard Grafana

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

## 🔍 Estrutura do Projeto

```
Lab01_PART2_NUSP/
├── src/
│   ├── ingest_data.py              # 📥 Pipeline de ingestão
│   └── setup_great_expectations.py # ✅ Validação de dados
├── data_raw/
│   └── fertility_1m.csv            # 📊 1M registros brutos
├── data_silver/
│   ├── silver.py                   # 🔄 Transformações
│   ├── relatorio_silver.md         # 📋 Docs
│   └── fertility_silver.parquet     # 📦 Dados agregados
├── data_gold/
│   ├── gold.py                     # 🎯 Análises finais
│   ├── relatorio_gold.md           # 📋 Docs
├── grafana/
│   ├── dashboards/                 # 📈 Painéis
│   └── provisioning/               # ⚙️ Config
├── gx_context/
│   └── data_docs/                  # 📄 Relatório validação
├── docker-compose.yml              # 🐳 Orquestração
├── Dockerfile                      # 🔨 Imagem app
├── pyproject.toml                  # 📦 Dependências modernas
├── requirements.txt                # 📦 Compatibilidade
├── .gitignore                      # 🚫 Git ignore
├── .env.example                    # ⚙️ Exemplo config
└── README.md                       # 📖 Este arquivo
```

---

## 🛠️ Troubleshooting

### Erro: "Connection refused"

```bash
# Verificar se containers estão rodando
docker-compose ps

# Se não estão, iniciar
docker-compose up -d
```

### Erro: "Password authentication failed"

```bash
# Resetar senha do PostgreSQL
docker exec fertility_postgres psql -U postgres -c "ALTER USER postgres WITH PASSWORD 'senha';"
```

### Grafana não mostra dados

```bash
# 1. Verificar datasource
# Admin → Data Sources → PostgreSQL Fertility → Test

# 2. Verificar conexão ao banco
docker exec fertility_postgres psql -U postgres -d fertility_gold -c "SELECT COUNT(*) FROM fertility_data;"

# 3. Atualizar dashboard
python fix_grafana_datasource.py
```

---

## 📝 Requisitos Atendidos

✅ **Estrutura de Código**
- [x] Repositório GitHub público (Lab01_PART2_NUSP)
- [x] Ambiente virtual com .venv/venv
- [x] pyproject.toml + requirements.txt
- [x] .gitignore completo

✅ **Infraestrutura Containerizada**
- [x] PostgreSQL via Docker
- [x] Dockerfile para aplicação
- [x] docker-compose.yml
- [x] Network (fertility_network)

✅ **Qualidade de Dados**
- [x] Great Expectations configurado
- [x] 5 expectativas distintas
- [x] Data Docs (HTML)

✅ **Visualização de Dados**
- [x] Grafana conectado ao PostgreSQL
- [x] 6 visualizações (stat, gauge, pizza, barras, histograma, tabela)

✅ **Documentação**
- [x] README.md completo
- [x] Instruções Docker
- [x] Instruções Great Expectations
- [x] Passo a passo reproduzível

---

**Data**: Março 2026  
**Status**: ✅ Projeto Completo  
**Versão**: 1.0.0

### 3.4 Executar pipeline completo de dados (com validações)
```bash
# Executar main que processa as camadas
.venv\Scripts\python.exe scripts/main

# Ou exportar para PostgreSQL diretamente
.venv\Scripts\python.exe scripts/export_to_postgres.py
```

## 🔧 Troubleshooting

### Erro: "Could not connect to PostgreSQL"
```bash
# Verificar se container está rodando
docker ps | grep fertility_postgres

# Se não estiver, reiniciar
docker-compose -f config/docker-compose.yml restart postgres
```

### Erro: "Great Expectations not found"
```bash
# Reinstalar dependências
.venv\Scripts\python.exe -m pip install great-expectations>=0.17.0
```

### Ver logs do container app
```bash
docker-compose -f config/docker-compose.yml logs -f app
```

### Limpar tudo e começar do zero
```bash
# Parar e remover todos os containers e volumes
docker-compose -f config/docker-compose.yml down -v

# Reconstruir
docker build -f config/Dockerfile -t fertility-app:latest .
docker-compose -f config/docker-compose.yml up -d
```

## 📊 Arquitetura

```
┌─────────────────────────────────────┐
│     Docker Compose                  │
├─────────────────────────────────────┤
│                                     │
│  ┌──────────────┐  ┌────────────┐  │
│  │  PostgreSQL  │  │  Grafana   │  │
│  │   :5432      │  │  :3000     │  │
│  └──────────────┘  └────────────┘  │
│                                     │
│  ┌──────────────────────────────┐  │
│  │  App Container               │  │
│  │  • Raw Data Validation (GX)  │  │
│  │  • Data Processing           │  │
│  │  • Export to PostgreSQL      │  │
│  └──────────────────────────────┘  │
│                                     │
└─────────────────────────────────────┘
```

## 📚 Estrutura de Pastas

```
config/              → Docker, Dockerfile, SQL
scripts/             → Python executáveis
data_raw/            → Dados brutos + validações GX
data_silver/         → Dados processados
data_gold/           → Dados refinados
grafana/             → Dashboards e provisioning
```

## 🎯 Próximos Passos

1. ✅ Construir imagem: `docker build -f config/Dockerfile -t fertility-app:latest .`
2. ✅ Subir containers: `docker-compose -f config/docker-compose.yml up -d`
3. ✅ Validar dados: `.venv\Scripts\python.exe data_raw/validate_raw_data.py`
4. ✅ Acessar Grafana: `http://localhost:3000`

## 📞 Suporte

Para problemas, check:
- Logs dos containers: `docker-compose logs [service_name]`
- Relatórios GX: `data_raw/gx_context/data_docs/index.html`
- Variáveis de ambiente: `.env`
