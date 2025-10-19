#!/usr/bin/env python3
"""
ðŸ“„ DESCARGADOR DE PDFs ADRES - Ã‰TICO Y PROFESIONAL
MÃ³dulo para descargar PDFs encontrados durante el web scraping de ADRES
Aplicando principios Ã©ticos desarrollados en el taller
"""

import requests
from bs4 import BeautifulSoup
import time
import os
import json
from datetime import datetime
import urllib.parse
from pathlib import Path
import logging

class DescargadorPDFsADRES:
    """
    Descargador Ã©tico de PDFs de ADRES
    """
    
    def __init__(self):
        self.config = self._configurar_descargador()
        self.logger = self._configurar_logging()
        self.directorio_pdfs = "data/pdfs_adres"
        self.metadatos_pdfs = []
        
    def _configurar_descargador(self):
        """ConfiguraciÃ³n Ã©tica para descarga de PDFs"""
        return {
            "headers_eticos": {
                'User-Agent': 'Taller-BigData-Educativo/2.0 (investigacion.academica@universidad.edu)',
                'Accept': 'application/pdf,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Purpose': 'Academic Research - PDF Document Analysis - ADRES Study'
            },
            "delay_entre_descargas": 3.0,  # 3 segundos entre descargas
            "timeout": 45,  # 45 segundos para PDFs (pueden ser grandes)
            "max_reintentos": 2,
            "max_size_mb": 50,  # MÃ¡ximo 50MB por PDF
            "dominios_permitidos": ['normograma.adres.gov.co', 'adres.gov.co']
        }
    
    def _configurar_logging(self):
        """Configurar logging especÃ­fico para PDFs"""
        logger = logging.getLogger('DescargadorPDFs')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def crear_directorio_pdfs(self):
        """Crear directorio para almacenar PDFs"""
        Path(self.directorio_pdfs).mkdir(parents=True, exist_ok=True)
        self.logger.info("Directorio de PDFs creado: %s", self.directorio_pdfs)
    
    def buscar_pdfs_en_pagina(self, url_pagina):
        """
        Buscar enlaces a PDFs en una pÃ¡gina de ADRES
        """
        print(f"ðŸ” Buscando PDFs en: {url_pagina}")
        
        try:
            # Respetar delay
            time.sleep(self.config["delay_entre_descargas"])
            
            response = requests.get(
                url_pagina,
                headers=self.config["headers_eticos"],
                timeout=self.config["timeout"]
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar enlaces a PDFs
            enlaces_pdf = []
            
            # Buscar enlaces directos a PDF
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                if href and href.lower().endswith('.pdf'):
                    # Convertir URL relativa a absoluta
                    url_completa = urllib.parse.urljoin(url_pagina, href)
                    
                    # Verificar dominio permitido
                    if self._es_dominio_permitido(url_completa):
                        enlaces_pdf.append({
                            'url': url_completa,
                            'texto_enlace': link.get_text(strip=True),
                            'pagina_origen': url_pagina
                        })
            
            self.logger.info("PDFs encontrados: %d", len(enlaces_pdf))
            return enlaces_pdf
            
        except Exception as e:
            self.logger.error("Error buscando PDFs en %s: %s", url_pagina, str(e))
            return []
    
    def _es_dominio_permitido(self, url):
        """Verificar si el dominio estÃ¡ permitido"""
        parsed_url = urllib.parse.urlparse(url)
        return any(dominio in parsed_url.netloc for dominio in self.config["dominios_permitidos"])
    
    def descargar_pdf(self, info_pdf):
        """
        Descargar un PDF especÃ­fico
        """
        url_pdf = info_pdf['url']
        texto_enlace = info_pdf.get('texto_enlace', 'documento')
        
        # Generar nombre de archivo seguro
        nombre_archivo = self._generar_nombre_archivo(url_pdf, texto_enlace)
        ruta_archivo = os.path.join(self.directorio_pdfs, nombre_archivo)
        
        # Verificar si ya existe
        if os.path.exists(ruta_archivo):
            print(f"âš ï¸ PDF ya existe: {nombre_archivo}")
            return ruta_archivo
        
        print(f"ðŸ“¥ Descargando: {nombre_archivo}")
        
        try:
            # Respetar delay entre descargas
            time.sleep(self.config["delay_entre_descargas"])
            
            # Verificar tamaÃ±o antes de descargar
            head_response = requests.head(url_pdf, headers=self.config["headers_eticos"], timeout=10)
            content_length = head_response.headers.get('content-length')
            
            if content_length:
                size_mb = int(content_length) / (1024 * 1024)
                if size_mb > self.config["max_size_mb"]:
                    print(f"âš ï¸ PDF muy grande ({size_mb:.1f}MB), omitiendo: {nombre_archivo}")
                    return None
            
            # Descargar PDF
            response = requests.get(
                url_pdf,
                headers=self.config["headers_eticos"],
                timeout=self.config["timeout"],
                stream=True
            )
            response.raise_for_status()
            
            # Guardar archivo
            with open(ruta_archivo, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # Verificar que se descargÃ³ correctamente
            if os.path.exists(ruta_archivo) and os.path.getsize(ruta_archivo) > 0:
                size_kb = os.path.getsize(ruta_archivo) / 1024
                print(f"âœ… Descargado: {nombre_archivo} ({size_kb:.1f} KB)")
                
                # Guardar metadatos
                self.metadatos_pdfs.append({
                    'url_original': url_pdf,
                    'nombre_archivo': nombre_archivo,
                    'ruta_local': ruta_archivo,
                    'texto_enlace': texto_enlace,
                    'pagina_origen': info_pdf.get('pagina_origen'),
                    'fecha_descarga': datetime.now().isoformat(),
                    'tamaÃ±o_bytes': os.path.getsize(ruta_archivo)
                })
                
                return ruta_archivo
            else:
                print(f"âŒ Error: archivo vacÃ­o o no creado: {nombre_archivo}")
                return None
                
        except Exception as e:
            self.logger.error("Error descargando PDF %s: %s", url_pdf, str(e))
            return None\n    \n    def _generar_nombre_archivo(self, url_pdf, texto_enlace):\n        \"\"\"Generar nombre de archivo seguro para el PDF\"\"\"\n        # Extraer nombre del URL\n        nombre_url = os.path.basename(urllib.parse.urlparse(url_pdf).path)\n        \n        if nombre_url and nombre_url.endswith('.pdf'):\n            nombre_base = nombre_url\n        else:\n            # Usar texto del enlace como base\n            nombre_limpio = \"\".join(c for c in texto_enlace if c.isalnum() or c in (' ', '-', '_')).strip()\n            nombre_limpio = nombre_limpio[:50]  # Limitar longitud\n            nombre_base = f\"{nombre_limpio}.pdf\"\n        \n        # Agregar timestamp para evitar colisiones\n        timestamp = datetime.now().strftime(\"%Y%m%d_%H%M%S\")\n        nombre_final = f\"{timestamp}_{nombre_base}\"\n        \n        return nombre_final\n    \n    def descargar_pdfs_desde_urls(self, urls_paginas):\n        \"\"\"\n        Buscar y descargar PDFs de mÃºltiples pÃ¡ginas\n        \"\"\"\n        print(\"ðŸŽ“ TALLER BIG DATA - DESCARGADOR DE PDFs ADRES\")\n        print(\"ðŸ” BÃºsqueda y descarga Ã©tica de documentos PDF\")\n        print(\"=\" * 60)\n        \n        self.crear_directorio_pdfs()\n        \n        total_pdfs_encontrados = 0\n        total_pdfs_descargados = 0\n        \n        for i, url in enumerate(urls_paginas, 1):\n            print(f\"\\nðŸ“„ PÃ¡gina {i}/{len(urls_paginas)}: {url}\")\n            \n            # Buscar PDFs en esta pÃ¡gina\n            pdfs_encontrados = self.buscar_pdfs_en_pagina(url)\n            total_pdfs_encontrados += len(pdfs_encontrados)\n            \n            # Descargar cada PDF encontrado\n            for j, info_pdf in enumerate(pdfs_encontrados, 1):\n                print(f\"  ðŸ“¥ PDF {j}/{len(pdfs_encontrados)}\")\n                ruta_descargada = self.descargar_pdf(info_pdf)\n                \n                if ruta_descargada:\n                    total_pdfs_descargados += 1\n        \n        # Guardar metadatos\n        self.guardar_metadatos_pdfs()\n        \n        # Resumen final\n        print(f\"\\nðŸ“Š RESUMEN DE DESCARGA\")\n        print(\"=\" * 40)\n        print(f\"ðŸ” PDFs encontrados: {total_pdfs_encontrados}\")\n        print(f\"ðŸ“¥ PDFs descargados: {total_pdfs_descargados}\")\n        print(f\"ðŸ“ Directorio: {self.directorio_pdfs}\")\n        \n        return total_pdfs_descargados > 0\n    \n    def guardar_metadatos_pdfs(self):\n        \"\"\"Guardar metadatos de PDFs descargados\"\"\"\n        if not self.metadatos_pdfs:\n            return\n        \n        archivo_metadatos = os.path.join(self.directorio_pdfs, \"metadatos_pdfs.json\")\n        \n        datos_completos = {\n            'fecha_generacion': datetime.now().isoformat(),\n            'total_pdfs': len(self.metadatos_pdfs),\n            'directorio_pdfs': self.directorio_pdfs,\n            'pdfs': self.metadatos_pdfs\n        }\n        \n        with open(archivo_metadatos, 'w', encoding='utf-8') as f:\n            json.dump(datos_completos, f, indent=2, ensure_ascii=False)\n        \n        print(f\"ðŸ’¾ Metadatos guardados: {archivo_metadatos}\")\n\n

# Bloque de demostración removido - módulo de librería
# Para usar: importar DescargadorPDFsADRES desde este módulo
