# 🏗️ Arquitetura Docker - Pipeline Fertility

## Diagrama de Rede e Containers

```
┌────────────────────────────────────────────────────────────────┐
│                    HOST (Windows/Linux/MacOS)                    │
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │         Docker Network: fertility_network (bridge)          │  │
│  │                                                              │  │
│  │  ┌──────────────────────────┐  ┌──────────────────────────┐ │  │
│  │  │  Container: fertility_app │  │ Container: pregnancy_pg  │ │  │
│  │  │                            │  │                          │ │  │
│  │  │ ┌────────────────────────┐ │  │ ┌──────────────────────┐ │ │  │
│  │  │ │  Python 3.11           │ │  │ │ PostgreSQL 16        │ │ │  │
│  │  │ │  ├─ raw.py             │ │  │ │ ├─ fertility_db      │ │ │  │
│  │  │ │  ├─ silver.py          │ │  │ │ ├─ port: 5432       │ │ │  │
│  │  │ │  └─ gold.py            │ │  │ │ ├─ user: postgres   │ │ │  │
│  │  │ │                         │ │  │ │ └─ data: /var/lib/  │ │ │  │
│  │  │ │ Ambiente:              │ │  │ │    postgresql/data  │ │ │  │
│  │  │ │ • DB_HOST=postgres     │ │  │ │                      │ │ │  │
│  │  │ │ • DB_PORT=5432         │ │  │ │ Volumes:            │ │ │  │
│  │  │ │ • DB_NAME=fertility_db  │ │  │ │ • postgres_data     │ │ │  │
│  │  │ └────────────────────────┘ │  │ │ • init.sql (init)   │ │ │  │
│  │  │                             │  │ └──────────────────────┘ │ │  │
│  │  │ Volumes:                    │  │                          │ │  │
│  │  │ • .:/app                    │  │                          │ │  │
│  │  │ • __pycache__ (local)       │  │                          │ │  │
│  │  └──────────────────────────┘  │  └──────────────────────────┘ │  │
│  │           │                               │                      │  │
│  │           │ connect string               │                      │  │
│  │           └───────────────────────────────┘                      │  │
│  │                                                                  │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  Mapeamento de Portas (Host → Container):                           │
│  • APP: Sem mapeamento (interno)                                   │
│  • PG:  5432:5432 (acesso externo ao banco)                       │
│                                                                      │
└────────────────────────────────────────────────────────────────┘
```

## Fluxo de Dados

```
┌─────────────────────────────────────────────────────────────┐
│                  DADOS FLUEM DA SEGUINTE FORMA               │
└─────────────────────────────────────────────────────────────┘

CSV (1M registros)
   ↓
fertility_1m.csv (data_raw/)
   ↓
raw.py (Container: fertility_app)
   ╰─→ Lê CSV, carrega em memória
   ├─→ Transforma dados brutos
   ├─→ Output: variável raw_data
   ↓
silver.py (Container: fertility_app)
   ├─→ Limpa e padroniza
   ├─→ Remove duplicatas/nulos
   ├─→ Converte tipos de dados
   ╰─→ Output: fertility_silver.parquet
   ↓
gold.py (Container: fertility_app)
   ├─→ Cria schema Star em PostgreSQL
   ├─→ Conecta via "postgres:5432" (DNS interno)
   ├─→ Carrega dados no container fertility_postgres
   ├─→ Cria tabelas: fact_fertility, dim_*
   ├─→ Cria índices para performance
   ╰─→ Output: Dados em PostgreSQL
   ↓
Análises & Gráficos
   ├─→ Query SQL no PostgreSQL
   ├─→ Matplotlib visualizations
   └─→ Relatórios em markdown
```

## Configuração da Rede

### Como os containers se comunicam?

#### **Resolução de DNS**

```
Container A                 Container B
(fertility_app)            (fertility_postgres)
   │                              │
   │  "postgres:5432"             │
   │  ─────────────────────────→  │
   │  (Docker DNS resolve)        │
   │                              │
   └──────────────────────────────┘
```

- **Nome do serviço:** `postgres` (definido em docker-compose.yml)
- **Porta interna:** `5432` (padrão PostgreSQL)
- **Rede:** `fertility_network` (bridge)

### Porta Mapping

| Serviço | Porta Interna | Porta Externa (Host) | Acessível de |
|---------|---------------|----------------------|--------------|
| PostgreSQL | 5432 | 5432 | Host + Network |
| App Python | N/A (interno) | N/A | Apenas internal network |

---

## Arquivos de Configuração

### 📄 `docker-compose.yml`

Define dois serviços:

1. **postgres** (image: `postgres:16-alpine`)
   - Ambiente: DB_USER, DB_PASSWORD, DB_NAME
   - Volumes:
     - `postgres_data:/var/lib/postgresql/data` (persistência)
     - `init.sql:/docker-entrypoint-initdb.d/init.sql` (inicialização)
   - Healthcheck: verifica se está pronto
   - Network: `fertility_network`

2. **app** (build: `.`)
   - Build: Dockerfile (Python 3.11)
   - Depends_on: postgres (service_healthy)
   - Ambiente: DB_HOST=postgres (nome do serviço)
   - Volumes: código hotreload
   - Network: `fertility_network`

### 💾 `init.sql`

Executado automaticamente quando o container PostgreSQL inicia:

```sql
-- Cria schema
CREATE SCHEMA IF NOT EXISTS fertility_warehouse;

-- Cria tabelas (dim_age, dim_season, dim_diagnosis)
CREATE TABLE IF NOT EXISTS fertility_warehouse.dim_age (...)

-- Cria fact table
CREATE TABLE IF NOT EXISTS fertility_warehouse.fact_fertility (...)

-- Cria índices para performance
CREATE INDEX idx_fact_fertility_diagnosis ON ...
```

### 🔒 `.env`

Variáveis de ambiente (NÃO commitar em Git com dados sensíveis):

```env
DB_USER=postgres
DB_PASSWORD=senha
DB_NAME=fertility_db
```

---

## Ciclo de Vida dos Containers

### 1. **Build**

```
Dockerfile
   ├─ FROM python:3.11-slim
   ├─ WORKDIR /app
   ├─ COPY requirements.txt
   ├─ RUN pip install
   └─ COPY . .
      ↓
   Imagem: lab1-a:latest
```

### 2. **Up (docker-compose up -d)**

```
Step 1: Criar network "fertility_network" (bridge)
Step 2: Criar volume "postgres_data"
Step 3: Iniciar postgres container
   ├─ Executar init.sql (criar schema e tabelas)
   ├─ Healthcheck até passar
   └─ Pronto em 10-15 segundos
Step 4: Iniciar app container
   ├─ Aguardar postgres estar healthy
   ├─ Executar "python main"
   └─ Conectar em "postgres:5432"
Step 5: Ambos em execução e comunicando
```

### 3. **Down (docker-compose down)**

```
Step 1: Parar containers
Step 2: Remover containers
Step 3: Manter volumes (dados persistem)
        ↓ (use -v para remover tudo)
```

---

## Persistência de Dados

### Volume: `postgres_data`

```
┌────────────────────────┐
│   postgres_data        │
│   (Docker Volume)      │
├────────────────────────┤
│ /var/lib/postgresql/   │
│ data/                  │
│ ├─ pg_wal/             │
│ ├─ global/             │
│ ├─ base/               │
│ └─ postgresql.conf     │
└────────────────────────┘
      ↑
      │ (mapeado em container)
      │
   PostgreSQL Container
```

**Dados SOBREVIVEM:**
- `docker-compose restart`
- `docker-compose stop/start`
- Reboot da máquina

**Dados são PERDIDOS:**
- `docker-compose down -v` (remove volumes)
- `docker volume rm` manual

---

## Health Checks

### PostgreSQL

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
  interval: 10s
  timeout: 5s
  retries: 5
```

- **Estado inicial:** starting
- **Após 10-15s:** healthy (ou unhealthy se falhar)
- **App aguarda:** until healthy antes de conectar

---

## Monitoramento

### Verificar Containers

```bash
docker-compose ps

# Output:
# NAME              COMMAND             STATUS
# fertility_app     python main         Up
# fertility_postgres postgres           Up (healthy)
```

### Ver Logs

```bash
# App
docker-compose logs app

# PostgreSQL
docker-compose logs postgres

# Ambos, seguindo (-f):
docker-compose logs -f
```

### Executar Comandos

```bash
# PostgreSQL CLI
docker-compose exec postgres psql -U postgres

# Ver variáveis de ambiente do app
docker-compose exec app env | grep DB_

# Verificar conectividade
docker-compose exec app ping postgres
```

---

## Troubleshooting Arquitetura

### ❌ "Cannot connect to postgres"

**Causa:** App conecta antes do PostgreSQL estar ready

```
✅ Solução: healthcheck garante isso
   depends_on:
     postgres:
       condition: service_healthy
```

### ❌ "No such file or directory: init.sql"

**Causa:** Arquivo não encontrado no contexto de build

```
✅ Solução: Certifique-se que init.sql está no diretório raiz
```

### ❌ "bind: port already in use"

**Causa:** Porta 5432 já está ocupada

```bash
# Ver quem está usando
netstat -ano | findstr :5432

# Mudar no docker-compose.yml:
ports:
  - "5433:5432"  # External:Internal
```

---

## 🎯 Resumo

| Aspecto | Detalhe |
|--------|---------|
| **Rede** | Bridge network `fertility_network` |
| **DNS** | Container postgres acessível via nome |
| **Porta DB** | 5432 (interna) → 5432 (host) |
| **Inicialização** | init.sql cria schema e tabelas |
| **Persistência** | Volume `postgres_data` mantém dados |
| **Dependências** | App aguarda PostgreSQL estar healthy |
| **Variáveis** | .env fornece credenciais |
| **Comunicação** | SQLAlchemy via `postgresql://postgres:senha@postgres:5432/fertility_db` |

---

Próximo passo: `docker-compose up -d` 🚀
