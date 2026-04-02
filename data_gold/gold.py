#!/usr/bin/env python
# -*- coding: utf-8 -*-
# CAMADA GOLD (BUSINESS/WAREHOUSE)

import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configuração
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)

# 1. CARREGAR DADOS DA CAMADA SILVER

silver_path = Path(__file__).parent.parent / 'data_silver' / 'fertility_silver.parquet'
silver_data = pd.read_parquet(silver_path)
print(silver_data.head())

gold_dir = Path(__file__).parent
gold_dir.mkdir(exist_ok=True)

# 2. CRIAR STAR SCHEMA EM POSTGRESQL

# Configuração da conexão com o banco de dados
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'senha')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'fertility_db')

# String de conexão
DATABASE_URL = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# Conectar a banco de dados PostgreSQL
try:
    engine = create_engine(DATABASE_URL)
    connection = engine.connect()
    print(f"[OK] Conexão estabelecida com PostgreSQL em {DB_HOST}:{DB_PORT}/{DB_NAME}")
    connection.close()
except Exception as e:
    print(f"[ERRO] Falha na conexão com PostgreSQL: {e}")
    raise

# Criar engine para operações
engine = create_engine(DATABASE_URL)

# Criar tabela fato (Fact Table)
fact_table = silver_data.copy()
fact_table.insert(0, 'patient_id', range(1, len(fact_table) + 1))

fact_table.to_sql('fact_fertility', engine, if_exists='replace', index=False, schema='fertility_warehouse')
print(f"[OK] Fact Table criada: {len(fact_table)} registros em fertility_warehouse.fact_fertility")

# Criar dimensões (Dimension Tables)
# Dimensão Idade (binned)
age_dimension = pd.DataFrame({
    'age_id': range(1, len(silver_data['age'].unique()) + 1),
    'age': sorted(silver_data['age'].unique()),
    'age_group': pd.cut(sorted(silver_data['age'].unique()), 
                        bins=[0, 28, 30, 32, 50], 
                        labels=['Young (27-28)', 'Middle (29-30)', 'Senior (31-32)', 'Older (33+)']).astype(str)
})
age_dimension.to_sql('dim_age', engine, if_exists='replace', index=False, schema='fertility_warehouse')

# Dimensão Estação
season_dimension = pd.DataFrame({
    'season_id': range(1, len(silver_data['season'].unique()) + 1),
    'season': silver_data['season'].unique()
})
season_dimension.to_sql('dim_season', engine, if_exists='replace', index=False, schema='fertility_warehouse')

# Dimensão Diagnóstico
diagnosis_dimension = pd.DataFrame({
    'diagnosis_id': range(1, len(silver_data['diagnosis'].unique()) + 1),
    'diagnosis': silver_data['diagnosis'].unique()
})
diagnosis_dimension.to_sql('dim_diagnosis', engine, if_exists='replace', index=False, schema='fertility_warehouse')

print("[OK] Dimensões criadas (Idade, Estação, Diagnóstico)")


# ANÁLISE 1: Taxa de Diagnóstico por Hábito de Fumar


print("ANÁLISE 1: Impacto do Fumo na Fertilidade")

query1 = """
SELECT 
    smoking_habit,
    COUNT(*) as total_patients,
    SUM(CASE WHEN diagnosis = 'Altered' THEN 1 ELSE 0 END) as altered_diagnosis,
    ROUND(100.0 * SUM(CASE WHEN diagnosis = 'Altered' THEN 1 ELSE 0 END) / COUNT(*), 2) as taxa_alteracao_pct
FROM fertility_warehouse.fact_fertility
GROUP BY smoking_habit
ORDER BY taxa_alteracao_pct DESC
"""

result1 = pd.read_sql_query(query1, engine)
print("\n" + result1.to_string(index=False))

# Visualização
fig, ax = plt.subplots(figsize=(10, 6))
result1.set_index('smoking_habit')['taxa_alteracao_pct'].plot(kind='bar', color='salmon', ax=ax)
ax.set_title('Taxa de Diagnóstico Alterado por Hábito de Fumar', fontsize=14, fontweight='bold')
ax.set_ylabel('Taxa de Alteração (%)')
ax.set_xlabel('Hábito de Fumar')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(gold_dir / 'analise1_fumo.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================

# ANÁLISE 2: Correlação entre Sedentarismo e Fertilidade

print("ANÁLISE 2: Impacto do Sedentarismo na Fertilidade")


# Categorizar horas de sedentarismo
silver_data['sedentary_category'] = pd.cut(silver_data['number_of_hours_spent_sitting_per_day'],
                                           bins=[0, 5, 10, 15, 350],
                                           labels=['Baixo (0-5h)', 'Médio (5-10h)', 'Alto (10-15h)', 'Crítico (15+h)'])

query2 = """
WITH sedentary_binned AS (
    SELECT 
        CASE 
            WHEN number_of_hours_spent_sitting_per_day <= 5 THEN 'Baixo (0-5h)'
            WHEN number_of_hours_spent_sitting_per_day <= 10 THEN 'Médio (5-10h)'
            WHEN number_of_hours_spent_sitting_per_day <= 15 THEN 'Alto (10-15h)'
            ELSE 'Crítico (15+h)'
        END as sedentary_category,
        ROUND(AVG(number_of_hours_spent_sitting_per_day), 2) as avg_hours,
        COUNT(*) as total_patients,
        SUM(CASE WHEN diagnosis = 'Altered' THEN 1 ELSE 0 END) as altered_diagnosis,
        ROUND(100.0 * SUM(CASE WHEN diagnosis = 'Altered' THEN 1 ELSE 0 END) / COUNT(*), 2) as taxa_alteracao_pct
    FROM fertility_warehouse.fact_fertility
    GROUP BY sedentary_category
)
SELECT * FROM sedentary_binned
ORDER BY avg_hours
"""

result2 = pd.read_sql_query(query2, engine)
print("\n" + result2.to_string(index=False))

# Visualização
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
result2.set_index('sedentary_category')[['avg_hours']].plot(kind='bar', ax=axes[0], color='steelblue')
axes[0].set_title('Média de Horas Sentado', fontsize=12, fontweight='bold')
axes[0].set_ylabel('Horas/dia')
result2.set_index('sedentary_category')[['taxa_alteracao_pct']].plot(kind='bar', ax=axes[1], color='coral')
axes[1].set_title('Taxa de Diagnóstico Alterado', fontsize=12, fontweight='bold')
axes[1].set_ylabel('Taxa (%)')
plt.tight_layout()
plt.savefig(gold_dir / 'analise2_sedentarismo.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================

# ANÁLISE 3: Sazonalidade e Diagnósticos

print("ANÁLISE 3: Sazonalidade e Diagnósticos de Fertilidade")

query3 = """
SELECT 
    season,
    COUNT(*) as total_patients,
    SUM(CASE WHEN diagnosis = 'Altered' THEN 1 ELSE 0 END) as altered_diagnosis,
    SUM(CASE WHEN diagnosis = 'Normal' THEN 1 ELSE 0 END) as normal_diagnosis,
    ROUND(100.0 * SUM(CASE WHEN diagnosis = 'Altered' THEN 1 ELSE 0 END) / COUNT(*), 2) as taxa_alteracao_pct
FROM fertility_warehouse.fact_fertility
GROUP BY season
ORDER BY taxa_alteracao_pct DESC
"""

result3 = pd.read_sql_query(query3, engine)
print("\n" + result3.to_string(index=False))

# Visualização
fig, ax = plt.subplots(figsize=(10, 6))
x = range(len(result3))
ax.bar(x, result3['normal_diagnosis'], label='Normal', color='green', alpha=0.7)
ax.bar(x, result3['altered_diagnosis'], bottom=result3['normal_diagnosis'], label='Altered', color='red', alpha=0.7)
ax.set_xticks(x)
ax.set_xticklabels(result3['season'], rotation=45)
ax.set_title('Distribuição de Diagnósticos por Estação', fontsize=14, fontweight='bold')
ax.set_ylabel('Número de Pacientes')
ax.legend()
plt.tight_layout()
plt.savefig(gold_dir / 'analise3_sazonalidade.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================

# ANÁLISE 4: Carga Acumulada de Fatores de Risco

print("ANÁLISE 4: Carga Acumulada de Fatores de Risco")

# Calcular score de risco
risk_score = silver_data.copy()
risk_cols = ['childish_diseases', 'accident_or_serious_trauma', 'surgical_intervention', 
             'high_fevers_in_the_last_year', 'frequency_of_alcohol_consumption', 'smoking_habit']

# Contar fatores de risco 
risk_factors = 0
for col in risk_cols:
    if col in ['childish_diseases', 'accident_or_serious_trauma', 'surgical_intervention']:
        risk_score[col + '_risk'] = (risk_score[col] == 'yes').astype(int)
    elif col == 'smoking_habit':
        risk_score[col + '_risk'] = (risk_score[col].isin(['daily', 'occasional'])).astype(int)
    elif col == 'frequency_of_alcohol_consumption':
        risk_score[col + '_risk'] = (risk_score[col].isin(['several times a week', 'once a week'])).astype(int)
    elif col == 'high_fevers_in_the_last_year':
        risk_score[col + '_risk'] = (risk_score[col] != 'more than 3 months ago').astype(int)

risk_cols_new = [col + '_risk' for col in risk_cols]
risk_score['risk_score'] = risk_score[risk_cols_new].sum(axis=1)

query4_data = risk_score.groupby('risk_score').agg({
    'diagnosis': ['count', lambda x: (x == 'Altered').sum()]
}).round(2)
query4_data.columns = ['total_patients', 'altered_diagnosis']
query4_data['taxa_alteracao_pct'] = (query4_data['altered_diagnosis'] / query4_data['total_patients'] * 100).round(2)
query4_data = query4_data.reset_index()
query4_data.columns = ['risk_score', 'total_patients', 'altered_diagnosis', 'taxa_alteracao_pct']

print("\n" + query4_data.to_string(index=False))

# Visualização
fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(query4_data['risk_score'], query4_data['taxa_alteracao_pct'], s=query4_data['total_patients'] * 20, 
          alpha=0.6, color='purple')
ax.set_xlabel('Score de Risco (número de fatores)', fontsize=12, fontweight='bold')
ax.set_ylabel('Taxa de Diagnóstico Alterado (%)', fontsize=12, fontweight='bold')
ax.set_title('Carga Acumulada de Fatores de Risco vs Diagnóstico', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(gold_dir / 'analise4_risco_acumulado.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================

# ANÁLISE 5: Perfil Demográfico de Risco

print("ANÁLISE 5: Perfil Demográfico de Risco")

query5 = """
SELECT 
    CASE 
        WHEN age <= 28 THEN '27-28'
        WHEN age <= 30 THEN '29-30'
        WHEN age <= 32 THEN '31-32'
        ELSE '33-36'
    END as age_group,
    COUNT(*) as total_patients,
    SUM(CASE WHEN diagnosis = 'Altered' THEN 1 ELSE 0 END) as altered_diagnosis,
    ROUND(100.0 * SUM(CASE WHEN diagnosis = 'Altered' THEN 1 ELSE 0 END) / COUNT(*), 2) as taxa_alteracao_pct,
    ROUND(AVG(CASE WHEN smoking_habit IN ('daily', 'occasional') THEN 1 ELSE 0 END) * 100, 1) as pct_fumantes,
    ROUND(AVG(CASE WHEN childish_diseases = 'yes' THEN 1 ELSE 0 END) * 100, 1) as pct_dencas_infantis,
    ROUND(AVG(CASE WHEN surgical_intervention = 'yes' THEN 1 ELSE 0 END) * 100, 1) as pct_cirurgias
FROM fertility_warehouse.fact_fertility
GROUP BY age_group
ORDER BY age_group
"""

result5 = pd.read_sql_query(query5, engine)
print("\n" + result5.to_string(index=False))

# Visualização
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Taxa de alteração por grupo etário
axes[0, 0].bar(result5['age_group'], result5['taxa_alteracao_pct'], color='darkred', alpha=0.7)
axes[0, 0].set_title('Taxa de Diagnóstico Alterado por Faixa Etária', fontweight='bold')
axes[0, 0].set_ylabel('Taxa (%)')

# Proporção de fumantes
axes[0, 1].bar(result5['age_group'], result5['pct_fumantes'], color='orange', alpha=0.7)
axes[0, 1].set_title('% de Fumantes por Faixa Etária', fontweight='bold')
axes[0, 1].set_ylabel('%')

# Proporção de doenças infantis
axes[1, 0].bar(result5['age_group'], result5['pct_dencas_infantis'], color='skyblue', alpha=0.7)
axes[1, 0].set_title('% com Histórico de Doenças Infantis', fontweight='bold')
axes[1, 0].set_ylabel('%')

# Proporção de cirurgias
axes[1, 1].bar(result5['age_group'], result5['pct_cirurgias'], color='lightgreen', alpha=0.7)
axes[1, 1].set_title('% com Histórico de Cirurgias', fontweight='bold')
axes[1, 1].set_ylabel('%')

plt.tight_layout()
plt.savefig(gold_dir / 'analise5_perfil_demografico.png', dpi=300, bbox_inches='tight')
plt.close()

engine.dispose()
