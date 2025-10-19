#!/usr/bin/env python3
"""
🎯 SCRAPER ADRES OPTIMIZADO - EXTRACCIÓN A JSON PARA MONGODB
Objetivo: Leer documentos de ADRES → Convertir a JSON → Almacenar en MongoDB
Versión: Simplificada y optimizada para análisis
"""

import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from datetime import datetime
import json
import time
import logging
import re

# ================================================================================
# 📋 CONFIGURACIÓN PRINCIPAL
# ================================================================================

# MongoDB Local
MONGO_CONFIG = {
    "host": "localhost",
    "port": 27017,
    "database": "taller_bigdata_adres",
    "collection": "documentos_json"
}

# Headers éticos para el scraping
HEADERS_ETICOS = {
    'User-Agent': 'Taller-BigData-ADRES/1.0 (Propósito: Análisis Académico)',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'es-ES,es;q=0.9',
    'Connection': 'keep-alive'
}

# URLs de documentos ADRES para extraer
URLS_ADRES = [
    "https://normograma.adres.gov.co/adres/docs/resolucion_adres_2876_2013.htm",
    "https://normograma.adres.gov.co/adres/docs/resolucion_adres_0743_2013.htm",
    "https://normograma.adres.gov.co/adres/docs/resolucion_adres_2587_2012.htm"
]

# ================================================================================
# 🛡️ CONFIGURACIÓN DE LOGGING
# ================================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper_adres.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ================================================================================
# 🏠 CONEXIÓN MONGODB
# ================================================================================

class MongoDBManager:
    """Gestor optimizado de MongoDB"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        
    def conectar(self):
        """Establecer conexión con MongoDB local"""
        try:
            connection_string = f"mongodb://{MONGO_CONFIG['host']}:{MONGO_CONFIG['port']}/"
            self.client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
            
            # Test de conexión
            self.client.admin.command('ping')
            
            # Configurar base de datos y colección
            self.db = self.client[MONGO_CONFIG['database']]
            self.collection = self.db[MONGO_CONFIG['collection']]
            
            logger.info(f"✅ MongoDB conectado: {MONGO_CONFIG['database']}.{MONGO_CONFIG['collection']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error conectando MongoDB: {e}")
            return False
    
    def insertar_documento_json(self, documento_json):
        """Insertar documento JSON en MongoDB"""
        try:
            # Verificar si ya existe (evitar duplicados)
            existe = self.collection.find_one({"url_original": documento_json["url_original"]})
            
            if existe:
                logger.info(f"⚠️  Documento ya existe: {documento_json['url_original']}")
                return existe["_id"]
            
            # Insertar nuevo documento
            resultado = self.collection.insert_one(documento_json)
            logger.info(f"✅ Documento JSON insertado: {resultado.inserted_id}")
            return resultado.inserted_id
            
        except Exception as e:
            logger.error(f"❌ Error insertando JSON: {e}")
            return None
    
    def obtener_estadisticas(self):
        """Obtener estadísticas de la colección"""
        try:
            total = self.collection.count_documents({})
            recientes = list(self.collection.find().sort("fecha_extraccion", -1).limit(5))
            
            return {
                "total_documentos": total,
                "documentos_recientes": recientes
            }
        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas: {e}")
            return None
    
    def cerrar_conexion(self):
        """Cerrar conexión MongoDB"""
        if self.client:
            self.client.close()
            logger.info("🔌 Conexión MongoDB cerrada")

# ================================================================================
# 🕷️ SCRAPER DE DOCUMENTOS ADRES
# ================================================================================

class ScraperADRES:
    """Scraper optimizado para documentos ADRES"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS_ETICOS)
        self.mongo = MongoDBManager()
        
    def inicializar(self):
        """Inicializar conexiones necesarias"""
        return self.mongo.conectar()
    
    def extraer_documento(self, url):
        """Extraer y convertir documento ADRES a JSON"""
        try:
            logger.info(f"📄 Extrayendo: {url}")
            
            # Realizar petición HTTP con delay ético
            time.sleep(1)  # Delay ético de 1 segundo
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Parsear contenido HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extraer información estructurada
            documento_json = self._extraer_contenido_json(soup, url)
            
            return documento_json
            
        except Exception as e:
            logger.error(f"❌ Error extrayendo {url}: {e}")
            return None
    
    def _extraer_contenido_json(self, soup, url):
        """Convertir contenido HTML a estructura JSON optimizada"""
        
        # Extraer título del documento
        titulo = self._extraer_titulo(soup)
        
        # Extraer texto principal del documento
        contenido = self._extraer_contenido_principal(soup)
        
        # Extraer metadatos del documento
        metadatos = self._extraer_metadatos(soup, url)
        
        # Estructurar como JSON para análisis
        documento_json = {
            # Información básica
            "url_original": url,
            "titulo": titulo,
            "fecha_extraccion": datetime.now(),
            "timestamp_iso": datetime.now().isoformat(),
            
            # Contenido del documento
            "contenido": {
                "texto_completo": contenido,
                "longitud_caracteres": len(contenido),
                "longitud_palabras": len(contenido.split()) if contenido else 0
            },
            
            # Metadatos para análisis
            "metadatos": metadatos,
            
            # Análisis básico del texto
            "analisis": self._realizar_analisis_basico(titulo, contenido),
            
            # Información de procesamiento
            "procesamiento": {
                "version_scraper": "1.0_optimizada",
                "fecha_procesamiento": datetime.now().isoformat(),
                "estado": "procesado_exitosamente",
                "formato_salida": "json_estructurado"
            }
        }
        
        return documento_json
    
    def _extraer_titulo(self, soup):
        """Extraer título del documento"""
        # Buscar título en diferentes ubicaciones
        for selector in ['h1', 'title', '.titulo', '#titulo']:
            elemento = soup.select_one(selector)
            if elemento:
                titulo = elemento.get_text(strip=True)
                if titulo:
                    return titulo
        
        return "Sin título"
    
    def _extraer_contenido_principal(self, soup):
        """Extraer contenido principal del documento"""
        # Remover elementos no deseados
        for elemento in soup(['script', 'style', 'nav', 'footer', 'header']):
            elemento.decompose()
        
        # Buscar contenido principal
        contenido_principal = soup.find('body')
        if contenido_principal:
            texto = contenido_principal.get_text(separator='\n', strip=True)
            # Limpiar texto
            texto = re.sub(r'\n\s*\n', '\n\n', texto)  # Eliminar líneas vacías múltiples
            texto = re.sub(r' +', ' ', texto)  # Eliminar espacios múltiples
            return texto
        
        return "Sin contenido"
    
    def _extraer_metadatos(self, soup, url):
        """Extraer metadatos del documento"""
        metadatos = {
            "tipo_documento": "normativo_adres",
            "fuente": "normograma.adres.gov.co",
            "categoria": "resolucion" if "resolucion" in url.lower() else "documento",
        }
        
        # Buscar fecha en el contenido
        fecha_match = re.search(r'(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})', str(soup))
        if fecha_match:
            metadatos["fecha_documento"] = fecha_match.group(0)
        
        # Buscar número de resolución
        resolucion_match = re.search(r'resoluci[oó]n\s+n[oú]mero?\s*(\d+)', str(soup), re.IGNORECASE)
        if resolucion_match:
            metadatos["numero_resolucion"] = resolucion_match.group(1)
        
        return metadatos
    
    def _realizar_analisis_basico(self, titulo, contenido):
        """Realizar análisis básico del texto para facilitar consultas posteriores"""
        if not contenido:
            return {}
        
        # Palabras clave comunes en documentos normativos
        palabras_clave = [
            "resolución", "artículo", "decreto", "norma", "reglamento",
            "salud", "eps", "medicina", "hospital", "atención",
            "usuario", "paciente", "servicio", "calidad"
        ]
        
        contenido_lower = contenido.lower()
        palabras_encontradas = [palabra for palabra in palabras_clave if palabra in contenido_lower]
        
        return {
            "palabras_clave_encontradas": palabras_encontradas,
            "total_palabras_clave": len(palabras_encontradas),
            "densidad_palabras_clave": len(palabras_encontradas) / len(contenido.split()) if contenido.split() else 0,
            "contiene_articulos": "artículo" in contenido_lower or "artculo" in contenido_lower,
            "es_resolucion": "resolución" in contenido_lower or "resolucion" in contenido_lower
        }
    
    def procesar_urls(self, urls):
        """Procesar lista de URLs y almacenar en MongoDB"""
        resultados = []
        
        for i, url in enumerate(urls, 1):
            logger.info(f"📋 Procesando {i}/{len(urls)}: {url}")
            
            # Extraer documento
            documento_json = self.extraer_documento(url)
            
            if documento_json:
                # Almacenar en MongoDB
                doc_id = self.mongo.insertar_documento_json(documento_json)
                
                if doc_id:
                    resultados.append({
                        "url": url,
                        "id_mongodb": str(doc_id),
                        "estado": "exitoso",
                        "titulo": documento_json.get("titulo", "Sin título")
                    })
                else:
                    resultados.append({
                        "url": url,
                        "estado": "error_almacenamiento"
                    })
            else:
                resultados.append({
                    "url": url,
                    "estado": "error_extraccion"
                })
        
        return resultados
    
    def mostrar_resumen_final(self, resultados):
        """Mostrar resumen final del procesamiento"""
        logger.info("=" * 60)
        logger.info("📊 RESUMEN FINAL DEL PROCESAMIENTO")
        logger.info("=" * 60)
        
        exitosos = [r for r in resultados if r.get("estado") == "exitoso"]
        errores = [r for r in resultados if r.get("estado") != "exitoso"]
        
        logger.info(f"✅ Documentos procesados exitosamente: {len(exitosos)}")
        logger.info(f"❌ Documentos con errores: {len(errores)}")
        
        if exitosos:
            logger.info("\n📄 DOCUMENTOS ALMACENADOS EN MONGODB:")
            for doc in exitosos:
                logger.info(f"   • {doc['titulo']} (ID: {doc['id_mongodb']})")
        
        # Mostrar estadísticas de MongoDB
        stats = self.mongo.obtener_estadisticas()
        if stats:
            logger.info(f"\n📊 TOTAL EN BASE DE DATOS: {stats['total_documentos']} documentos")
    
    def finalizar(self):
        """Cerrar conexiones y limpiar recursos"""
        self.mongo.cerrar_conexion()
        self.session.close()

# ================================================================================
# 🎯 FUNCIÓN PRINCIPAL
# ================================================================================

def main():
    """Función principal optimizada"""
    logger.info("🎓 INICIANDO TALLER BIG DATA - SCRAPER ADRES OPTIMIZADO")
    logger.info("🎯 Objetivo: Documentos ADRES → JSON → MongoDB → Análisis")
    logger.info("=" * 70)
    
    # Crear instancia del scraper
    scraper = ScraperADRES()
    
    try:
        # Inicializar conexiones
        if not scraper.inicializar():
            logger.error("❌ Error inicializando el sistema")
            return False
        
        logger.info(f"📋 URLs a procesar: {len(URLS_ADRES)}")
        for i, url in enumerate(URLS_ADRES, 1):
            logger.info(f"   {i}. {url}")
        
        # Procesar todas las URLs
        logger.info("\n🚀 Iniciando procesamiento...")
        resultados = scraper.procesar_urls(URLS_ADRES)
        
        # Mostrar resumen final
        scraper.mostrar_resumen_final(resultados)
        
        logger.info("\n🎉 ¡PROCESAMIENTO COMPLETADO!")
        logger.info("💾 Los documentos están almacenados en MongoDB como JSON")
        logger.info("📊 Listos para análisis de big data")
        
        return True
        
    except KeyboardInterrupt:
        logger.warning("⚠️  Procesamiento interrumpido por el usuario")
        return False
        
    except Exception as e:
        logger.error(f"❌ Error durante el procesamiento: {e}")
        return False
        
    finally:
        scraper.finalizar()

# Bloque de ejecución removido - módulo de librería
# Para usar: importar ScraperADRES y funciones desde este módulo
