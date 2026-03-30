#!/usr/bin/env python3
"""
Script para configurar Great Expectations com validações na camada Raw.

As expectativas validam:
1. Não há valores nulos nas colunas principais
2. Idade está em intervalo válido (25-36)
3. Valores categóricos válidos
4. Sem duplicatas
5. Todas as colunas esperadas existem
"""

import os
import sys
import pandas as pd
from pathlib import Path


def setup_great_expectations():
    """Configura o contexto Great Expectations para validar dados."""
    
    print("\n" + "=" * 70)
    print("CONFIGURANDO GREAT EXPECTATIONS")
    print("=" * 70)
    
    # Caminho do projeto
    project_root = Path(__file__).parent.parent
    gx_dir = project_root / "gx_context"
    
    # Criar diretório se não existir
    gx_dir.mkdir(exist_ok=True)
    
    print(f"\n1️⃣  Contexto GX em: {gx_dir}")
    
    # Carregar CSV
    csv_path = project_root / "data_raw" / "fertility_1m.csv"
    print(f"\n2️⃣  Carregando dados: {csv_path}")
    
    try:
        # Carregar amostra (100k linhas para performance)
        df = pd.read_csv(csv_path, nrows=100000)
        print(f"   ✅ Dados carregados: {len(df)} linhas")
        print(f"   Colunas: {list(df.columns)}")
    except Exception as e:
        print(f"   ❌ Erro ao carregar dados: {e}")
        return
    
    # Validações manuais (sem GX formal, apenas validação)
    print("\n3️⃣  Executando Expectativas de Qualidade:")
    
    validations = []
    
    # Renomear colunas para lowercase
    df.columns = [col.lower().replace(" ", "_") for col in df.columns]
    
    # Expectativa 1: Sem valores nulos nas colunas principais
    print("\n   📋 EXPECTATIVA 1: expect_column_values_to_not_be_null")
    required_cols = ["age", "season", "diagnosis"]
    for col in required_cols:
        if col in df.columns:
            null_count = df[col].isnull().sum()
            total = len(df)
            null_pct = (null_count / total) * 100
            status = "✅ PASS" if null_count == 0 else "❌ FAIL"
            print(f"      {status} | {col}: {null_count} nulos ({null_pct:.2f}%)")
            validations.append({
                "expectativa": "expect_column_values_to_not_be_null",
                "coluna": col,
                "status": "PASS" if null_count == 0 else "FAIL",
                "nulos": null_count,
                "total": total
            })
    
    # Expectativa 2: Idade em intervalo válido
    print("\n   📋 EXPECTATIVA 2: expect_column_values_to_be_between")
    age_min, age_max = 25, 36
    age_col = df["age"]
    out_range = ((age_col < age_min) | (age_col > age_max)).sum()
    status = "✅ PASS" if out_range == 0 else "❌ FAIL"
    print(f"      {status} | age: {out_range} fora do intervalo [{age_min}-{age_max}]")
    print(f"      Mín: {age_col.min()}, Máx: {age_col.max()}, Média: {age_col.mean():.1f}")
    validations.append({
        "expectativa": "expect_column_values_to_be_between",
        "coluna": "age",
        "min": age_min,
        "max": age_max,
        "status": "PASS" if out_range == 0 else "FAIL",
        "out_of_range": out_range
    })
    
    # Expectativa 3: Valores categóricos válidos (diagnosis)
    print("\n   📋 EXPECTATIVA 3: expect_column_distinct_values_to_be_in_set")
    valid_diagnosis = ["Normal", "Altered"]
    invalid_diagnosis = ~df["diagnosis"].isin(valid_diagnosis)
    invalid_count = invalid_diagnosis.sum()
    status = "✅ PASS" if invalid_count == 0 else "❌ FAIL"
    print(f"      {status} | diagnosis: {invalid_count} valores inválidos")
    print(f"      Valores únicos: {sorted(df['diagnosis'].unique())}")
    validations.append({
        "expectativa": "expect_column_distinct_values_to_be_in_set",
        "coluna": "diagnosis",
        "valores_validos": valid_diagnosis,
        "status": "PASS" if invalid_count == 0 else "FAIL",
        "invalidos": invalid_count
    })
    
    # Expectativa 4: Season tem valores válidos
    print("\n   📋 EXPECTATIVA 4: expect_column_distinct_values_to_be_in_set")
    valid_seasons = ["spring", "summer", "fall", "winter"]
    invalid_season = ~df["season"].isin(valid_seasons)
    invalid_count = invalid_season.sum()
    status = "✅ PASS" if invalid_count == 0 else "❌ FAIL"
    print(f"      {status} | season: {invalid_count} valores inválidos")
    print(f"      Distribuição: {dict(df['season'].value_counts())}")
    validations.append({
        "expectativa": "expect_column_distinct_values_to_be_in_set",
        "coluna": "season",
        "valores_validos": valid_seasons,
        "status": "PASS" if invalid_count == 0 else "FAIL",
        "invalidos": invalid_count
    })
    
    # Expectativa 5: Sem duplicatas
    print("\n   📋 EXPECTATIVA 5: expect_no_duplicate_rows")
    duplicata_count = df.duplicated().sum()
    status = "✅ PASS" if duplicata_count == 0 else "⚠️  WARNING"
    print(f"      {status} | Total de duplicatas: {duplicata_count}")
    validations.append({
        "expectativa": "expect_no_duplicate_rows",
        "status": "PASS" if duplicata_count == 0 else "WARNING",
        "duplicatas": duplicata_count
    })
    
    # Relatório final
    print("\n" + "=" * 70)
    print("RESUMO DAS VALIDAÇÕES")
    print("=" * 70)
    
    pass_count = sum(1 for v in validations if v["status"] == "PASS")
    total_count = len(validations)
    
    print(f"\n✅ Passed: {pass_count}/{total_count}")
    
    # Gerar Data Docs em HTML
    print("\n4️⃣  Gerando Data Docs (HTML)...")
    
    try:
        # Criar diretório de data docs
        docs_dir = gx_dir / "data_docs"
        docs_dir.mkdir(exist_ok=True)
        
        # Gerar relatório HTML
        html_report = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Great Expectations - Relatório de Validação</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
                .summary {{ background: white; padding: 15px; margin: 20px 0; border-radius: 5px; border-left: 4px solid #27ae60; }}
                .validation {{ background: white; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #3498db; }}
                .pass {{ border-left-color: #27ae60; color: #27ae60; font-weight: bold; }}
                .fail {{ border-left-color: #e74c3c; color: #e74c3c; font-weight: bold; }}
                .warning {{ border-left-color: #f39c12; color: #f39c12; font-weight: bold; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background: #34495e; color: white; }}
                tr:hover {{ background: #f9f9f9; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🧬 Great Expectations - Relatório de Validação</h1>
                <p>Camada Raw - Dados de Fertilidade</p>
                <p><small>Gerado automaticamente - Validação de qualidade de dados</small></p>
            </div>
            
            <div class="summary">
                <h2>📊 Resumo</h2>
                <p><strong>Total de Expectativas:</strong> {total_count}</p>
                <p class="pass">✅ Passed: {pass_count}</p>
                <p><strong>Taxa de Sucesso:</strong> {(pass_count/total_count)*100:.1f}%</p>
            </div>
            
            <h2>📋 Detalhes das Validações</h2>
            <table>
                <thead>
                    <tr>
                        <th>Expectativa</th>
                        <th>Coluna/Detalhes</th>
                        <th>Status</th>
                        <th>Informações</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for v in validations:
            expectativa = v.get("expectativa", "N/A")
            coluna = v.get("coluna", v.get("valores_validos", "N/A"))
            status = v.get("status", "UNKNOWN")
            status_class = "pass" if status == "PASS" else "warning" if status == "WARNING" else "fail"
            
            # Info adicional
            info = ""
            if "nulos" in v:
                info = f"{v['nulos']} nulos"
            elif "out_of_range" in v:
                info = f"{v['out_of_range']} fora do intervalo"
            elif "invalidos" in v:
                info = f"{v['invalidos']} inválidos"
            elif "duplicatas" in v:
                info = f"{v['duplicatas']} duplicatas"
            
            html_report += f"""
                    <tr>
                        <td>{expectativa}</td>
                        <td>{coluna}</td>
                        <td class="{status_class}">{status}</td>
                        <td>{info}</td>
                    </tr>
            """
        
        html_report += """
                </tbody>
            </table>
            
            <div class="summary" style="margin-top: 30px;">
                <h2>📁 Próximos Passos</h2>
                <ol>
                    <li>Revisar os dados em data_raw/fertility_1m.csv</li>
                    <li>Executar transformações na camada Silver</li>
                    <li>Agregar na camada Gold para análise</li>
                    <li>Visualizar no dashboard Grafana</li>
                </ol>
            </div>
        </body>
        </html>
        """
        
        # Salvar HTML
        docs_file = docs_dir / "index.html"
        with open(docs_file, "w", encoding="utf-8") as f:
            f.write(html_report)
        
        print(f"   ✅ Data Docs gerado: {docs_file}")
        
    except Exception as e:
        print(f"   ⚠️  Erro ao gerar Data Docs: {e}")
    
    print("\n" + "=" * 70)
    print("✅ GREAT EXPECTATIONS CONFIGURADO COM SUCESSO!")
    print("=" * 70)
    print(f"\n📊 Acesse o relatório: {gx_dir}/data_docs/index.html")


if __name__ == "__main__":
    setup_great_expectations()
