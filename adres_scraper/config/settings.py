#!/usr/bin/env python3
"""
Configuración Centralizada del Sistema ADRES Scraper
===================================================
Todas las configuraciones del sistema unificadas
"""

import os
from dataclasses import dataclass
from typing import Dict, List, Optional
from urllib.parse import urljoin

@dataclass
class EthicalConfig:
    """Configuración ética para web scraping"""
    delay_between_requests: float = 3.0  # segundos
    max_retries: int = 3
    request_timeout: int = 30
    respect_robots_txt: bool = True
    user_agent: str = "ADRES-Scraper-Educativo/2.0 (proposito:academico)"
    
@dataclass 
class MongoDBConfig:
    """Configuración MongoDB Atlas"""
    connection_string: str = "mongodb+srv://efrenbohorquezv_db_user:Central2025*@cluster0.ljpppvo.mongodb.net/"
    database_name: str = "adres_documentos"
    collections: Dict[str, str] = None
    
    def __post_init__(self):
        if self.collections is None:
            self.collections = {
                'documents': 'resoluciones_adres',
                'pdf_files': 'pdfs_archivos',
                'pdf_metadata': 'pdfs_metadatos',
                'download_sessions': 'metadatos_descargas'
            }

@dataclass
class ScrapingConfig:
    """Configuración de web scraping"""
    allowed_domains: List[str] = None
    default_headers: Dict[str, str] = None
    ssl_verify: bool = False
    max_content_size: int = 10 * 1024 * 1024  # 10MB
    
    def __post_init__(self):
        if self.allowed_domains is None:
            self.allowed_domains = [
                'normograma.adres.gov.co',
                'adres.gov.co'
            ]
            
        if self.default_headers is None:
            self.default_headers = {
                'User-Agent': 'ADRES-Scraper-Educativo/2.0 (proposito:academico)',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Cache-Control': 'max-age=0'
            }

@dataclass
class PathsConfig:
    """Configuración de rutas y directorios"""
    base_dir: str = os.getcwd()
    data_dir: str = "data"
    downloads_dir: str = "data/downloads"
    json_output_dir: str = "data/json_outputs"
    logs_dir: str = "logs"
    temp_dir: str = "temp"
    
    def __post_init__(self):
        # Crear rutas absolutas
        self.data_dir = os.path.join(self.base_dir, self.data_dir)
        self.downloads_dir = os.path.join(self.base_dir, self.downloads_dir)
        self.json_output_dir = os.path.join(self.base_dir, self.json_output_dir)
        self.logs_dir = os.path.join(self.base_dir, self.logs_dir)
        self.temp_dir = os.path.join(self.base_dir, self.temp_dir)
        
        # Crear directorios si no existen
        for directory in [self.data_dir, self.downloads_dir, self.json_output_dir, 
                         self.logs_dir, self.temp_dir]:
            os.makedirs(directory, exist_ok=True)

@dataclass
class URLsConfig:
    """Configuración de URLs objetivo"""
    base_url: str = "https://normograma.adres.gov.co"
    default_document_url: str = "https://normograma.adres.gov.co/compilacion/docs/concepto_adres_20241209688471_2024.html"
    guides_url: str = "https://normograma.adres.gov.co/compilacion/aprende_adres_guias.html"
    
    # URLs de ejemplo para pruebas
    test_urls: List[str] = None
    
    def __post_init__(self):
        if self.test_urls is None:
            self.test_urls = [
                "https://normograma.adres.gov.co/adres/docs/resolucion_adres_2876_2013.htm",
                "https://normograma.adres.gov.co/adres/docs/resolucion_adres_0743_2013.htm",
                "https://normograma.adres.gov.co/adres/docs/resolucion_adres_2587_2012.htm"
            ]

class Config:
    """Clase principal de configuración del sistema"""
    
    def __init__(self):
        self.ethical = EthicalConfig()
        self.mongodb = MongoDBConfig()
        self.scraping = ScrapingConfig()
        self.paths = PathsConfig()
        self.urls = URLsConfig()
    
    def validate(self) -> bool:
        """Validar configuración"""
        try:
            # Validar URLs
            from urllib.parse import urlparse
            
            for url in [self.urls.default_document_url, self.urls.guides_url]:
                parsed = urlparse(url)
                if not parsed.netloc or parsed.netloc not in self.scraping.allowed_domains:
                    raise ValueError(f"URL no válida o dominio no permitido: {url}")
            
            # Validar directorios
            for directory in [self.paths.data_dir, self.paths.downloads_dir]:
                if not os.path.exists(directory):
                    raise ValueError(f"Directorio no encontrado: {directory}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error en validación de configuración: {e}")
            return False
    
    def get_mongodb_uri(self) -> str:
        """Obtener URI de MongoDB con validación"""
        return self.mongodb.connection_string
    
    def get_collection_name(self, collection_type: str) -> str:
        """Obtener nombre de colección por tipo"""
        return self.mongodb.collections.get(collection_type, f"adres_{collection_type}")
    
    def get_download_path(self, filename: str = None) -> str:
        """Obtener ruta de descarga"""
        if filename:
            return os.path.join(self.paths.downloads_dir, filename)
        return self.paths.downloads_dir
    
    def get_json_output_path(self, filename: str) -> str:
        """Obtener ruta para archivos JSON de salida"""
        return os.path.join(self.paths.json_output_dir, filename)
    
    def print_summary(self):
        """Mostrar resumen de configuración"""
        print("="*60)
        print("🔧 CONFIGURACIÓN DEL SISTEMA ADRES SCRAPER")
        print("="*60)
        print(f"📊 Base de datos: {self.mongodb.database_name}")
        print(f"⏱️ Delay entre requests: {self.ethical.delay_between_requests}s")
        print(f"🔄 Max reintentos: {self.ethical.max_retries}")
        print(f"📁 Directorio datos: {self.paths.data_dir}")
        print(f"🌐 URL por defecto: {self.urls.default_document_url}")
        print(f"🛡️ Dominios permitidos: {', '.join(self.scraping.allowed_domains)}")
        print("="*60)

# Instancia global de configuración
config = Config()

# Función para obtener configuración
def get_config() -> Config:
    """Obtener instancia de configuración"""
    return config

# Función para recargar configuración
def reload_config():
    """Recargar configuración"""
    global config
    config = Config()
    return config