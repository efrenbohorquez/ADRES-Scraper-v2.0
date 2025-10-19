#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Taller de Big Data - Web Scraping Ético y Profesional
=====================================================

Autor: Taller Big Data 2024
Fecha: Octubre 2025
Objetivo: Demostrar técnicas de web scraping ético aplicadas al sitio de ADRES

Este script implementa las mejores prácticas de web scraping:
- Respeto por los recursos del servidor
- Manejo adecuado de errores y excepciones
- Headers apropiados para evitar ser detectado como bot malicioso
- Retrasos configurables para prevenir DoS
- Extracción limpia y profesional del contenido

URL objetivo: https://normograma.adres.gov.co/compilacion/docs/concepto_adres_20241209688471_2024.html
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import os
from datetime import datetime
import logging
from typing import Dict, Optional, Any

# Importar MongoDB Manager
try:
    from .mongodb_manager import MongoDBManager, crear_instancia_mongodb
    MONGODB_DISPONIBLE = True
except ImportError:
    try:
        from mongodb_manager import MongoDBManager, crear_instancia_mongodb
        MONGODB_DISPONIBLE = True
    except ImportError:
        MONGODB_DISPONIBLE = False
        MongoDBManager = None

# ----------------------------------------------------------------------
# 1. Configuración Ética y Profesional
# ----------------------------------------------------------------------

class ConfiguracionEticaADRES:
    """
    Clase de configuración para el web scraping ético de ADRES
    """
    
    # 1.1 URL de destino
    URL_OBJETIVO = "https://normograma.adres.gov.co/compilacion/docs/concepto_adres_20241209688471_2024.html"
    
    # 1.2 Encabezados (Headers) éticos para identificarse apropiadamente
    # Transparencia total: identificamos claramente el propósito académico
    HEADERS = {
        'User-Agent': 'Taller-BigData-Educativo/1.0 (Propósito: Investigación Académica; Universidad)',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
        'Accept-Language': 'es-ES,es;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'From': 'taller-bigdata@universidad.edu',
        'Purpose': 'Academic Research - Data Science Educational Project'
    }
    
    # 1.3 Retraso (Delay): CRÍTICO para no afectar ADRES
    # Delay conservador para máximo respeto al servidor
    DELAY_SECONDS = 2.0  # 2 segundos mínimo entre peticiones
    
    # 1.4 Configuración de timeouts conservadores
    REQUEST_TIMEOUT = 15  # Timeout generoso para evitar errores innecesarios
    
    # 1.5 Máximo número de reintentos para evitar loops infinitos
    MAX_RETRIES = 2
    
    # 1.6 Configuración de User-Agent rotation para evitar detección
    RESPECTFUL_USER_AGENTS = [
        'Taller-BigData-Educativo/1.0 (Propósito: Investigación Académica)',
        'Academic-Research-Bot/1.0 (Universidad; Análisis de Datos Públicos)',
        'Educational-Web-Scraper/1.0 (Curso Big Data; Uso Responsable)'
    ]
    
    # 1.5 Directorio de salida
    OUTPUT_DIR = 'web_scraping_adres_output'


class WebScraperADRES:
    """
    Clase principal para el web scraping ético de documentos de ADRES
    """
    
    def __init__(self, config: ConfiguracionEticaADRES = None, usar_mongodb: bool = False):
        """
        Inicializar el scraper con configuración ética
        
        Args:
            config: Instancia de ConfiguracionEticaADRES o None para usar la configuración por defecto
            usar_mongodb: Si True, intentará conectar y usar MongoDB para almacenamiento
        """
        self.config = config or ConfiguracionEticaADRES()
        self.usar_mongodb = usar_mongodb and MONGODB_DISPONIBLE
        self.mongodb_manager = None
        self._setup_logging()
        
        # Configurar MongoDB si está disponible y se solicita
        if self.usar_mongodb:
            self._configurar_mongodb()
    
    def _configurar_mongodb(self):
        """Configurar y conectar a MongoDB"""
        try:
            if MONGODB_DISPONIBLE:
                self.mongodb_manager = crear_instancia_mongodb()
                if self.mongodb_manager.conectar():
                    self.logger.info("✅ MongoDB configurado y conectado correctamente")
                else:
                    self.logger.warning("⚠️ No se pudo conectar a MongoDB, continuando sin almacenamiento en BD")
                    self.mongodb_manager = None
                    self.usar_mongodb = False
            else:
                self.logger.warning("⚠️ PyMongo no disponible, continuando sin MongoDB")
                self.usar_mongodb = False
        except Exception as e:
            self.logger.warning("⚠️ Error configurando MongoDB: %s. Continuando sin BD", e)
            self.mongodb_manager = None
            self.usar_mongodb = False
        
    def _setup_logging(self):
        """
        Configurar el sistema de logging para auditoría y debugging
        """
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('web_scraper_adres.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def _validar_url_adres(self, url: str) -> bool:
        """Validar que la URL pertenezca a ADRES para prevenir ataques"""
        dominios_permitidos = ['normograma.adres.gov.co', 'adres.gov.co']
        try:
            from urllib.parse import urlparse
            parsed_url = urlparse(url)
            return any(dominio in parsed_url.netloc for dominio in dominios_permitidos)
        except Exception:
            return False

    def extraer_contenido_adres(self, url: str) -> Dict[str, Any]:
        """
        Realiza una solicitud HTTP ética y extrae el texto principal de la URL dada.
        PREVIENE LOOPS INFINITOS con control estricto de reintentos.
        
        Args:
            url: URL del documento de ADRES a procesar
            
        Returns:
            Diccionario con el contenido extraído y metadatos del proceso
        """
        
        self.logger.info("Iniciando extracción ética de: %s", url)
        
        # PREVENCIÓN DE LOOPS: Validar URL antes de procesar
        if not self._validar_url_adres(url):
            return {
                'url_original': url,
                'status': 'Error de Validación',
                'detalle': 'URL no válida o no pertenece al dominio autorizado de ADRES',
                'fecha_extraccion': datetime.now().isoformat()
            }
        
        # Aplicar delay conservador para NO AFECTAR ADRES
        print(f"⏱️ Esperando {self.config.DELAY_SECONDS} segundos para respetar servidor ADRES...")
        time.sleep(self.config.DELAY_SECONDS)
        
        # Control de reintentos para evitar loops infinitos
        for intento in range(self.config.MAX_RETRIES + 1):
            try:
                if intento > 0:
                    delay_adicional = intento * 2  # Backoff exponencial
                    print(f"🔄 Intento {intento + 1}/{self.config.MAX_RETRIES + 1} - Esperando {delay_adicional}s adicionales...")
                    time.sleep(delay_adicional)
                
                # Petición HTTP GET con headers éticos
                self.logger.info("Realizando petición HTTP con headers apropiados...")
                response = requests.get(
                    url, 
                    headers=self.config.HEADERS, 
                    timeout=self.config.REQUEST_TIMEOUT,
                    allow_redirects=False  # Prevenir redirects infinitos
                )
                
                # Verificar si la respuesta fue exitosa (código 200)
                response.raise_for_status() 
                self.logger.info("Petición exitosa. Código de respuesta: %s", response.status_code)
                
                # Verificar que tenemos contenido HTML válido
                if not response.content or len(response.content) < 100:
                    raise ValueError("Contenido HTML insuficiente o vacío")
                
                # Creación del objeto BeautifulSoup (DOM) con manejo de encoding
                soup = BeautifulSoup(response.text, 'lxml')
                
                # Identificación del contenedor principal
                contenido_principal = self._encontrar_contenedor_principal(soup)
                
                if contenido_principal:
                    # Extraer todo el texto dentro del contenedor
                    texto_extraido = self._limpiar_texto(contenido_principal)
                    
                    # Formatear la salida con metadatos completos
                    data = {
                        'url_original': url,
                        'fecha_extraccion': datetime.now().isoformat(),
                        'timestamp_unix': int(time.time()),
                        'texto_completo': texto_extraido,
                        'longitud_caracteres': len(texto_extraido),
                        'longitud_palabras': len(texto_extraido.split()),
                        'status': 'OK',
                        'intentos_realizados': intento + 1,
                        'metadatos_http': {
                            'status_code': response.status_code,
                            'content_type': response.headers.get('content-type', 'unknown'),
                            'encoding': response.encoding
                        }
                    }
                    
                    self.logger.info("Extracción completada. Caracteres: %s", len(texto_extraido))
                    return data
                else:
                    # Si es el último intento y no encontramos contenido
                    if intento == self.config.MAX_RETRIES:
                        error_msg = 'No se encontró el contenedor principal después de múltiples intentos.'
                        self.logger.error(error_msg)
                        return {
                            'url_original': url, 
                            'status': 'Error', 
                            'detalle': error_msg,
                            'intentos_realizados': intento + 1,
                            'fecha_extraccion': datetime.now().isoformat()
                        }
                    else:
                        # Continuar con el siguiente intento
                        self.logger.warning("Contenedor no encontrado en intento %s. Reintentando...", intento + 1)
                        continue

            except requests.exceptions.HTTPError as e:
                # Si es el último intento, devolver error
                if intento == self.config.MAX_RETRIES:
                    error_msg = f"Error HTTP después de {intento + 1} intentos: {e}"
                    self.logger.error(error_msg)
                    return {
                        'url_original': url, 
                        'status': 'Error HTTP', 
                        'detalle': error_msg,
                        'intentos_realizados': intento + 1,
                        'fecha_extraccion': datetime.now().isoformat()
                    }
                else:
                    self.logger.warning("Error HTTP en intento %s: %s. Reintentando...", intento + 1, e)
                    continue
            
            except requests.exceptions.RequestException as e:
                # Si es el último intento, devolver error
                if intento == self.config.MAX_RETRIES:
                    error_msg = f"Error de conexión después de {intento + 1} intentos: {e}"
                    self.logger.error(error_msg)
                    return {
                        'url_original': url, 
                        'status': 'Error de Conexión', 
                        'detalle': error_msg,
                        'intentos_realizados': intento + 1,
                        'fecha_extraccion': datetime.now().isoformat()
                    }
                else:
                    self.logger.warning("Error de conexión en intento %s: %s. Reintentando...", intento + 1, e)
                    continue
            
            except ValueError as e:
                # Si es el último intento, devolver error
                if intento == self.config.MAX_RETRIES:
                    error_msg = f"Error de validación después de {intento + 1} intentos: {e}"
                    self.logger.error(error_msg)
                    return {
                        'url_original': url, 
                        'status': 'Error de Validación', 
                        'detalle': error_msg,
                        'intentos_realizados': intento + 1,
                        'fecha_extraccion': datetime.now().isoformat()
                    }
                else:
                    self.logger.warning("Error de validación en intento %s: %s. Reintentando...", intento + 1, e)
                    continue
        
        # Si llegamos aquí, todos los intentos fallaron
        return {
            'url_original': url, 
            'status': 'Error', 
            'detalle': 'Todos los intentos de extracción fallaron',
            'intentos_realizados': self.config.MAX_RETRIES + 1,
            'fecha_extraccion': datetime.now().isoformat()
        }

    def _encontrar_contenedor_principal(self, soup: BeautifulSoup) -> Optional[Any]:
        """
        Encuentra el contenedor principal del documento usando múltiples estrategias
        
        Args:
            soup: Objeto BeautifulSoup del documento HTML
            
        Returns:
            Elemento HTML que contiene el contenido principal o None
        """
        
        # Lista de selectores a probar, ordenados por especificidad
        selectores_candidatos = [
            # Selectores específicos comunes en sitios gubernamentales
            {'selector': 'div', 'attrs': {'id': 'content-wrapper'}},
            {'selector': 'div', 'attrs': {'id': 'main-content'}}, 
            {'selector': 'div', 'attrs': {'class': 'content'}},
            {'selector': 'div', 'attrs': {'class': 'main-content'}},
            {'selector': 'div', 'attrs': {'class': 'document-content'}},
            {'selector': 'div', 'attrs': {'class': 'texto-concepto'}},
            {'selector': 'div', 'attrs': {'class': 'contenido-normograma'}},
            
            # Selectores HTML5 semánticos
            {'selector': 'main'},
            {'selector': 'article'},
            {'selector': 'section'},
            
            # Fallbacks más generales
            {'selector': 'div', 'attrs': {'id': 'container'}},
            {'selector': 'div', 'attrs': {'class': 'container'}},
        ]
        
        for selector_info in selectores_candidatos:
            if 'attrs' in selector_info:
                contenedor = soup.find(selector_info['selector'], selector_info['attrs'])
            else:
                contenedor = soup.find(selector_info['selector'])
                
            if contenedor and contenedor.get_text(strip=True):
                self.logger.info(f"Contenedor encontrado: {selector_info}")
                return contenedor
        
        # Si no encontramos ningún contenedor específico, usar el body como último recurso
        self.logger.warning("No se encontró contenedor específico. Usando body como fallback.")
        return soup.find('body')

    def _limpiar_texto(self, contenedor) -> str:
        """
        Limpia y formatea el texto extraído del contenedor HTML
        
        Args:
            contenedor: Elemento HTML con el contenido
            
        Returns:
            Texto limpio y formateado
        """
        
        # Remover elementos no deseados antes de la extracción de texto
        elementos_a_remover = ['script', 'style', 'nav', 'header', 'footer', 'aside']
        
        for elemento in elementos_a_remover:
            for tag in contenedor.find_all(elemento):
                tag.decompose()
        
        # Extraer texto con separadores de línea
        texto = contenedor.get_text(separator='\n', strip=True)
        
        # Limpiar líneas vacías múltiples
        lineas = [linea.strip() for linea in texto.split('\n') if linea.strip()]
        texto_limpio = '\n'.join(lineas)
        
        return texto_limpio

    def procesar_documento(self, url: str = None, guardar_archivo: bool = True, 
                          guardar_mongodb: bool = True) -> Dict[str, Any]:
        """
        Método principal para procesar un documento de ADRES
        
        Args:
            url: URL a procesar (usa la configurada por defecto si es None)
            guardar_archivo: Si True, guarda el resultado en archivo JSON
            guardar_mongodb: Si True y MongoDB está disponible, almacena en la base de datos
            
        Returns:
            Resultado de la extracción
        """
        
        url_objetivo = url or self.config.URL_OBJETIVO
        
        # Procesar la URL
        resultado_extraccion = self.extraer_contenido_adres(url_objetivo)
        
        if resultado_extraccion.get('status') == 'OK':
            # Guardar en archivo JSON si se solicita
            if guardar_archivo:
                ruta_archivo = self._guardar_resultado(resultado_extraccion)
                resultado_extraccion['archivo_json'] = ruta_archivo
            
            # Almacenar en MongoDB si está disponible y se solicita
            if guardar_mongodb and self.usar_mongodb and self.mongodb_manager:
                mongodb_id = self._almacenar_en_mongodb(resultado_extraccion)
                if mongodb_id:
                    resultado_extraccion['mongodb_id'] = mongodb_id
                    self.logger.info("✅ Documento almacenado en MongoDB con ID: %s", mongodb_id)
            
        return resultado_extraccion

    def _almacenar_en_mongodb(self, documento: Dict[str, Any]) -> Optional[str]:
        """
        Almacenar el documento extraído en MongoDB
        
        Args:
            documento: Diccionario con los datos del documento
            
        Returns:
            ID del documento almacenado en MongoDB o None si falló
        """
        try:
            if self.mongodb_manager:
                return self.mongodb_manager.almacenar_documento(documento)
            return None
        except Exception as e:
            self.logger.warning("⚠️ Error almacenando en MongoDB: %s", e)
            return None

    def _guardar_resultado(self, resultado: Dict[str, Any]) -> str:
        """
        Guarda el resultado de la extracción en formato JSON
        
        Args:
            resultado: Diccionario con el resultado de la extracción
            
        Returns:
            Ruta del archivo guardado
        """
        
        # Crear directorio de salida si no existe
        os.makedirs(self.config.OUTPUT_DIR, exist_ok=True)
        
        # Generar nombre de archivo con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f'concepto_adres_{timestamp}.json'
        ruta_archivo = os.path.join(self.config.OUTPUT_DIR, nombre_archivo)
        
        try:
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                json.dump(resultado, f, indent=4, ensure_ascii=False)
                
            self.logger.info(f"Resultado guardado en: {ruta_archivo}")
            print(f"✅ Proceso finalizado exitosamente. Contenido guardado en: {ruta_archivo}")
            
            return ruta_archivo
            
        except Exception as e:
            error_msg = f"Error al guardar el archivo JSON: {e}"
            self.logger.error(error_msg)
            print(f"❌ {error_msg}")
            raise

    def cerrar_conexiones(self):
        """Cerrar todas las conexiones activas"""
        if self.mongodb_manager:
            self.mongodb_manager.cerrar_conexion()
            self.logger.info("✅ Conexiones cerradas correctamente")


# ----------------------------------------------------------------------
# 3. Punto de Entrada Principal
# ----------------------------------------------------------------------

def main():
    """
    Función principal para ejecutar el web scraper de ADRES con soporte MongoDB
    """
    
    print("=" * 70)
    print("🎓 TALLER DE BIG DATA - WEB SCRAPING ÉTICO PROFESIONAL")
    print("📋 Extracción de Contenido de ADRES con MongoDB")
    print("=" * 70)
    
    # Detectar si MongoDB está disponible
    mongodb_disponible = MONGODB_DISPONIBLE
    
    try:
        # Crear instancia del scraper con MongoDB si está disponible
        print(f"\n🔧 Configurando scraper...")
        print(f"   • MongoDB disponible: {'✅ Sí' if mongodb_disponible else '❌ No (continúa sin BD)'}")
        
        scraper = WebScraperADRES(usar_mongodb=mongodb_disponible)
        
        # Procesar el documento
        resultado = scraper.procesar_documento()
        
        # Mostrar resumen de resultados
        if resultado.get('status') == 'OK':
            print("\n📊 RESUMEN DE EXTRACCIÓN:")
            print(f"   • URL procesada: {resultado['url_original']}")
            print(f"   • Caracteres extraídos: {resultado['longitud_caracteres']:,}")
            print(f"   • Palabras extraídas: {resultado['longitud_palabras']:,}")
            print(f"   • Intentos realizados: {resultado.get('intentos_realizados', 1)}")
            print(f"   • Fecha de extracción: {resultado['fecha_extraccion']}")
            
            # Información de almacenamiento
            if 'archivo_json' in resultado:
                print(f"   • Archivo JSON: {resultado['archivo_json']}")
            if 'mongodb_id' in resultado:
                print(f"   • MongoDB ID: {resultado['mongodb_id']}")
            
            print("\n✅ Extracción completada exitosamente siguiendo principios éticos.")
            print("   ⏱️ Delays implementados para NO AFECTAR servidor ADRES")
            print("   🛡️ Validación de dominio para prevenir loops")
            print("   🔄 Sistema de reintentos controlado")
            
        else:
            print(f"\n❌ Error en la extracción: {resultado.get('detalle', 'Error desconocido')}")
            
        # Cerrar conexiones
        scraper.cerrar_conexiones()
            
    except Exception as e:
        print(f"\n❌ Error crítico en la ejecución: {e}")
        print("💡 Sugerencias:")
        print("   • Verifica tu conexión a internet")
        print("   • Si usas MongoDB, asegúrate de que esté ejecutándose")
        print("   • Revisa que todas las dependencias estén instaladas")
        return 1
    
    return 0

# Bloque de ejecución removido - módulo de librería
# Para ejecutar el scraper, importar y usar las clases desde otro script
