"""
Fertility Data Pipeline - Módulo principal

Módulo para ingestão, validação e transformação de dados de fertilidade.
Segue arquitetura Medallion: Raw → Silver → Gold
"""

__version__ = "1.0.0"
__author__ = "Data Team"
__all__ = ["ingest_data", "setup_great_expectations"]
