#!/usr/bin/env python3
"""
Descargador de PDFs para ADRES Scraper
=====================================
Descarga ética de archivos PDF desde sitios de ADRES
"""

import os
import re
import time
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import logging

from ..config.settings import Config
from ..utils.helpers import (
    setup_logging, validate_url, safe_filename, 
    format_file_size, create_timestamp, ensure_directory
)


class PDFDownloader:
    """
    Descargador ético de archivos PDF desde sitios de ADRES
    """
    
    def __init__(self, config: Config = None):
        """
        Inicializar descargador de PDFs
        
        Args:
            config: Configuración del sistema
        """
        self.config = config or Config()
        self.session = requests.Session()
        self.logger = setup_logging("pdf_downloader", self.config.paths.logs_dir)
        
        # Configurar sesión con headers éticos
        self.session.headers.update(self.config.scraping.default_headers)
        
        # Estadísticas de descarga
        self.stats = {
            'pages_analyzed': 0,
            'pdfs_found': 0,
            'pdfs_downloaded': 0,
            'total_size_mb': 0.0,
            'start_time': None,
            'end_time': None
        }
    
    def download_pdfs_from_page(self, url: str, output_dir: str = None) -> Dict[str, Any]:
        """
        Descargar todos los PDFs encontrados en una página
        
        Args:
            url: URL de la página a analizar
            output_dir: Directorio de descarga (opcional)
            
        Returns:
            Diccionario con resultados de la descarga
        """
        self.stats['start_time'] = datetime.now()
        
        if not output_dir:
            timestamp = create_timestamp()
            output_dir = os.path.join(
                self.config.paths.downloads_dir, 
                f"pdfs_adres_{timestamp}"
            )
        
        # Crear directorio de salida
        ensure_directory(output_dir)
        pdfs_dir = os.path.join(output_dir, "pdfs")
        ensure_directory(pdfs_dir)
        
        self.logger.info(f"Iniciando descarga de PDFs desde: {url}")
        self.logger.info(f"Directorio de salida: {output_dir}")
        
        try:
            # Analizar página y encontrar PDFs
            pdf_links = self._find_pdf_links(url)
            
            if not pdf_links:
                return self._create_result(url, output_dir, [], "No se encontraron PDFs")
            
            self.logger.info(f"Encontrados {len(pdf_links)} PDFs para descargar")
            
            # Descargar PDFs
            downloaded_files = []
            
            for i, pdf_info in enumerate(pdf_links, 1):
                self.logger.info(f"Descargando PDF {i}/{len(pdf_links)}: {pdf_info['filename']}")
                
                # Aplicar delay ético entre descargas
                if i > 1:
                    delay = self.config.ethical.delay_between_requests
                    self.logger.info(f"Esperando {delay}s (respeto al servidor)")
                    time.sleep(delay)
                
                # Descargar PDF individual
                downloaded_file = self._download_single_pdf(
                    pdf_info['url'], 
                    pdfs_dir,
                    pdf_info
                )
                
                if downloaded_file:
                    downloaded_files.append(downloaded_file)
                    self.stats['pdfs_downloaded'] += 1
            
            # Generar metadatos de la sesión
            self._generate_session_metadata(url, output_dir, downloaded_files, pdf_links)
            
            # Generar análisis de la página
            self._generate_page_analysis(url, output_dir, pdf_links)
            
            self.stats['end_time'] = datetime.now()
            
            return self._create_result(url, output_dir, downloaded_files)
            
        except Exception as e:
            self.logger.error(f"Error en descarga de PDFs: {e}")
            return self._create_result(url, output_dir, [], f"Error: {e}")
    
    def _find_pdf_links(self, url: str) -> List[Dict[str, Any]]:
        """
        Encontrar todos los enlaces a PDFs en una página
        
        Args:
            url: URL de la página a analizar
            
        Returns:
            Lista de información de PDFs encontrados
        """
        try:
            # Realizar petición con delay ético
            self.logger.info(f"Analizando página: {url}")
            time.sleep(self.config.ethical.delay_between_requests)
            
            response = self.session.get(
                url, 
                timeout=self.config.ethical.request_timeout,
                verify=self.config.scraping.ssl_verify
            )
            response.raise_for_status()
            
            self.stats['pages_analyzed'] += 1
            
            # Parsear HTML
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Encontrar todos los enlaces
            links = soup.find_all('a', href=True)
            pdf_links = []
            
            for link in links:
                href = link.get('href', '').strip()
                if not href:
                    continue
                
                # Verificar si es un PDF
                if self._is_pdf_link(href):
                    # Construir URL absoluta
                    absolute_url = urljoin(url, href)
                    
                    # Validar URL
                    if validate_url(absolute_url, self.config.scraping.allowed_domains):
                        pdf_info = {
                            'url': absolute_url,
                            'href_original': href,
                            'text': link.get_text(strip=True),
                            'filename': self._extract_filename(absolute_url),
                            'tipo': '.pdf'
                        }
                        pdf_links.append(pdf_info)
                        self.stats['pdfs_found'] += 1
            
            self.logger.info(f"Encontrados {len(pdf_links)} PDFs válidos")
            return pdf_links
            
        except Exception as e:
            self.logger.error(f"Error analizando página: {e}")
            return []
    
    def _download_single_pdf(self, pdf_url: str, output_dir: str, pdf_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Descargar un PDF individual
        
        Args:
            pdf_url: URL del PDF
            output_dir: Directorio de destino
            pdf_info: Información del PDF
            
        Returns:
            Información del archivo descargado o None si falla
        """
        try:
            # Generar nombre de archivo seguro
            timestamp = create_timestamp()
            original_filename = pdf_info['filename']
            safe_name = safe_filename(f"{timestamp}_{original_filename}")
            filepath = os.path.join(output_dir, safe_name)
            
            # Verificar que el archivo no exista
            counter = 1
            while os.path.exists(filepath):
                name, ext = os.path.splitext(safe_name)
                filepath = os.path.join(output_dir, f"{name}_{counter}{ext}")
                counter += 1
            
            # Descargar PDF
            self.logger.info(f"Descargando: {pdf_url}")
            
            response = self.session.get(
                pdf_url,
                timeout=self.config.ethical.request_timeout * 2,  # Timeout más largo para PDFs
                verify=self.config.scraping.ssl_verify
            )
            response.raise_for_status()
            
            # Verificar que sea realmente un PDF
            if not self._verify_pdf_content(response.content):
                self.logger.warning(f"El archivo no parece ser un PDF válido: {pdf_url}")
                return None
            
            # Guardar archivo
            with open(filepath, 'wb') as pdf_file:
                pdf_file.write(response.content)
            
            file_size = len(response.content)
            size_mb = file_size / (1024 * 1024)
            self.stats['total_size_mb'] += size_mb
            
            file_info = {
                'nombre_archivo': os.path.basename(filepath),
                'ruta_local': filepath,
                'url_original': pdf_url,
                'tamaño_bytes': file_size,
                'tamaño_formateado': format_file_size(file_size),
                'fecha_descarga': datetime.now().isoformat(),
                **pdf_info
            }
            
            self.logger.info(f"PDF descargado: {os.path.basename(filepath)} ({format_file_size(file_size)})")
            return file_info
            
        except Exception as e:
            self.logger.error(f"Error descargando PDF {pdf_url}: {e}")
            return None
    
    def _is_pdf_link(self, href: str) -> bool:
        """
        Verificar si un enlace apunta a un PDF
        
        Args:
            href: URL o href del enlace
            
        Returns:
            True si parece ser un enlace a PDF
        """
        href_lower = href.lower()
        
        # Verificación directa por extensión
        if href_lower.endswith('.pdf'):
            return True
        
        # Verificación por patrones en la URL
        pdf_patterns = [
            r'\.pdf(\?|$)',
            r'/pdf/',
            r'type=pdf',
            r'format=pdf'
        ]
        
        for pattern in pdf_patterns:
            if re.search(pattern, href_lower):
                return True
        
        return False
    
    def _verify_pdf_content(self, content: bytes) -> bool:
        """
        Verificar que el contenido sea realmente un PDF
        
        Args:
            content: Contenido binario del archivo
            
        Returns:
            True si es un PDF válido
        """
        if len(content) < 10:
            return False
        
        # Los PDFs empiezan con %PDF
        return content[:4] == b'%PDF'
    
    def _extract_filename(self, url: str) -> str:
        """
        Extraer nombre de archivo desde URL
        
        Args:
            url: URL del archivo
            
        Returns:
            Nombre de archivo extraído
        """
        try:
            parsed = urlparse(url)
            filename = os.path.basename(parsed.path)
            
            if not filename or not filename.endswith('.pdf'):
                filename = f"documento_{create_timestamp()}.pdf"
            
            return filename
            
        except Exception:
            return f"documento_{create_timestamp()}.pdf"
    
    def _generate_session_metadata(self, url: str, output_dir: str, downloaded_files: List[Dict], all_pdfs: List[Dict]):
        """
        Generar archivo de metadatos de la sesión
        
        Args:
            url: URL analizada
            output_dir: Directorio de salida
            downloaded_files: Archivos descargados
            all_pdfs: Todos los PDFs encontrados
        """
        metadata = {
            'fecha_proceso': datetime.now().isoformat(),
            'url_objetivo': url,
            'directorio_descargas': output_dir,
            'estadisticas': {
                'pdfs_encontrados': len(all_pdfs),
                'pdfs_descargados': len(downloaded_files),
                'tamaño_total_mb': round(self.stats['total_size_mb'], 2),
                'tiempo_proceso_minutos': self._calculate_process_time()
            },
            'archivos_descargados': downloaded_files,
            'todos_los_pdfs_encontrados': all_pdfs,
            'configuracion_descarga': {
                'delay_entre_requests': self.config.ethical.delay_between_requests,
                'timeout_requests': self.config.ethical.request_timeout,
                'dominios_permitidos': self.config.scraping.allowed_domains
            }
        }
        
        metadata_file = os.path.join(output_dir, 'metadatos_descarga.json')
        
        try:
            import json
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Metadatos guardados en: {metadata_file}")
            
        except Exception as e:
            self.logger.error(f"Error guardando metadatos: {e}")
    
    def _generate_page_analysis(self, url: str, output_dir: str, pdf_links: List[Dict]):
        """
        Generar análisis de la página procesada
        
        Args:
            url: URL analizada
            output_dir: Directorio de salida
            pdf_links: Enlaces PDF encontrados
        """
        try:
            # Re-obtener la página para análisis completo
            response = self.session.get(url, verify=self.config.scraping.ssl_verify)
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Análisis básico de la página
            analysis = {
                'url_analizada': url,
                'fecha_analisis': datetime.now().isoformat(),
                'titulo_pagina': soup.title.get_text(strip=True) if soup.title else '',
                'total_enlaces': len(soup.find_all('a', href=True)),
                'documentos_pdf_encontrados': len(pdf_links),
                'tipos_documentos': ['.pdf'],
                'enlaces_pdf': pdf_links,
                'estructura_pagina': {
                    'tiene_navegacion': bool(soup.find('nav')),
                    'tiene_header': bool(soup.find('header')),
                    'tiene_footer': bool(soup.find('footer')),
                    'headings_h1': len(soup.find_all('h1')),
                    'headings_h2': len(soup.find_all('h2')),
                    'headings_h3': len(soup.find_all('h3'))
                }
            }
            
            analysis_file = os.path.join(output_dir, 'analisis_pagina.json')
            
            import json
            with open(analysis_file, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Análisis de página guardado en: {analysis_file}")
            
        except Exception as e:
            self.logger.error(f"Error generando análisis de página: {e}")
    
    def _calculate_process_time(self) -> float:
        """Calcular tiempo de proceso en minutos"""
        if self.stats['start_time'] and self.stats['end_time']:
            delta = self.stats['end_time'] - self.stats['start_time']
            return round(delta.total_seconds() / 60, 2)
        return 0.0
    
    def _create_result(self, url: str, output_dir: str, files: List[Dict], error: str = None) -> Dict[str, Any]:
        """
        Crear diccionario de resultado
        
        Args:
            url: URL procesada
            output_dir: Directorio de salida
            files: Archivos descargados
            error: Mensaje de error (opcional)
            
        Returns:
            Diccionario con resultado de la operación
        """
        return {
            'url_procesada': url,
            'directorio_salida': output_dir,
            'archivos_descargados': len(files),
            'detalles_archivos': files,
            'estadisticas': self.stats.copy(),
            'error': error,
            'timestamp': datetime.now().isoformat(),
            'exitoso': error is None
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de descarga"""
        return self.stats.copy()
    
    def reset_stats(self):
        """Reiniciar estadísticas"""
        for key in self.stats:
            if isinstance(self.stats[key], (int, float)):
                self.stats[key] = 0
            else:
                self.stats[key] = None