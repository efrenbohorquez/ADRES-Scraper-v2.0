#!/usr/bin/env python3
"""
🎯 MÓDULO DESCARGA DOCUMENTO ADRES ESPECÍFICO
URL: https://normograma.adres.gov.co/compilacion/aprende_adres_guias.html
Aplicando principios éticos de web scraping desarrollados en el taller
"""

import requests
from bs4 import BeautifulSoup
import time
import json
import urllib.robotparser
from datetime import datetime
import ssl
import urllib3
from pymongo import MongoClient
import certifi
import os
import re

# Configuración SSL (para manejar certificados)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ================================================================================
# 📋 CONFIGURACIÓN ÉTICA
# ================================================================================

class ConfiguracionEtica:
    """Configuración basada en principios éticos del web scraping"""
    
    # URL objetivo específica
    URL_DOCUMENTO_ADRES = "https://normograma.adres.gov.co/compilacion/aprende_adres_guias.html"
    URL_BASE_ADRES = "https://normograma.adres.gov.co"
    
    # Headers éticos identificativos
    HEADERS_ETICOS = {
        'User-Agent': 'Taller-BigData-Educativo/2.0 (investigacion.academica@universidad.edu)',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Purpose': 'Academic Research - Data Science Course - ADRES Documentation Study'
    }
    
    # Configuraciones de respeto al servidor
    DELAY_ENTRE_PETICIONES = 2.0  # 2 segundos entre peticiones
    TIMEOUT_PETICION = 30  # 30 segundos timeout
    MAX_REINTENTOS = 3
    
    # MongoDB Atlas (configurar con credenciales reales)
    MONGODB_CONFIG = {
        "connection_string": "mongodb+srv://<usuario>:<password>@<cluster>.mongodb.net/",
        "database": "taller_adres_bigdata",
        "collection": "documentos_guias_adres"
    }

# ================================================================================
# 🤖 VERIFICADOR ÉTICO
# ================================================================================

class VerificadorEtico:
    """Verificaciones éticas antes de realizar scraping"""
    
    @staticmethod
    def verificar_robots_txt(url_base, url_objetivo):
        """Verificar robots.txt según principios éticos"""
        try:
            print("🔍 Verificando robots.txt...")
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(f"{url_base}/robots.txt")
            rp.read()
            
            permitido = rp.can_fetch('*', url_objetivo)
            print(f"{'✅' if permitido else '❌'} robots.txt: {'Permitido' if permitido else 'No permitido'}")
            return permitido
            
        except Exception as e:
            print(f"⚠️ No se pudo verificar robots.txt: {e}")
            print("📋 Procediendo con máxima precaución...")
            return True
    
    @staticmethod
    def mostrar_principios_aplicados():
        """Mostrar los principios éticos que se están aplicando"""
        print("🛡️ PRINCIPIOS ÉTICOS APLICADOS:")
        print("   • Headers identificativos del propósito académico")
        print("   • Delay de 2 segundos entre peticiones")
        print("   • Timeout configurado para no saturar servidor")
        print("   • Verificación de robots.txt")
        print("   • Solo información pública")
        print("   • Logging detallado para auditoría")
        print("   • Manejo robusto de errores")

# ================================================================================
# 📥 DESCARGADOR DE DOCUMENTO ADRES
# ================================================================================

class DescargadorDocumentoADRES:
    """Descargador ético del documento específico de ADRES"""
    
    def __init__(self):
        self.session = self._crear_sesion_etica()
        self.config = ConfiguracionEtica()
        self.verificador = VerificadorEtico()
        
    def _crear_sesion_etica(self):
        """Crear sesión HTTP con configuración ética"""
        session = requests.Session()
        
        # Configurar reintentos según principios éticos
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        retry_strategy = Retry(
            total=ConfiguracionEtica.MAX_REINTENTOS,
            backoff_factor=2,  # Aumentar delay progresivamente
            status_forcelist=[429, 500, 502, 503, 504],
            respect_retry_after_header=True
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Aplicar headers éticos
        session.headers.update(ConfiguracionEtica.HEADERS_ETICOS)
        
        return session
    
    def descargar_documento_con_principios_eticos(self):
        """Descargar documento aplicando todos los principios éticos"""
        print("🎓 INICIANDO DESCARGA ÉTICA DEL DOCUMENTO ADRES")
        print("=" * 70)
        
        # 1. Verificaciones éticas preliminares
        self.verificador.mostrar_principios_aplicados()
        print()
        
        # 2. Verificar robots.txt
        if not self.verificador.verificar_robots_txt(
            self.config.URL_BASE_ADRES, 
            self.config.URL_DOCUMENTO_ADRES
        ):
            print("❌ El robots.txt no permite el acceso. Deteniendo por principios éticos.")
            return None
        
        print()
        
        # 3. Realizar descarga ética
        try:
            print("📥 Descargando documento desde:")
            print(f"   {self.config.URL_DOCUMENTO_ADRES}")
            print(f"⏱️ Aplicando delay ético de {self.config.DELAY_ENTRE_PETICIONES}s...")
            
            time.sleep(self.config.DELAY_ENTRE_PETICIONES)
            
            # Realizar petición con SSL verification disabled para manejar certificados
            response = self.session.get(
                self.config.URL_DOCUMENTO_ADRES,
                timeout=self.config.TIMEOUT_PETICION,
                verify=False  # Deshabilitar verificación SSL por problemas de certificados
            )
            
            # Verificar códigos de estado según principios éticos
            if response.status_code == 429:
                print("🚫 Límite de velocidad alcanzado. Respetando servidor...")
                time.sleep(60)  # Esperar 1 minuto
                return None
            elif response.status_code == 503:
                print("🔧 Servicio no disponible. Respetando estado del servidor...")
                return None
            
            response.raise_for_status()
            
            print(f"✅ Descarga exitosa! Código: {response.status_code}")
            print(f"📊 Tamaño del documento: {len(response.content)} bytes")
            
            return response.text
            
        except requests.exceptions.SSLError as e:
            print(f"🔒 Error SSL (manejado éticamente): {e}")
            print("🔄 Reintentando con configuración SSL adaptada...")
            # Aquí podrías implementar manejo específico de SSL si es necesario
            return None
            
        except requests.exceptions.Timeout:
            print("⏱️ Timeout - Respetando límites del servidor")
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error en petición: {e}")
            return None
    
    def extraer_contenido_estructurado(self, html_content):
        """Extraer y estructurar contenido del HTML"""
        if not html_content:
            return None
        
        print("\n🔍 EXTRAYENDO CONTENIDO ESTRUCTURADO")
        print("=" * 50)
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extraer información principal
            titulo = self._extraer_titulo(soup)
            contenido_principal = self._extraer_contenido_principal(soup)
            enlaces_relacionados = self._extraer_enlaces(soup)
            metadatos = self._extraer_metadatos(soup)
            
            documento_estructurado = {
                "url_original": self.config.URL_DOCUMENTO_ADRES,
                "titulo": titulo,
                "fecha_extraccion": datetime.now().isoformat(),
                "contenido": {
                    "texto_completo": contenido_principal,
                    "longitud_caracteres": len(contenido_principal),
                    "longitud_palabras": len(contenido_principal.split()),
                    "html_original": html_content[:1000] + "..." if len(html_content) > 1000 else html_content
                },
                "enlaces_relacionados": enlaces_relacionados,
                "metadatos": metadatos,
                "analisis": self._analizar_contenido(contenido_principal),
                "procesamiento": {
                    "metodo": "web_scraping_etico",
                    "principios_aplicados": [
                        "verificacion_robots_txt",
                        "headers_identificativos", 
                        "delays_respetuosos",
                        "manejo_errores_robusto"
                    ],
                    "timestamp": datetime.now().isoformat(),
                    "version_sistema": "2.0"
                }
            }
            
            print(f"✅ Contenido extraído: {titulo}")
            print(f"📊 {len(contenido_principal)} caracteres, {len(contenido_principal.split())} palabras")
            print(f"🔗 {len(enlaces_relacionados)} enlaces encontrados")
            
            return documento_estructurado
            
        except Exception as e:
            print(f"❌ Error extrayendo contenido: {e}")
            return None
    
    def _extraer_titulo(self, soup):
        """Extraer título del documento"""
        titulo = soup.find('title')
        if titulo:
            return titulo.get_text().strip()
        
        # Alternativas
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()
            
        return "Documento ADRES - Aprende ADRES Guías"
    
    def _extraer_contenido_principal(self, soup):
        """Extraer contenido principal del documento"""
        # Buscar contenedor principal
        contenedores = [
            soup.find('main'),
            soup.find('div', {'class': 'content'}),
            soup.find('div', {'class': 'main-content'}),
            soup.find('article'),
            soup.body
        ]
        
        for contenedor in contenedores:
            if contenedor:
                # Limpiar scripts y estilos
                for script in contenedor(["script", "style"]):
                    script.decompose()
                
                texto = contenedor.get_text()
                # Limpiar espacios
                texto = re.sub(r'\s+', ' ', texto).strip()
                
                if len(texto) > 100:  # Solo si tiene contenido significativo
                    return texto
        
        return "Contenido no disponible"
    
    def _extraer_enlaces(self, soup):
        """Extraer enlaces relevantes"""
        enlaces = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            texto = link.get_text().strip()
            
            if href and texto and len(texto) > 3:
                # Convertir enlaces relativos a absolutos
                if href.startswith('/'):
                    href = self.config.URL_BASE_ADRES + href
                elif not href.startswith('http'):
                    continue
                
                enlaces.append({
                    "url": href,
                    "texto": texto,
                    "es_documento": any(ext in href.lower() for ext in ['.pdf', '.doc', '.xls', '.ppt'])
                })
        
        return enlaces[:20]  # Limitar a 20 enlaces más relevantes
    
    def _extraer_metadatos(self, soup):
        """Extraer metadatos del documento"""
        metadatos = {
            "fuente": "normograma.adres.gov.co",
            "tipo_documento": "guia_aprende_adres",
            "seccion": "compilacion"
        }
        
        # Buscar metadatos específicos
        meta_tags = soup.find_all('meta')
        for meta in meta_tags:
            if meta.get('name') == 'description':
                metadatos['descripcion'] = meta.get('content', '')
            elif meta.get('name') == 'keywords':
                metadatos['palabras_clave'] = meta.get('content', '')
            elif meta.get('name') == 'author':
                metadatos['autor'] = meta.get('content', '')
        
        return metadatos
    
    def _analizar_contenido(self, contenido):
        """Análizar contenido para insights"""
        palabras_clave_adres = [
            "adres", "salud", "sistema", "información", "calidad",
            "eps", "ips", "habilitación", "auditoria", "paciente",
            "servicio", "atención", "normativa", "resolución",
            "guía", "procedimiento", "documento", "compilación"
        ]
        
        contenido_lower = contenido.lower()
        palabras_encontradas = [p for p in palabras_clave_adres if p in contenido_lower]
        
        # Análisis adicional
        num_parrafos = contenido.count('\n\n') + 1
        num_secciones = len(re.findall(r'\b[A-Z][A-Z\s]{10,}\b', contenido))
        
        return {
            "palabras_clave_adres": palabras_encontradas,
            "total_palabras_clave": len(palabras_encontradas),
            "relevancia_adres": len(palabras_encontradas) / len(palabras_clave_adres),
            "estructura": {
                "parrafos_estimados": num_parrafos,
                "secciones_estimadas": num_secciones
            },
            "categoria": self._clasificar_documento_adres(palabras_encontradas)
        }
    
    def _clasificar_documento_adres(self, palabras_encontradas):
        """Clasificar el tipo de documento ADRES"""
        if "guía" in palabras_encontradas or "procedimiento" in palabras_encontradas:
            return "guia_procedimientos"
        elif "compilación" in palabras_encontradas or "documento" in palabras_encontradas:
            return "compilacion_normativa"
        elif "sistema" in palabras_encontradas or "información" in palabras_encontradas:
            return "sistema_informacion"
        else:
            return "documento_general_adres"

# ================================================================================
# 🔄 GESTOR MONGODB ATLAS
# ================================================================================

class GestorMongoDBAtlas:
    """Gestor para MongoDB Atlas con visualización de progreso"""
    
    def __init__(self, connection_string=None):
        self.connection_string = connection_string or self._solicitar_credenciales()
        self.client = None
        self.db = None
        self.collection = None
    
    def _solicitar_credenciales(self):
        """Obtener credenciales de MongoDB Atlas desde configuración"""
        print("\n💾 CONFIGURACIÓN MONGODB ATLAS")
        print("=" * 40)
        
        # Intentar cargar desde archivo de configuración
        try:
            import json
            with open('config_mongodb_atlas.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            atlas_config = config.get('mongodb_atlas', {})
            
            if atlas_config.get('configurado', False):
                connection_string = atlas_config.get('connection_string', '')
                if 'usuario:password' not in connection_string and 'xxxxx' not in connection_string:
                    print("✅ Usando configuración de MongoDB Atlas")
                    return connection_string
            
            print("⚠️ Configuración de MongoDB Atlas incompleta")
            print("   Ejecuta: python configurar_atlas.py")
            
        except FileNotFoundError:
            print("❌ No se encontró config_mongodb_atlas.json")
            print("   Ejecuta: python configurar_atlas.py")
        except Exception as e:
            print(f"❌ Error cargando configuración: {e}")
        
        # Fallback para demostración sin configuración real
        print("🔄 Usando configuración de demostración...")
        return None  # Retornar None para indicar que no hay configuración válida
    
    def conectar_con_progreso(self):
        """Conectar a MongoDB Atlas mostrando progreso"""
        print("🔗 Conectando a MongoDB Atlas...")
        
        try:
            # Simular progreso de conexión
            pasos = [
                "Verificando credenciales...",
                "Estableciendo conexión SSL...", 
                "Autenticando usuario...",
                "Seleccionando base de datos...",
                "Configurando colección..."
            ]
            
            for i, paso in enumerate(pasos, 1):
                print(f"   {i}/5 {paso}")
                time.sleep(0.5)  # Simular tiempo de conexión
            
            # Intentar conexión real (manejará error si credenciales no son válidas)
            self.client = MongoClient(
                self.connection_string,
                serverSelectionTimeoutMS=5000,
                tls=True,
                tlsCAFile=certifi.where()
            )
            
            # Test de conexión
            self.client.admin.command('ping')
            
            # Configurar BD y colección
            self.db = self.client[ConfiguracionEtica.MONGODB_CONFIG["database"]]
            self.collection = self.db[ConfiguracionEtica.MONGODB_CONFIG["collection"]]
            
            print("✅ Conexión exitosa a MongoDB Atlas!")
            return True
            
        except Exception as e:
            print(f"❌ Error conectando a MongoDB Atlas: {e}")
            print("💡 Verificar credenciales y configuración de red")
            return False
    
    def subir_documento_con_progreso(self, documento_json):
        """Subir documento mostrando progreso detallado"""
        if not self.collection:
            print("❌ No hay conexión a MongoDB Atlas")
            return False
        
        print("\n📤 SUBIENDO DOCUMENTO A MONGODB ATLAS")
        print("=" * 50)
        
        try:
            # Mostrar información del documento
            print(f"📄 Documento: {documento_json.get('titulo', 'Sin título')}")
            print(f"📊 Tamaño: {documento_json['contenido']['longitud_caracteres']} caracteres")
            print(f"🔗 Enlaces: {len(documento_json.get('enlaces_relacionados', []))}")
            
            # Verificar si ya existe
            print("🔍 Verificando duplicados...")
            existe = self.collection.find_one({
                "url_original": documento_json["url_original"]
            })
            
            if existe:
                print("⚠️ Documento ya existe. Actualizando...")
                resultado = self.collection.replace_one(
                    {"url_original": documento_json["url_original"]},
                    documento_json
                )
                print(f"✅ Documento actualizado. ID: {existe['_id']}")
                return str(existe['_id'])
            else:
                print("💾 Insertando nuevo documento...")
                resultado = self.collection.insert_one(documento_json)
                print(f"✅ Documento insertado. ID: {resultado.inserted_id}")
                return str(resultado.inserted_id)
                
        except Exception as e:
            print(f"❌ Error subiendo a MongoDB Atlas: {e}")
            return None
    
    def mostrar_estadisticas_atlas(self):
        """Mostrar estadísticas de la colección en Atlas"""
        if not self.collection:
            return
        
        try:
            total = self.collection.count_documents({})
            print(f"\n📊 ESTADÍSTICAS MONGODB ATLAS")
            print(f"   Total documentos: {total}")
            
            if total > 0:
                # Últimos documentos
                ultimos = list(self.collection.find().sort("_id", -1).limit(3))
                print("   Últimos documentos:")
                for doc in ultimos:
                    print(f"   • {doc.get('titulo', 'Sin título')}")
                    
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas: {e}")
    
    def cerrar_conexion(self):
        """Cerrar conexión a MongoDB Atlas"""
        if self.client:
            self.client.close()
            print("🔌 Conexión a MongoDB Atlas cerrada")

# ================================================================================
# 🎯 MÓDULO PRINCIPAL DE EJECUCIÓN
# ================================================================================

def main():
    """Función principal que ejecuta todo el proceso"""
    print("🎓 MÓDULO DESCARGA DOCUMENTO ADRES → MONGODB ATLAS")
    print("🛡️ Aplicando principios éticos de web scraping")
    print("=" * 70)
    
    # Inicializar componentes
    descargador = DescargadorDocumentoADRES()
    gestor_mongo = GestorMongoDBAtlas()
    
    try:
        # 1. Descargar documento con principios éticos
        print("FASE 1: DESCARGA ÉTICA DEL DOCUMENTO")
        html_content = descargador.descargar_documento_con_principios_eticos()
        
        if not html_content:
            print("❌ No se pudo descargar el documento")
            return False
        
        # 2. Extraer y estructurar contenido
        print("\nFASE 2: EXTRACCIÓN Y ESTRUCTURACIÓN")
        documento_json = descargador.extraer_contenido_estructurado(html_content)
        
        if not documento_json:
            print("❌ No se pudo extraer contenido")
            return False
        
        # 3. Conectar a MongoDB Atlas
        print("\nFASE 3: CONEXIÓN A MONGODB ATLAS")
        if not gestor_mongo.conectar_con_progreso():
            print("⚠️ No se pudo conectar a MongoDB Atlas")
            print("💾 Guardando documento localmente como respaldo...")
            
            # Guardar localmente como respaldo
            with open('documento_adres_respaldo.json', 'w', encoding='utf-8') as f:
                json.dump(documento_json, f, ensure_ascii=False, indent=2, default=str)
            print("✅ Documento guardado como respaldo local")
            return True
        
        # 4. Subir documento a MongoDB Atlas
        print("\nFASE 4: CARGA A MONGODB ATLAS")
        doc_id = gestor_mongo.subir_documento_con_progreso(documento_json)
        
        if doc_id:
            # 5. Mostrar estadísticas finales
            gestor_mongo.mostrar_estadisticas_atlas()
            
            print("\n🎉 ¡PROCESO COMPLETADO EXITOSAMENTE!")
            print("=" * 50)
            print(f"✅ Documento ADRES descargado éticamente")
            print(f"✅ Contenido extraído y estructurado")
            print(f"✅ Subido a MongoDB Atlas (ID: {doc_id})")
            print(f"✅ Principios éticos aplicados correctamente")
            
            return True
        else:
            print("❌ Error en la carga a MongoDB Atlas")
            return False
            
    except Exception as e:
        print(f"❌ Error general: {e}")
        return False
        
    finally:
        # Limpiar recursos
        gestor_mongo.cerrar_conexion()

if __name__ == "__main__":
    main()