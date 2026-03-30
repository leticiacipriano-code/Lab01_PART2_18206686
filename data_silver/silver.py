#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Camadas de Dados (Medallion Architecture)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'data_raw'))
from raw import raw_data

print(raw_data.head())

# CAMADA SILVER (TRATAMENTO)

# 1. RELATÓRIO BÁSICO

print("RELATÓRIO BÁSICO - CAMADA SILVER")

# Contagem de nulos
print("\n1. CONTAGEM DE NULOS:")
print(raw_data.isnull().sum())

# Tipos de dados
print("\n2. TIPOS DE DADOS:")
print(raw_data.dtypes)

# Estatísticas descritivas
print("\n3. ESTATÍSTICAS DESCRITIVAS:")
print(raw_data.describe())

# Duplicatas
print(f"\n4. DUPLICATAS: {raw_data.duplicated().sum()} linhas duplicadas")

# 2. PADRONIZAÇÃO DE NOMES DE COLUNAS (snake_case)
silver_data = raw_data.copy()
silver_data.columns = [col.lower().replace(' ', '_').replace('_per_', '_per_').replace('_of_', '_of_')
                       for col in silver_data.columns]
print(f"\n Nomes de colunas padronizados para snake_case")
print(f"Colunas: {list(silver_data.columns)}")

# 3. TRATAMENTO DE VALORES AUSENTES
silver_data = silver_data.dropna()  

# 4. REMOÇÃO DE DUPLICATAS
# etapa removida pois não faz muito sentido remover duplicatas nesse tipo de dataset

# 5. CONVERSÃO DE TIPOS (identificar e converter)
# Converter colunas categóricas para categoria
categorical_cols = ['season', 'childish_diseases', 'accident_or_serious_trauma', 
                    'surgical_intervention', 'high_fevers_in_the_last_year', 
                    'frequency_of_alcohol_consumption', 'smoking_habit', 'diagnosis']
for col in categorical_cols:
    if col in silver_data.columns:
        silver_data[col] = silver_data[col].astype('category')


print(f"\nDados limpos - Shape final: {silver_data.shape}")

# 6. GRÁFICOS E RELATÓRIO MARKDOWN

# Criar figura com subplots
fig = plt.figure(figsize=(16, 12))

# Gráfico 1: Distribuição de Idade(Age)
ax1 = plt.subplot(2, 3, 1)
silver_data['age'].hist(bins=20, color='skyblue', edgecolor='black')
ax1.set_title('Distribuição de Idade', fontsize=12, fontweight='bold')
ax1.set_xlabel('Idade')
ax1.set_ylabel('Frequência')

# Gráfico 2: Contagem de Diagnósticos (Diagnosis)
ax2 = plt.subplot(2, 3, 2)
diagnosis_counts = silver_data['diagnosis'].value_counts()
diagnosis_counts.plot(kind='bar', color=['green', 'red'], ax=ax2)
ax2.set_title('Contagem de Diagnósticos', fontsize=12, fontweight='bold')
ax2.set_xlabel('Diagnóstico')
ax2.set_ylabel('Contagem')
ax2.tick_params(axis='x', rotation=0)

# Gráfico 3: Distribuição por Estação
ax3 = plt.subplot(2, 3, 3)
season_counts = silver_data['season'].value_counts()
season_counts.plot(kind='pie', autopct='%1.1f%%', ax=ax3, colors=['lightcoral', 'lightyellow', 'lightgreen', 'lightblue'])
ax3.set_title('Distribuição por Estação', fontsize=12, fontweight='bold')
ax3.set_ylabel('')

# Gráfico 4: Horas sentado por dia
ax4 = plt.subplot(2, 3, 4)
silver_data['number_of_hours_spent_sitting_per_day'].hist(bins=10, color='orange', edgecolor='black')
ax4.set_title('Distribuição de Horas Sentado/Dia', fontsize=12, fontweight='bold')
ax4.set_xlabel('Horas')
ax4.set_ylabel('Frequência')

# Gráfico 5: Idade vs Diagnósticos
ax5 = plt.subplot(2, 3, 5)
silver_data.boxplot(column='age', by='diagnosis', ax=ax5)
ax5.set_title('Idade por Diagnóstico', fontsize=12, fontweight='bold')
ax5.set_xlabel('Diagnóstico')
ax5.set_ylabel('Idade')
plt.sca(ax5)
plt.xticks(rotation=0)

# Gráfico 6: Hábito de fumar
ax6 = plt.subplot(2, 3, 6)
smoking_counts = silver_data['smoking_habit'].value_counts()
smoking_counts.plot(kind='barh', color='salmon', ax=ax6)
ax6.set_title('Hábito de Fumar', fontsize=12, fontweight='bold')
ax6.set_xlabel('Contagem')

plt.tight_layout()
silver_dir = Path(__file__).parent
silver_dir.mkdir(exist_ok=True)
graficos_path = silver_dir / 'graficos_silver.png'
plt.savefig(graficos_path, dpi=300, bbox_inches='tight')
print(f"Gráficos salvos em {graficos_path}")
plt.close()

# 7. PERSISTÊNCIA - SALVAR EM PARQUET
parquet_path = silver_dir / 'fertility_silver.parquet'
silver_data.to_parquet(parquet_path, index=False)

