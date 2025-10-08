#!/usr/bin/env python3
"""
ADRES Scraper - Scraper Principal Unificado
==========================================
Web scraper ético para documentos de ADRES consolidado y optimizado
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import os
import logging
from datetime import datetime
from typing import Dict, Optional, Any, List
from urllib.parse import urlparse, urljoin

from ..config.settings import Config
from ..utils.helpers import setup_logging, validate_url, normalizar_url
from ..core.content_analyzer import ContentAnalyzer


class ADREScraper:
    """
    Scraper principal unificado para documentos de ADRES
    Implementa las mejores prácticas de web scraping ético
    """
    
    def __init__(self, config: Config = None):
        """
        Inicializar scraper con configuración
        
        Args:
            config: Instancia de configuración del sistema
        """
        self.config = config or Config()
        self.session = requests.Session()
        self.logger = setup_logging("adres_scraper", self.config.paths.logs_dir)
        self.content_analyzer = ContentAnalyzer()
        
        # Configurar sesión con headers éticos
        self.session.headers.update(self.config.scraping.default_headers)
        
        self.logger.info("ADRES Scraper inicializado correctamente")
    
    def scrape_document(self, url: str = None) -> Dict[str, Any]:
        """
        Extraer documento de ADRES siguiendo principios éticos
        
        Args:
            url: URL del documento a extraer (opcional, usa la configurada por defecto)
            
        Returns:
            Diccionario con el contenido extraído y metadatos
        """
        target_url = url or self.config.urls.default_document_url
        
        self.logger.info(f"Iniciando extracción ética de: {target_url}")
        
        # Validar URL
        if not self._validate_url(target_url):
            return self._create_error_response(
                target_url, 
                "URL no válida o dominio no permitido",
                "validation_error"
            )
        
        # Extraer contenido con reintentos controlados
        for attempt in range(self.config.ethical.max_retries + 1):
            try:
                if attempt > 0:
                    # Backoff exponencial para reintentos
                    delay = self.config.ethical.delay_between_requests * (2 ** attempt)
                    self.logger.info(f"Reintento {attempt + 1}, esperando {delay}s")
                    time.sleep(delay)
                else:
                    # Delay ético inicial
                    self.logger.info(f"Esperando {self.config.ethical.delay_between_requests}s (respeto al servidor)")
                    time.sleep(self.config.ethical.delay_between_requests)
                
                # Realizar petición HTTP
                response = self._make_request(target_url)
                
                if response:
                    # Procesar contenido
                    return self._process_response(response, target_url, attempt + 1)
                    
            except Exception as e:
                self.logger.error(f"Error en intento {attempt + 1}: {e}")
                if attempt == self.config.ethical.max_retries:
                    return self._create_error_response(
                        target_url,
                        f"Falló después de {self.config.ethical.max_retries + 1} intentos: {e}",
                        "extraction_error"
                    )
        
        return self._create_error_response(target_url, "Error desconocido", "unknown_error")
    
    def scrape_multiple_documents(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Extraer múltiples documentos con delays éticos
        
        Args:
            urls: Lista de URLs a procesar
            
        Returns:
            Lista de resultados de extracción
        """
        results = []
        total_urls = len(urls)
        
        self.logger.info(f"Procesando {total_urls} URLs con principios éticos")
        
        for i, url in enumerate(urls, 1):
            self.logger.info(f"Procesando {i}/{total_urls}: {url}")
            
            result = self.scrape_document(url)
            results.append(result)
            
            # Delay entre documentos (excepto el último)
            if i < total_urls:
                delay = self.config.ethical.delay_between_requests
                self.logger.info(f"Esperando {delay}s antes del siguiente documento")
                time.sleep(delay)
        
        return results
    
    def _make_request(self, url: str) -> Optional[requests.Response]:
        """
        Realizar petición HTTP con manejo de errores
        
        Args:
            url: URL objetivo
            
        Returns:
            Respuesta HTTP o None si falla
        """
        try:
            self.logger.info("Realizando petición HTTP con headers éticos")
            
            response = self.session.get(
                url,
                timeout=self.config.ethical.request_timeout,
                allow_redirects=True,
                verify=self.config.scraping.ssl_verify
            )
            
            response.raise_for_status()
            
            # Verificar tamaño de contenido
            content_length = len(response.content)
            if content_length > self.config.scraping.max_content_size:
                raise ValueError(f"Contenido muy grande: {content_length} bytes")
            
            self.logger.info(f"Petición exitosa. Código: {response.status_code}, Tamaño: {content_length} bytes")
            return response
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error en petición HTTP: {e}")
            return None
        except ValueError as e:
            self.logger.error(f"Error de validación: {e}")
            return None
    
    def _process_response(self, response: requests.Response, url: str, attempts: int) -> Dict[str, Any]:
        """
        Procesar respuesta HTTP y extraer contenido
        
        Args:
            response: Respuesta HTTP
            url: URL original
            attempts: Número de intentos realizados
            
        Returns:
            Diccionario con contenido extraído
        """
        try:
            # Crear objeto BeautifulSoup
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Encontrar contenedor principal
            main_container = self._find_main_container(soup)
            
            if not main_container:
                return self._create_error_response(
                    url,
                    "No se pudo encontrar el contenedor principal de contenido",
                    "parsing_error"
                )
            
            # Extraer y limpiar texto
            extracted_text = self._extract_clean_text(main_container)
            
            # Analizar contenido
            analysis = self.content_analyzer.analyze_content(extracted_text, url)
            
            # Crear respuesta exitosa
            return {
                'url_original': url,
                'status': 'OK',
                'fecha_extraccion': datetime.now().isoformat(),
                'timestamp_unix': int(time.time()),
                'texto_completo': extracted_text,
                'longitud_caracteres': len(extracted_text),
                'longitud_palabras': len(extracted_text.split()),
                'intentos_realizados': attempts,
                'analisis_contenido': analysis,
                'metadatos_http': {
                    'status_code': response.status_code,
                    'content_type': response.headers.get('content-type', ''),
                    'server': response.headers.get('server', ''),
                    'content_length': len(response.content)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error procesando respuesta: {e}")
            return self._create_error_response(
                url,
                f"Error en procesamiento: {e}",
                "processing_error"
            )
    
    def _find_main_container(self, soup: BeautifulSoup) -> Optional[Any]:
        """
        Encontrar el contenedor principal de contenido
        
        Args:
            soup: Objeto BeautifulSoup
            
        Returns:
            Elemento contenedor principal o None
        """
        # Selectores ordenados por especificidad
        selectors = [
            {'tag': 'main'},
            {'tag': 'article'},
            {'tag': 'div', 'attrs': {'id': 'content'}},
            {'tag': 'div', 'attrs': {'class': 'content'}},
            {'tag': 'div', 'attrs': {'class': 'main-content'}},
            {'tag': 'div', 'attrs': {'class': 'document-content'}},
            {'tag': 'div', 'attrs': {'class': 'texto-concepto'}},
            {'tag': 'div', 'attrs': {'class': 'contenido-normograma'}},
            {'tag': 'section'},
            {'tag': 'div', 'attrs': {'id': 'container'}},
            {'tag': 'div', 'attrs': {'class': 'container'}}
        ]
        
        for selector in selectors:
            if 'attrs' in selector:
                container = soup.find(selector['tag'], selector['attrs'])
            else:
                container = soup.find(selector['tag'])
            
            if container and container.get_text(strip=True):
                self.logger.info(f"Contenedor encontrado: {selector}")
                return container
        
        # Fallback al body
        self.logger.warning("Usando body como fallback")
        return soup.find('body')
    
    def _extract_clean_text(self, container) -> str:
        """
        Extraer y limpiar texto del contenedor
        
        Args:
            container: Elemento HTML contenedor
            
        Returns:
            Texto limpio extraído
        """
        # Eliminar elementos no deseados
        unwanted_elements = ['script', 'style', 'nav', 'header', 'footer', 'aside', 'noscript']
        
        for element_type in unwanted_elements:
            for element in container.find_all(element_type):
                element.decompose()
        
        # Extraer texto con separadores
        text = container.get_text(separator='\n', strip=True)
        
        # Limpiar líneas vacías múltiples
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        cleaned_text = '\n'.join(lines)
        
        return cleaned_text
    
    def _validate_url(self, url: str) -> bool:
        """
        Validar que la URL pertenezca a dominios permitidos
        
        Args:
            url: URL a validar
            
        Returns:
            True si la URL es válida
        """
        try:
            parsed_url = urlparse(url)
            return any(domain in parsed_url.netloc for domain in self.config.scraping.allowed_domains)
        except Exception:
            return False
    
    def _create_error_response(self, url: str, error_message: str, error_type: str) -> Dict[str, Any]:
        """
        Crear respuesta de error estandarizada
        
        Args:
            url: URL que causó el error
            error_message: Mensaje de error
            error_type: Tipo de error
            
        Returns:
            Diccionario de respuesta de error
        """
        return {
            'url_original': url,
            'status': 'ERROR',
            'error_type': error_type,
            'error_message': error_message,
            'fecha_error': datetime.now().isoformat(),
            'timestamp_unix': int(time.time())
        }
    
    def save_result(self, result: Dict[str, Any], filename: str = None) -> str:
        """
        Guardar resultado en archivo JSON
        
        Args:
            result: Resultado a guardar
            filename: Nombre del archivo (opcional)
            
        Returns:
            Ruta del archivo guardado
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f'adres_scraping_result_{timestamp}.json'
        
        filepath = self.config.paths.get_json_output_path(filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Resultado guardado en: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error guardando archivo: {e}")
            raise
    
    def close(self):
        """Cerrar sesión y recursos"""
        if self.session:
            self.session.close()
        self.logger.info("Sesión cerrada correctamente")