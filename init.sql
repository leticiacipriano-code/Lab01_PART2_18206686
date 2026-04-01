-- Script de inicialização do banco de dados PostgreSQL
-- Cria schemas e tabelas para o pipeline de dados Fertility

-- Criar schema para organizar as tabelas
CREATE SCHEMA IF NOT EXISTS fertility_warehouse;

-- Tabelas de contexto (Dimension Tables)
CREATE TABLE IF NOT EXISTS fertility_warehouse.dim_age (
    age_id SERIAL PRIMARY KEY,
    age INT NOT NULL UNIQUE,
    age_group VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS fertility_warehouse.dim_season (
    season_id SERIAL PRIMARY KEY,
    season VARCHAR(50) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS fertility_warehouse.dim_diagnosis (
    diagnosis_id SERIAL PRIMARY KEY,
    diagnosis VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de fatos (Fact Table)
CREATE TABLE IF NOT EXISTS fertility_warehouse.fact_fertility (
    patient_id SERIAL PRIMARY KEY,
    age INT NOT NULL,
    season VARCHAR(50),
    childrens_count VARCHAR(50),
    childish_diseases VARCHAR(50),
    accident_or_serious_trauma VARCHAR(50),
    surgical_intervention VARCHAR(50),
    high_fevers_in_the_last_year VARCHAR(50),
    frequency_of_alcohol_consumption VARCHAR(50),
    smoking_habit VARCHAR(50),
    number_of_hours_spent_sitting_per_day INT,
    diagnosis VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para melhorar performance
CREATE INDEX idx_fact_fertility_diagnosis ON fertility_warehouse.fact_fertility(diagnosis);
CREATE INDEX idx_fact_fertility_season ON fertility_warehouse.fact_fertility(season);
CREATE INDEX idx_fact_fertility_smoking ON fertility_warehouse.fact_fertility(smoking_habit);
CREATE INDEX idx_fact_fertility_age ON fertility_warehouse.fact_fertility(age);

-- Tabela de logs de execução
CREATE TABLE IF NOT EXISTS fertility_warehouse.execution_logs (
    log_id SERIAL PRIMARY KEY,
    job_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL,
    records_processed INT,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Grant permissões ao usuário postgres
GRANT ALL PRIVILEGES ON SCHEMA fertility_warehouse TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA fertility_warehouse TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA fertility_warehouse TO postgres;
