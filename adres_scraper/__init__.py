#!/usr/bin/env python3
"""
ADRES Scraper - Paquete Principal
=================================
Web scraping ético para documentos de ADRES (Colombia)

Autor: Taller Big Data 2025
Licencia: MIT
"""

__version__ = "2.0.0"
__author__ = "Taller Big Data"
__email__ = "contacto@ejemplo.com"
__description__ = "Web scraping ético para documentos de ADRES"

from .core.scraper import ADREScraper
from .core.content_analyzer import ContentAnalyzer
from .mongodb.manager import MongoDBManager
from .downloaders.pdf_downloader import PDFDownloader
from .config.settings import Config

__all__ = [
    'ADREScraper',
    'ContentAnalyzer', 
    'MongoDBManager',
    'PDFDownloader',
    'Config'
]