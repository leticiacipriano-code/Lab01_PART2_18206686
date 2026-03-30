## 🏗️ ARQUITETURA - Grafana + PostgreSQL

```
┌──────────────────────────────────────────────────────────────┐
│                     CAMADA DE APRESENTAÇÃO                   │
│                         (Visualização)                       │
│                                                              │
│              ┌─────────────────────────────────┐            │
│              │      GRAFANA DASHBOARD          │            │
│              │   (http://localhost:3000)       │            │
│              │                                 │            │
│              │  ┌──────────────────────────┐   │            │
│              │  │ 1. Idade (Linha)        │   │            │
│              │  │ 2. Dados por Idade      │   │            │
│              │  │ 3. Estação (Pizza)      │   │            │
│              │  │ 4. Total Records (Stat) │   │            │
│              │  │ 5. Idades Únicas (Stat) │   │            │
│              │  └──────────────────────────┘   │            │
│              └─────────────────────────────────┘            │
│                              ▲                               │
└──────────────────────────────┼───────────────────────────────┘
                               │ SQL Queries
                               │ (via PostgreSQL Datasource)
                               │
┌──────────────────────────────┼───────────────────────────────┐
│                              │                               │
│            CAMADA DE APLICAÇÃO (Lógica)                      │
│                              │                               │
│        ┌─────────────────────┴────────────────────┐         │
│        │   export_to_postgres.py (Script Python)  │         │
│        │  ❶ conecta ao PostgreSQL                │         │
│        │  ❷ cria tabela fertility_data           │         │
│        │  ❸ importa dados do CSV                 │         │
│        │  ❹ cria índices                         │         │
│        └─────────────────────┬────────────────────┘         │
│                              │                               │
└──────────────────────────────┼───────────────────────────────┘
                               │
                               │ INSERT/SELECT
                               │
┌──────────────────────────────┼───────────────────────────────┐
│                              ▼                               │
│            CAMADA DE DADOS (Armazenamento)                   │
│                                                              │
│    ┌───────────────────────────────────────────────┐         │
│    │      PostgreSQL (Docker Container)            │         │
│    │      localhost:5432                           │         │
│    │                                               │         │
│    │  ┌─────────────────────────────────────────┐ │         │
│    │  │  Banco: fertility_db                    │ │         │
│    │  │                                         │ │         │
│    │  │  ┌─────────────────────────────────┐  │ │         │
│    │  │  │ fertility_data (Tabela)        │  │ │         │
│    │  │  │                                 │  │ │         │
│    │  │  │ Colunas:                        │  │ │         │
│    │  │  │ • age                           │  │ │         │
│    │  │  │ • season                        │  │ │         │
│    │  │  │ • education                     │  │ │         │
│    │  │  │ • fertility_score               │  │ │         │
│    │  │  │ • diagnosis                     │  │ │         │
│    │  │  │ • ... (10+ colunas)             │  │ │         │
│    │  │  │                                 │  │ │         │
│    │  │  │ Índices:                        │  │ │         │
│    │  │  │ • idx_age                       │  │ │         │
│    │  │  │ • idx_season                    │  │ │         │
│    │  │  │ • idx_diagnosis                 │  │ │         │
│    │  │  │ • idx_education                 │  │ │         │
│    │  │  └─────────────────────────────────┘  │ │         │
│    │  └─────────────────────────────────────────┘ │         │
│    └───────────────────────────────────────────────┘         │
│                                                              │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                    CAMADA RAW (Origem)                       │
│                                                              │
│    ┌──────────────────────────────────────────────┐         │
│    │  fertility_1m.csv (1.000.000 linhas)         │         │
│    │  (lido pelo export_to_postgres.py)          │         │
│    └──────────────────────────────────────────────┘         │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 🔄 FLUXO DE DADOS

```
1. ORIGEM
   └─ fertility_1m.csv (data_raw/)

2. PROCESSAMENTO
   └─ export_to_postgres.py
      ├─ Lê CSV com pandas
      ├─ Conecta ao PostgreSQL
      ├─ Cria tabela fertility_data
      ├─ Normaliza nomes de colunas
      └─ Insere dados em batch

3. ARMAZENAMENTO
   └─ PostgreSQL (Docker)
      ├─ Banco: fertility_db
      ├─ Tabela: fertility_data
      ├─ Índices: otimizados
      └─ Query: otimizadas

4. VISUALIZAÇÃO
   └─ Grafana Dashboard
      ├─ Datasource: PostgreSQL
      ├─ Queries: SQL executadas
      ├─ Refresh: a cada 30s
      └─ Visualizações: 5 tipos

5. ANÁLISE
   └─ Usuário
      ├─ Explora dashboards
      ├─ Cria alertas
      ├─ Exporta relatórios
      └─ Toma decisões
```

---

## 🐳 DOCKER COMPOSE ESTRUTURA

```
Service: postgres:16-alpine
├─ Container: fertility_postgres
├─ Port: 5432:5432
├─ Volume: postgres_data
├─ Network: fertility_network
└─ Healthcheck: ✓

Service: app (Python)
├─ Container: fertility_app
├─ Depends on: postgres
├─ Volume: .:/app
└─ Network: fertility_network

Service: grafana:latest ⭐ NOVO
├─ Container: fertility_grafana
├─ Port: 3000:3000
├─ Volume: grafana_data + provisioning
├─ Network: fertility_network
└─ Healthcheck: ✓

Network: fertility_network
├─ postgres
├─ app
└─ grafana (comunicam entre si)

Volumes:
├─ postgres_data (BD)
└─ grafana_data (Dashboards)
```

---

## 📊 DASHBOARD JSON ESTRUTURA

```
Dashboard: fertility-dashboard (5 Panels)
│
├─ Panel 1: Distribuição por Idade
│  ├─ Type: timeseries (gráfico de linha)
│  ├─ Query: GROUP BY age + COUNT(*)
│  └─ Refresh: 30s
│
├─ Panel 2: Dados por Idade
│  ├─ Type: table
│  ├─ Query: TOP 20 + AVG(fertility_score)
│  └─ Colunas: age, total_records, avg_score
│
├─ Panel 3: Distribuição por Estação
│  ├─ Type: piechart
│  ├─ Query: GROUP BY season + COUNT(%)
│  └─ Legend: Right (displayMode: table)
│
├─ Panel 4: Total de Registros
│  ├─ Type: stat
│  ├─ Query: COUNT(*)
│  └─ Format: number
│
└─ Panel 5: Idades Únicas
   ├─ Type: stat
   ├─ Query: COUNT(DISTINCT age)
   └─ Format: number
```

---

## 🔐 SEGURANÇA

```
┌─────────────────────────────────────────┐
│      PostgreSQL (Dentro do Docker)      │
│                                         │
│  User: fertility_user                   │
│  Password: fertility_password (no .env) │
│  Database: fertility_db                 │
│  Port: 5432 (internal)                  │
│                                         │
│  Grafana Server: http://localhost:3000 │
│  Grafana Admin: admin/admin             │
│                                         │
└─────────────────────────────────────────┘

⚠️ MUDAR na primeira vez:
   1. Grafana password (Avatar → Change)
   2. PostgreSQL password (ALTER USER)
   3. Criar usuário específico para Grafana
```

---

## 📝 PROVISIONING AUTOMÁTICO

```
Quando Grafana inicia:

1. LÊ: grafana/provisioning/datasources/postgresql.yaml
   └─ Cria datasource PostgreSQL automaticamente

2. LÊ: grafana/provisioning/dashboards/dashboards.yaml
   └─ Aponta para grafana/dashboards/

3. LÊ: grafana/dashboards/fertility-dashboard.json
   └─ Importa dashboard automaticamente

Result: ZERO configuração manual!
```

---

## 📈 PERFORMANCE

```
Connect Time: < 1s
Query Time: < 500ms (com índices)
Dashboard Load: < 2s
Refresh Interval: 30s

Índices criados:
├─ idx_fertility_data_age ........... rápida por idade
├─ idx_fertility_data_season ........ rápida por estação
├─ idx_fertility_data_diagnosis ..... rápida por diagnóstico
└─ idx_fertility_data_education ..... rápida por educação
```

---

## 🗂️ ARQUIVOS & RESPONSABILIDADES

```
fertility_1m.csv
    │ → read by
    ▼
export_to_postgres.py
    │ → INSERT INTO
    ▼
PostgreSQL
    │ ◄ SELECT by
    ▼
postgresql.yaml (datasource)
    │ → register in
    ▼
Grafana
    │ ◄ display from
    ▼
fertility-dashboard.json
    │ → render
    ▼
Browser (http://localhost:3000)
```

---

**Arquitetura completa pronta para análise de dados!** 📊
