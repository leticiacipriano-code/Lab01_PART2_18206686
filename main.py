#!/usr/bin/env python3
"""
Script principal para executar o pipeline completo.

Uso:
    python main.py validate    # Executar só validações
    python main.py ingest      # Executar só ingestão
    python main.py full        # Executar pipeline completo
    python main.py --help      # Ver ajuda
"""

import sys
import argparse
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ingest_data import ingest_fertility_data
from setup_great_expectations import setup_great_expectations


def main():
    """Função principal do pipeline."""
    
    parser = argparse.ArgumentParser(
        description=" Fertility Data Pipeline - Lab01_PART2",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python main.py validate    # Executar validações GX
  python main.py ingest      # Ingerir dados no PostgreSQL
  python main.py full        # Executar pipeline completo
  python main.py --help      # Mostrar esta mensagem
        """
    )
    
    parser.add_argument(
        "action",
        nargs="?",
        default="full",
        choices=["validate", "ingest", "full"],
        help="Ação a executar (padrão: full)"
    )
    
    args = parser.parse_args()
    
    print("\n" + "=" * 70)
    print(" FERTILITY DATA PIPELINE - MENU PRINCIPAL")
    print("=" * 70)
    
    if args.action in ["validate", "full"]:
        print("\n  ETAPA 1: VALIDAÇÃO COM GREAT EXPECTATIONS")
        try:
            setup_great_expectations()
        except Exception as e:
            print(f" Erro na validação: {e}")
            if args.action != "full":
                return 1
    
    if args.action in ["ingest", "full"]:
        print("\n ETAPA 2: INGESTÃO DE DADOS")
        try:
            ingest_fertility_data()
        except Exception as e:
            print(f" Erro na ingestão: {e}")
            return 1
    
    print("\n" + "=" * 70)
    print(" PIPELINE CONCLUÍDO COM SUCESSO!")
    print("=" * 70)
    print("""
📊 Próximos passos:
   1. Acessar Grafana: http://localhost:3000
   2. Login: admin / admin
   3. Dashboard: Fertility Data - Gold Layer
   4. Validações: gx_context/data_docs/index.html
    """)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
