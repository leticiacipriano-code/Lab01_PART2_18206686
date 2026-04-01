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
import time
import pandas as pd
import psycopg
from pathlib import Path
from dotenv import load_dotenv

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from setup_great_expectations import setup_great_expectations


def wait_for_postgres(db_host, db_port, db_user, db_pass, db_name=None, max_retries=30):
    """Aguarda PostgreSQL estar pronto para aceitar conexoes."""
    for attempt in range(max_retries):
        try:
            if db_name is None:
                conn = psycopg.connect(
                    host=db_host, port=db_port, user=db_user, password=db_pass,
                    connect_timeout=5, dbname="postgres"
                )
            else:
                conn = psycopg.connect(
                    host=db_host, port=db_port, user=db_user, password=db_pass,
                    connect_timeout=5, dbname=db_name
                )
            conn.close()
            print(f"   OK PostgreSQL pronto")
            return True
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"   Tentativa {attempt + 1}/{max_retries}...")
                time.sleep(1)
            else:
                print(f"   ERRO: {e}")
    return False


def ingest_fertility_data():
    """Executa pipeline de ingestão completo."""
    
    print("\n" + "=" * 70)
    print(" PIPELINE DE INGESTÃO - FERTILITY DATA")
    print("=" * 70)
    
    # 1. Carregar variaveis de ambiente (NAO sobrescrever ja definidas)
    print("\n Carregando configuracoes...")
    load_dotenv(override=False)  # Respeita variaveis ja definidas pelo docker-compose
    
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = int(os.getenv("DB_PORT", "5432"))
    db_user = os.getenv("DB_USER", "postgres")
    db_pass = os.getenv("DB_PASSWORD", "senha")
    db_name = os.getenv("DB_NAME", "fertility_db")
    
    print(f"  Banco de dados: {db_user}@{db_host}:{db_port}/{db_name}")
    
    project_root = Path(__file__).parent.parent
    csv_path = project_root / "data_raw" / "fertility_1m.csv"
    
    # 2. Aguardar PostgreSQL estar pronto
    print("\n Aguardando PostgreSQL estar pronto...")
    if not wait_for_postgres(db_host, db_port, db_user, db_pass, db_name):
        print("  ERRO: Impossivel conectar ao PostgreSQL. Abortando.")
        return
    
    # 3. Validar dados com Great Expectations
    print("\n Validando dados com Great Expectations...")
    try:
        setup_great_expectations()
    except Exception as e:
        print(f"  Aviso na validacao: {e}")
    
    # 4. Carregar dados
    print("\n Carregando dados do CSV...")
    try:
        df = pd.read_csv(csv_path)
        print(f"   {len(df):,} registros carregados")
        print(f"   Colunas: {list(df.columns)}")
    except Exception as e:
        print(f"   ERRO ao carregar CSV: {e}")
        return
    
    # 5. Conectar ao PostgreSQL
    print(f"\n Conectando ao PostgreSQL ({db_host}:{db_port}/{db_name})...")
    try:
        conn = psycopg.connect(
            host=db_host,
            port=db_port,
            dbname=db_name,
            user=db_user,
            password=db_pass
        )
        cur = conn.cursor()
        print("   OK conexao estabelecida")
    except Exception as e:
        print(f"   ERRO ao conectar: {e}")
        return
    
    # 6. Verificar dados existentes
    print("\n Verificando dados existentes...")
    try:
        cur.execute("SELECT COUNT(*) FROM fertility_warehouse.fact_fertility")
        existing_count = cur.fetchone()[0]
        print(f"   Registros existentes: {existing_count:,}")
        
        if existing_count > 0:
            print("   Dados ja existem no banco. Pulando ingestao.")
            cur.execute("SELECT COUNT(DISTINCT diagnosis) FROM fertility_warehouse.fact_fertility")
            diagnoses = cur.fetchone()[0]
            print(f"   Diagnosticos unicos: {diagnoses}")
            conn.close()
            return
    except Exception as e:
        print(f"   Nota: {e}")
    
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
                    row.get('age', 0),
                    row.get('season', ''),
                    row.get('childrens_count', 0) if 'childrens_count' in row else None,
                    row.get('childish_diseases', 0) if 'childish_diseases' in row else None,
                    row.get('accident_or_serious_trauma', 0) if 'accident_or_serious_trauma' in row else None,
                    row.get('surgical_intervention', 0) if 'surgical_intervention' in row else None,
                    row.get('high_fevers_in_the_last_year', 0) if 'high_fevers_in_the_last_year' in row else None,
                    row.get('frequency_of_alcohol_consumption', 0) if 'frequency_of_alcohol_consumption' in row else None,
                    row.get('smoking_habit', ''),
                    int(row.get('number_of_hours_spent_sitting_per_day', 0)),
                    row.get('diagnosis', '')
                ))
            
            # Inserir batch na tabela correta
            insert_sql = """
            INSERT INTO fertility_warehouse.fact_fertility 
            (age, season, childrens_count, childish_diseases, accident_or_serious_trauma,
             surgical_intervention, high_fevers_in_the_last_year,
             frequency_of_alcohol_consumption, smoking_habit,
             number_of_hours_spent_sitting_per_day, diagnosis)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cur.executemany(insert_sql, values)
            conn.commit()
            
            progress = ((batch_num + 1) / total_batches) * 100
            print(f"   [{batch_num + 1}/{total_batches}] {progress:.1f}% "
                  f"({(batch_num + 1) * batch_size:,} registros)")
        
        print("   OK Ingestao completa!")
        
    except Exception as e:
        print(f"  Erro durante ingestão: {e}")
        conn.rollback()
        conn.close()
        return
    
    # 8. Verificar integridade
    print("\n Verificando integridade dos dados...")
    try:
        cur.execute("SELECT COUNT(*) FROM fertility_warehouse.fact_fertility")
        total_count = cur.fetchone()[0]
        
        cur.execute("SELECT diagnosis, COUNT(*) FROM fertility_warehouse.fact_fertility GROUP BY diagnosis ORDER BY COUNT(*) DESC")
        diagnoses = cur.fetchall()
        
        cur.execute("SELECT season, COUNT(*) FROM fertility_warehouse.fact_fertility GROUP BY season ORDER BY season")
        seasons = cur.fetchall()
        
        print(f"   Total de registros: {total_count:,}")
        print(f"   Diagnosticos:")
        for diag, count in diagnoses:
            print(f"      - {diag}: {count:,}")
        print(f"   Estacoes:")
        for season, count in seasons:
            print(f"      - {season}: {count:,}")
        
    except Exception as e:
        print(f"   Nota: {e}")
    
    conn.close()
    
    print("\n" + "=" * 70)
    print(" PIPELINE CONCLUÍDO COM SUCESSO!")
    print("=" * 70)
    print("\n Próximos passos:")
    print("   1. Visualizar dados em: http://localhost:3000")
    print("   2. Revisar validações em: gx_context/data_docs/index.html")


if __name__ == "__main__":
    ingest_fertility_data()
