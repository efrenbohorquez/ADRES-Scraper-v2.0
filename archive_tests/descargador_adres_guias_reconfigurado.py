#!/usr/bin/env python3
"""
📄 DESCARGADOR ADRES GUÍAS - RECONFIGURADO
URL específica: https://normograma.adres.gov.co/compilacion/aprende_adres_guias.html
Adaptado para manejar certificados SSL y estructura específica de ADRES
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
import ssl
import urllib3
from urllib3.exceptions import InsecureRequestWarning

# Desactivar advertencias SSL para desarrollo
urllib3.disable_warnings(InsecureRequestWarning)

class DescargadorADRESGuias:
    """
    Descargador específicamente configurado para la página de guías ADRES
    """
    
    def __init__(self):
        self.url_objetivo = "https://normograma.adres.gov.co/compilacion/aprende_adres_guias.html"
        self.config = self._configurar_descargador()
        self.logger = self._configurar_logging()
        self.directorio_descargas = "data/descargas_adres_guias"
        self.metadatos_archivos = []
        
    def _configurar_descargador(self):
        """Configuración específica para ADRES con manejo SSL"""
        return {
            "headers_optimizados": {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Cache-Control': 'max-age=0'
            },
            "delay_peticiones": 3.0,
            "timeout": 30,
            "max_reintentos": 3,
            "verify_ssl": False,  # Desactivar verificación SSL para desarrollo
            "max_size_mb": 100,
            "tipos_archivo": ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']
        }
    
    def _configurar_logging(self):
        """Configurar logging"""
        logger = logging.getLogger('ADRESGuias')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def crear_directorios(self):
        """Crear directorios necesarios"""
        Path(self.directorio_descargas).mkdir(parents=True, exist_ok=True)
        Path(os.path.join(self.directorio_descargas, "pdfs")).mkdir(parents=True, exist_ok=True)
        Path(os.path.join(self.directorio_descargas, "documentos")).mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Directorios creados en: {self.directorio_descargas}")
    
    def explorar_pagina_guias(self):
        """
        Explorar la página de guías ADRES específica
        """
        print(f"🔍 EXPLORANDO: {self.url_objetivo}")
        print("=" * 70)
        
        try:
            # Configurar sesión con manejo SSL
            session = requests.Session()
            session.verify = False  # Desactivar verificación SSL
            
            # Respetar delay
            time.sleep(self.config["delay_peticiones"])
            
            # Realizar petición
            response = session.get(
                self.url_objetivo,
                headers=self.config["headers_optimizados"],
                timeout=self.config["timeout"]
            )
            
            print(f"📊 Código de respuesta: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Conexión exitosa a ADRES")
                return self._analizar_contenido_pagina(response, session)
            else:
                print(f"⚠️ Código de respuesta inesperado: {response.status_code}")
                return None
                
        except requests.exceptions.SSLError as e:
            print(f"🔒 Error SSL: {e}")
            print("💡 Intentando conexión sin verificación SSL...")
            return self._explorar_sin_ssl()
        except requests.exceptions.RequestException as e:
            print(f"🌐 Error de conexión: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error inesperado: {e}")
            return None
    
    def _explorar_sin_ssl(self):
        """Explorar usando requests sin verificación SSL"""
        try:
            # Configurar urllib3 para no verificar SSL
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            response = requests.get(
                self.url_objetivo,
                headers=self.config["headers_optimizados"],
                timeout=self.config["timeout"],
                verify=False,
                allow_redirects=True
            )
            
            print(f"📊 Respuesta sin SSL: {response.status_code}")
            
            if response.status_code == 200:
                return self._analizar_contenido_pagina(response, requests.Session())
            else:
                return None
                
        except Exception as e:
            print(f"❌ Error final: {e}")
            return None
    
    def _analizar_contenido_pagina(self, response, session):
        """Analizar el contenido HTML de la página"""
        
        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            print(f"📄 Título de página: {soup.title.string if soup.title else 'Sin título'}")
            print(f"📊 Tamaño del HTML: {len(response.text)} caracteres")
            
            # Buscar enlaces a documentos
            enlaces_documentos = self._buscar_enlaces_documentos(soup)
            
            # Buscar contenido estructurado
            contenido_estructurado = self._extraer_contenido_estructurado(soup)
            
            # Guardar análisis de la página
            self._guardar_analisis_pagina(soup, enlaces_documentos, contenido_estructurado)
            
            # Intentar descargar documentos encontrados
            if enlaces_documentos:
                return self._procesar_descargas(enlaces_documentos, session)
            else:
                print("⚠️ No se encontraron enlaces a documentos")
                return True
                
        except Exception as e:
            print(f"❌ Error analizando contenido: {e}")
            return False
    
    def _buscar_enlaces_documentos(self, soup):
        """Buscar enlaces a documentos (PDF, DOC, etc.)"""
        
        enlaces_encontrados = []
        
        print("\n🔍 BUSCANDO DOCUMENTOS...")
        print("-" * 40)
        
        # Buscar todos los enlaces
        todos_los_enlaces = soup.find_all('a', href=True)
        print(f"📋 Total de enlaces encontrados: {len(todos_los_enlaces)}")
        
        for enlace in todos_los_enlaces:
            href = enlace.get('href', '')
            texto = enlace.get_text(strip=True)
            
            # Verificar si es un enlace a documento
            for tipo_archivo in self.config["tipos_archivo"]:
                if tipo_archivo.lower() in href.lower():
                    url_completa = urllib.parse.urljoin(self.url_objetivo, href)
                    
                    enlaces_encontrados.append({
                        'url': url_completa,
                        'tipo': tipo_archivo,
                        'texto': texto,
                        'href_original': href
                    })
                    
                    print(f"📄 Encontrado {tipo_archivo.upper()}: {texto[:50]}...")
                    break
        
        print(f"\n📊 Documentos encontrados: {len(enlaces_encontrados)}")
        return enlaces_encontrados
    
    def _extraer_contenido_estructurado(self, soup):
        """Extraer contenido estructurado de la página"""
        
        contenido = {
            'titulo_pagina': soup.title.string if soup.title else '',
            'headings': [],
            'parrafos': [],
            'listas': [],
            'tablas': []
        }
        
        # Extraer headings
        for nivel in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            headings = soup.find_all(nivel)
            for h in headings:
                contenido['headings'].append({
                    'nivel': nivel,
                    'texto': h.get_text(strip=True)
                })
        
        # Extraer párrafos principales
        parrafos = soup.find_all('p')
        for p in parrafos[:10]:  # Limitar a los primeros 10 párrafos
            texto = p.get_text(strip=True)
            if len(texto) > 50:  # Solo párrafos significativos
                contenido['parrafos'].append(texto)
        
        # Extraer listas
        listas = soup.find_all(['ul', 'ol'])
        for lista in listas[:5]:  # Limitar a 5 listas
            items = [li.get_text(strip=True) for li in lista.find_all('li')]
            if items:
                contenido['listas'].append(items)
        
        # Extraer tablas
        tablas = soup.find_all('table')
        for tabla in tablas[:3]:  # Limitar a 3 tablas
            filas = []
            for tr in tabla.find_all('tr')[:10]:  # Máximo 10 filas por tabla
                celdas = [td.get_text(strip=True) for td in tr.find_all(['td', 'th'])]
                if celdas:
                    filas.append(celdas)
            if filas:
                contenido['tablas'].append(filas)
        
        return contenido
    
    def _procesar_descargas(self, enlaces_documentos, session):
        """Procesar las descargas de documentos encontrados"""
        
        print(f"\n📥 INICIANDO DESCARGAS...")
        print("=" * 40)
        
        descargas_exitosas = 0
        
        for i, documento in enumerate(enlaces_documentos, 1):
            print(f"\n📄 Descarga {i}/{len(enlaces_documentos)}")
            print(f"📋 Tipo: {documento['tipo'].upper()}")
            print(f"🔗 URL: {documento['url']}")
            
            if self._descargar_documento(documento, session):
                descargas_exitosas += 1
        
        print(f"\n📊 RESUMEN DE DESCARGAS:")
        print(f"✅ Exitosas: {descargas_exitosas}")
        print(f"📄 Total intentos: {len(enlaces_documentos)}")
        
        return descargas_exitosas > 0
    
    def _descargar_documento(self, documento, session):
        """Descargar un documento específico"""
        
        try:
            # Generar nombre de archivo
            nombre_archivo = self._generar_nombre_archivo(documento)
            
            # Determinar subdirectorio
            if documento['tipo'].lower() == '.pdf':
                subdirectorio = "pdfs"
            else:
                subdirectorio = "documentos"
            
            ruta_archivo = os.path.join(self.directorio_descargas, subdirectorio, nombre_archivo)
            
            # Verificar si ya existe
            if os.path.exists(ruta_archivo):
                print(f"⚠️ Archivo ya existe: {nombre_archivo}")
                return True
            
            # Respetar delay
            time.sleep(self.config["delay_peticiones"])
            
            # Descargar
            response = session.get(
                documento['url'],
                headers=self.config["headers_optimizados"],
                timeout=self.config["timeout"],
                stream=True,
                verify=False
            )
            
            if response.status_code == 200:
                # Verificar tamaño
                content_length = response.headers.get('content-length')
                if content_length and int(content_length) > (self.config["max_size_mb"] * 1024 * 1024):
                    print(f"⚠️ Archivo muy grande, omitiendo")
                    return False
                
                # Guardar archivo
                with open(ruta_archivo, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                # Verificar descarga
                if os.path.exists(ruta_archivo) and os.path.getsize(ruta_archivo) > 0:
                    size_kb = os.path.getsize(ruta_archivo) / 1024
                    print(f"✅ Descargado: {nombre_archivo} ({size_kb:.1f} KB)")
                    
                    # Guardar metadatos
                    self.metadatos_archivos.append({
                        'nombre_archivo': nombre_archivo,
                        'ruta_local': ruta_archivo,
                        'url_original': documento['url'],
                        'tipo_archivo': documento['tipo'],
                        'texto_enlace': documento['texto'],
                        'fecha_descarga': datetime.now().isoformat(),
                        'tamaño_bytes': os.path.getsize(ruta_archivo)
                    })
                    
                    return True
                else:
                    print(f"❌ Error: archivo no se guardó correctamente")
                    return False
            else:
                print(f"❌ Error HTTP: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error descargando: {e}")
            return False
    
    def _generar_nombre_archivo(self, documento):
        """Generar nombre de archivo seguro"""
        
        # Extraer nombre base
        nombre_url = os.path.basename(urllib.parse.urlparse(documento['url']).path)
        
        if nombre_url and any(ext in nombre_url.lower() for ext in self.config["tipos_archivo"]):
            nombre_base = nombre_url
        else:
            # Usar texto del enlace
            texto_limpio = "".join(c for c in documento['texto'] if c.isalnum() or c in (' ', '-', '_')).strip()
            texto_limpio = texto_limpio[:40]  # Limitar longitud
            nombre_base = f"{texto_limpio}{documento['tipo']}"
        
        # Agregar timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{timestamp}_{nombre_base}"
    
    def _guardar_analisis_pagina(self, soup, enlaces, contenido):
        """Guardar análisis completo de la página"""
        
        analisis = {
            'url_analizada': self.url_objetivo,
            'fecha_analisis': datetime.now().isoformat(),
            'titulo_pagina': soup.title.string if soup.title else '',
            'total_enlaces': len(soup.find_all('a')),
            'documentos_encontrados': len(enlaces),
            'tipos_documentos': list(set([doc['tipo'] for doc in enlaces])),
            'contenido_estructurado': contenido,
            'enlaces_documentos': enlaces
        }
        
        archivo_analisis = os.path.join(self.directorio_descargas, "analisis_pagina.json")
        
        with open(archivo_analisis, 'w', encoding='utf-8') as f:
            json.dump(analisis, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Análisis guardado: {archivo_analisis}")
    
    def ejecutar_descarga_completa(self):
        """Ejecutar el proceso completo de descarga"""
        
        print("🎓 TALLER BIG DATA - DESCARGADOR ADRES GUÍAS")
        print("🔗 URL objetivo: https://normograma.adres.gov.co/compilacion/aprende_adres_guias.html")
        print("=" * 80)
        
        # Crear directorios
        self.crear_directorios()
        
        # Explorar página
        resultado = self.explorar_pagina_guias()
        
        if resultado:
            # Guardar metadatos finales
            self._guardar_metadatos_finales()
            
            print(f"\n🎉 ¡PROCESO COMPLETADO EXITOSAMENTE!")
            print(f"📁 Archivos en: {self.directorio_descargas}")
            return True
        else:
            print(f"\n❌ Error en el proceso de descarga")
            return False
    
    def _guardar_metadatos_finales(self):
        """Guardar metadatos finales del proceso"""
        
        metadatos_finales = {
            'fecha_proceso': datetime.now().isoformat(),
            'url_objetivo': self.url_objetivo,
            'directorio_descargas': self.directorio_descargas,
            'total_archivos_descargados': len(self.metadatos_archivos),
            'archivos': self.metadatos_archivos
        }
        
        archivo_metadatos = os.path.join(self.directorio_descargas, "metadatos_descarga.json")
        
        with open(archivo_metadatos, 'w', encoding='utf-8') as f:
            json.dump(metadatos_finales, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Metadatos finales: {archivo_metadatos}")

def main():
    """Función principal"""
    descargador = DescargadorADRESGuias()
    return descargador.ejecutar_descarga_completa()

if __name__ == "__main__":
    main()