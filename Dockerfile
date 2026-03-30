# Dockerfile para aplicação Python de pipeline de dados Fertility

FROM python:3.11-slim

# Define diretório de trabalho
WORKDIR /app

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Instala dependências do sistema necessárias para psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements.txt e instala dependências Python
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copia o código da aplicação
COPY . .

# Define o comando de entrada
CMD ["python", "main"]
