#!/usr/bin/env python3
"""
Script de ingestão principal: carrega dados de fertility_1m.csv para PostgreSQL.

Este script:
1. Carrega dados do CSV
2. Valida qualidade com Great Expectations
3. Insere em batches no PostgreSQL
4. Verifica integridade final
"""

import os
import sys
import pandas as pd
import psycopg
from pathlib import Path
from dotenv import load_dotenv

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from setup_great_expectations import setup_great_expectations


def ingest_fertility_data():
    """Executa pipeline de ingestão completo."""
    
    print("\n" + "=" * 70)
    print(" PIPELINE DE INGESTÃO - FERTILITY DATA")
    print("=" * 70)
    
    # 1. Carregar variáveis de ambiente
    print("\n Carregando configurações...")
    load_dotenv()
    
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = int(os.getenv("DB_PORT", "5432"))
    db_user = os.getenv("DB_USER", "postgres")
    db_pass = os.getenv("DB_PASSWORD", "senha")
    db_name = os.getenv("DB_NAME", "fertility_db")
    
    print(f"  Banco de dados: {db_user}@{db_host}:{db_port}/{db_name}")
    
    project_root = Path(__file__).parent.parent
    csv_path = project_root / "data_raw" / "fertility_1m.csv"
    
    # 2. Validar dados com Great Expectations
    print("\n Validando dados com Great Expectations...")
    setup_great_expectations()
    
    # 3. Carregar dados
    print("\n Carregando dados do CSV...")
    try:
        df = pd.read_csv(csv_path)
        print(f"   {len(df):,} registros carregados")
        print(f"   Colunas: {list(df.columns)}")
    except Exception as e:
        print(f"   Erro ao carregar CSV: {e}")
        return
    
    # 4. Conectar ao PostgreSQL
    print(f"\n Conectando ao PostgreSQL ({db_host}:{db_port})...")
    try:
        conn = psycopg.connect(
            host=db_host,
            port=db_port,
            dbname=db_name,
            user=db_user,
            password=db_pass
        )
        cur = conn.cursor()
        print("   Conexão estabelecida")
    except Exception as e:
        print(f"   Erro ao conectar: {e}")
        return
    
    # 5. Criar tabela se não existir
    print("\n  Preparando tabela no banco de dados...")
    try:
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS fertility_data (
            id SERIAL PRIMARY KEY,
            season VARCHAR(50),
            age INT,
            childish_diseases VARCHAR(50),
            accident_or_serious_trauma VARCHAR(50),
            surgical_intervention VARCHAR(50),
            high_fevers_in_the_last_year VARCHAR(50),
            frequency_of_alcohol_consumption VARCHAR(50),
            smoking_habit VARCHAR(50),
            number_of_hours_spent_sitting_per_day INT,
            diagnosis VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        cur.execute(create_table_sql)
        conn.commit()
        print("   Tabela criada ou já existe")
    except Exception as e:
        print(f"  Erro ao criar tabela: {e}")
        conn.close()
        return
    
    # 6. Verificar dados existentes
    print("\n  Verificando dados existentes...")
    try:
        cur.execute("SELECT COUNT(*) FROM fertility_data")
        existing_count = cur.fetchone()[0]
        print(f"   Registros existentes: {existing_count:,}")
        
        if existing_count > 0:
            print("    Dados já existem no banco. Pulando ingestão.")
            # Apenas validar
            cur.execute("SELECT COUNT(DISTINCT diagnosis) FROM fertility_data")
            diagnoses = cur.fetchone()[0]
            print(f"  Diagnósticos únicos: {diagnoses}")
            conn.close()
            return
    except Exception as e:
        print(f"   Erro ao verificar: {e}")
    
    # 7. Inserir dados em batches
    print(f"\n Inserindo {len(df):,} registros em batches...")
    batch_size = 10000
    total_batches = (len(df) + batch_size - 1) // batch_size
    
    try:
        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(df))
            batch_df = df.iloc[start_idx:end_idx]
            
            # Preparar dados
            values = []
            for _, row in batch_df.iterrows():
                values.append((
                    row.get('season', ''),
                    int(row.get('age', 0)),
                    row.get('childish_diseases', ''),
                    row.get('accident_or_serious_trauma', ''),
                    row.get('surgical_intervention', ''),
                    row.get('high_fevers_in_the_last_year', ''),
                    row.get('frequency_of_alcohol_consumption', ''),
                    row.get('smoking_habit', ''),
                    int(row.get('number_of_hours_spent_sitting_per_day', 0)),
                    row.get('diagnosis', '')
                ))
            
            # Inserir batch
            insert_sql = """
            INSERT INTO fertility_data 
            (season, age, childish_diseases, accident_or_serious_trauma,
             surgical_intervention, high_fevers_in_the_last_year,
             frequency_of_alcohol_consumption, smoking_habit,
             number_of_hours_spent_sitting_per_day, diagnosis)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cur.executemany(insert_sql, values)
            conn.commit()
            
            progress = ((batch_num + 1) / total_batches) * 100
            print(f"   [{batch_num + 1}/{total_batches}] {progress:.1f}% "
                  f"({(batch_num + 1) * batch_size:,} registros)")
        
        print("   Ingestão completa!")
        
    except Exception as e:
        print(f"  Erro durante ingestão: {e}")
        conn.rollback()
        conn.close()
        return
    
    # 8. Verificar integridade
    print("\n  Verificando integridade dos dados...")
    try:
        cur.execute("SELECT COUNT(*) FROM fertility_data")
        total_count = cur.fetchone()[0]
        
        cur.execute("SELECT diagnosis, COUNT(*) FROM fertility_data GROUP BY diagnosis")
        diagnoses = cur.fetchall()
        
        cur.execute("SELECT season, COUNT(*) FROM fertility_data GROUP BY season")
        seasons = cur.fetchall()
        
        print(f"   Total de registros: {total_count:,}")
        print(f"   Diagnósticos:")
        for diag, count in diagnoses:
            print(f"      - {diag}: {count:,}")
        print(f"   Estações:")
        for season, count in seasons:
            print(f"      - {season}: {count:,}")
        
    except Exception as e:
        print(f"   Erro ao verificar: {e}")
    
    conn.close()
    
    print("\n" + "=" * 70)
    print(" PIPELINE CONCLUÍDO COM SUCESSO!")
    print("=" * 70)
    print("\n Próximos passos:")
    print("   1. Visualizar dados em: http://localhost:3000")
    print("   2. Revisar validações em: gx_context/data_docs/index.html")


if __name__ == "__main__":
    ingest_fertility_data()
