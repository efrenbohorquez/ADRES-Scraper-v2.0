#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Taller de Big Data - Gestor de MongoDB para Datos de ADRES
=========================================================

Autor: Taller Big Data 2024
Fecha: Octubre 2025
Objetivo: Gestionar el almacenamiento de datos extraídos de ADRES en MongoDB

Este módulo implementa:
- Conexión segura a MongoDB local o en la nube
- Almacenamiento estructurado de documentos de ADRES
- Consultas y análisis de datos almacenados
- Validación de datos antes del almacenamiento
- Funciones de backup y recuperación
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

try:
    import pymongo
    from pymongo import MongoClient
    from pymongo.collection import Collection
    from pymongo.database import Database
    from pymongo.errors import ConnectionFailure, DuplicateKeyError, BulkWriteError
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    MongoClient = None
    Collection = None
    Database = None


@dataclass
class DocumentoADRES:
    """
    Estructura de datos para documentos de ADRES almacenados en MongoDB
    """
    id_documento: str
    url_original: str
    titulo: Optional[str]
    fecha_extraccion: str
    fecha_documento: Optional[str]
    tipo_documento: str
    texto_completo: str
    longitud_caracteres: int
    longitud_palabras: int
    metadatos_http: Dict[str, Any]
    analisis_contenido: Optional[Dict[str, Any]] = None
    palabras_clave: Optional[List[str]] = None
    terminos_juridicos: Optional[List[str]] = None
    estado_procesamiento: str = "extraido"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para MongoDB"""
        return asdict(self)


class ConfiguracionMongoDB:
    """
    Configuración para la conexión a MongoDB
    """
    
    # Configuración por defecto para MongoDB local
    DEFAULT_HOST = "localhost"
    DEFAULT_PORT = 27017
    DEFAULT_DATABASE = "taller_bigdata_adres"
    DEFAULT_COLLECTION = "documentos_adres"
    
    # Configuración para MongoDB Atlas (nube) - Usuario específico
    ATLAS_CONNECTION_STRING = "mongodb+srv://efrenbohorquezv_db_user:Central2025@cluster0.ljpppvo.mongodb.net/"
    
    ATLAS_CONNECTION_STRING_TEMPLATE = (
        "mongodb+srv://{username}:{password}@{cluster}.mongodb.net/"
        "{database}?retryWrites=true&w=majority"
    )
    
    def __init__(self, 
                 host: str = DEFAULT_HOST,
                 port: int = DEFAULT_PORT,
                 database: str = DEFAULT_DATABASE,
                 collection: str = DEFAULT_COLLECTION,
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 connection_string: Optional[str] = None):
        """
        Inicializar configuración de MongoDB
        
        Args:
            host: Dirección del servidor MongoDB
            port: Puerto de conexión
            database: Nombre de la base de datos
            collection: Nombre de la colección principal
            username: Usuario (opcional para autenticación)
            password: Contraseña (opcional para autenticación)
            connection_string: String de conexión completo (opcional, sobrescribe otros parámetros)
        """
        self.host = host
        self.port = port
        self.database_name = database
        self.collection_name = collection
        self.username = username
        self.password = password
        self.connection_string = connection_string
        
    def get_connection_string(self) -> str:
        """Obtener string de conexión apropiado"""
        if self.connection_string:
            return self.connection_string
        
        # Usar Atlas por defecto para este proyecto
        if hasattr(self, 'ATLAS_CONNECTION_STRING'):
            return self.ATLAS_CONNECTION_STRING + self.database_name
        
        if self.username and self.password:
            return f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}/{self.database_name}"
        else:
            return f"mongodb://{self.host}:{self.port}/"


class MongoDBManager:
    """
    Gestor principal para operaciones con MongoDB
    """
    
    def __init__(self, config: ConfiguracionMongoDB = None):
        """
        Inicializar el gestor de MongoDB
        
        Args:
            config: Configuración de MongoDB o None para usar configuración por defecto
        """
        if not MONGODB_AVAILABLE:
            raise ImportError(
                "PyMongo no está instalado. Instala con: pip install pymongo dnspython"
            )
        
        self.config = config or ConfiguracionMongoDB()
        self.client: Optional[MongoClient] = None
        self.database: Optional[Database] = None
        self.collection: Optional[Collection] = None
        self.logger = self._setup_logging()
        
    def _setup_logging(self) -> logging.Logger:
        """Configurar logging específico para MongoDB"""
        logger = logging.getLogger(f"{__name__}.MongoDB")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
        
    def conectar(self) -> bool:
        """
        Establecer conexión con MongoDB
        
        Returns:
            True si la conexión fue exitosa, False en caso contrario
        """
        try:
            connection_string = self.config.get_connection_string()
            self.logger.info("Intentando conectar a MongoDB: %s", 
                           connection_string.replace(self.config.password or '', '***'))
            
            # Configurar cliente con timeout apropiado
            self.client = MongoClient(
                connection_string,
                serverSelectionTimeoutMS=5000,  # 5 segundos timeout
                connectTimeoutMS=5000,
                maxPoolSize=10
            )
            
            # Verificar conexión
            self.client.admin.command('ping')
            self.logger.info("✅ Conexión a MongoDB establecida exitosamente")
            
            # Obtener base de datos y colección
            self.database = self.client[self.config.database_name]
            self.collection = self.database[self.config.collection_name]
            
            # Crear índices necesarios
            self._crear_indices()
            
            return True
            
        except ConnectionFailure as e:
            self.logger.error("❌ Error de conexión a MongoDB: %s", e)
            return False
        except Exception as e:
            self.logger.error("❌ Error inesperado conectando a MongoDB: %s", e)
            return False
    
    def _crear_indices(self):
        """Crear índices necesarios para optimizar consultas"""
        try:
            # Índice único por URL para evitar duplicados
            self.collection.create_index("url_original", unique=True)
            
            # Índices para búsquedas frecuentes
            self.collection.create_index("fecha_extraccion")
            self.collection.create_index("tipo_documento")
            self.collection.create_index("estado_procesamiento")
            
            # Índice de texto completo para búsquedas
            self.collection.create_index([("titulo", "text"), ("texto_completo", "text")])
            
            self.logger.info("✅ Índices de MongoDB creados/verificados correctamente")
            
        except Exception as e:
            self.logger.warning("⚠️ Error creando índices: %s", e)
    
    def almacenar_documento(self, documento: Dict[str, Any]) -> Optional[str]:
        """
        Almacenar un documento extraído de ADRES
        
        Args:
            documento: Diccionario con los datos del documento
            
        Returns:
            ID del documento almacenado o None si falló
        """
        if not self.collection:
            self.logger.error("No hay conexión activa a MongoDB")
            return None
        
        try:
            # Preparar documento para MongoDB
            doc_preparado = self._preparar_documento(documento)
            
            # Intentar insertar
            resultado = self.collection.insert_one(doc_preparado)
            
            self.logger.info("✅ Documento almacenado con ID: %s", resultado.inserted_id)
            return str(resultado.inserted_id)
            
        except DuplicateKeyError:
            # Documento ya existe, intentar actualizar
            self.logger.warning("⚠️ Documento ya existe, actualizando...")
            return self._actualizar_documento_existente(doc_preparado)
            
        except Exception as e:
            self.logger.error("❌ Error almacenando documento: %s", e)
            return None
    
    def _preparar_documento(self, documento: Dict[str, Any]) -> Dict[str, Any]:
        """Preparar documento para almacenamiento en MongoDB"""
        doc_preparado = documento.copy()
        
        # Asegurar ID único
        if 'id_documento' not in doc_preparado:
            doc_preparado['id_documento'] = self._generar_id_documento(documento)
        
        # Agregar timestamp de almacenamiento
        doc_preparado['fecha_almacenamiento'] = datetime.now(timezone.utc).isoformat()
        
        # Extraer título si no existe
        if 'titulo' not in doc_preparado or not doc_preparado['titulo']:
            doc_preparado['titulo'] = self._extraer_titulo(documento.get('texto_completo', ''))
        
        # Clasificar tipo de documento
        if 'tipo_documento' not in doc_preparado:
            doc_preparado['tipo_documento'] = self._clasificar_tipo_documento(documento)
        
        return doc_preparado
    
    def _generar_id_documento(self, documento: Dict[str, Any]) -> str:
        """Generar ID único para el documento"""
        url = documento.get('url_original', '')
        fecha = documento.get('fecha_extraccion', '')
        
        # Usar hash de la URL + fecha para generar ID único
        import hashlib
        contenido_hash = f"{url}_{fecha}"
        return hashlib.md5(contenido_hash.encode()).hexdigest()
    
    def _extraer_titulo(self, texto: str) -> str:
        """Extraer título del texto del documento"""
        if not texto:
            return "Sin título"
        
        # Tomar las primeras líneas no vacías como título
        lineas = [linea.strip() for linea in texto.split('\n') if linea.strip()]
        if lineas:
            titulo = lineas[0]
            # Limitar longitud del título
            return titulo[:100] + '...' if len(titulo) > 100 else titulo
        
        return "Sin título"
    
    def _clasificar_tipo_documento(self, documento: Dict[str, Any]) -> str:
        """Clasificar el tipo de documento basado en contenido y URL"""
        url = documento.get('url_original', '').lower()
        texto = documento.get('texto_completo', '').lower()
        
        if 'concepto' in url or 'concepto' in texto:
            return 'concepto_juridico'
        elif 'resolucion' in url or 'resolución' in texto:
            return 'resolucion'
        elif 'circular' in url or 'circular' in texto:
            return 'circular'
        elif 'decreto' in url or 'decreto' in texto:
            return 'decreto'
        else:
            return 'documento_normativo'
    
    def _actualizar_documento_existente(self, documento: Dict[str, Any]) -> Optional[str]:
        """Actualizar un documento que ya existe"""
        try:
            filtro = {'url_original': documento['url_original']}
            documento['fecha_actualizacion'] = datetime.now(timezone.utc).isoformat()
            
            resultado = self.collection.update_one(
                filtro,
                {'$set': documento},
                upsert=True
            )
            
            self.logger.info("✅ Documento actualizado para URL: %s", documento['url_original'])
            return documento.get('id_documento')
            
        except Exception as e:
            self.logger.error("❌ Error actualizando documento: %s", e)
            return None
    
    def buscar_documentos(self, 
                         filtro: Optional[Dict[str, Any]] = None,
                         limite: int = 10,
                         orden: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Buscar documentos en la colección
        
        Args:
            filtro: Filtros de búsqueda (opcional)
            limite: Número máximo de resultados
            orden: Campo por el cual ordenar (opcional)
            
        Returns:
            Lista de documentos encontrados
        """
        if not self.collection:
            self.logger.error("No hay conexión activa a MongoDB")
            return []
        
        try:
            query = filtro or {}
            cursor = self.collection.find(query).limit(limite)
            
            if orden:
                direccion = -1 if orden.startswith('-') else 1
                campo = orden.lstrip('-')
                cursor = cursor.sort(campo, direccion)
            
            documentos = list(cursor)
            
            # Convertir ObjectId a string para serialización
            for doc in documentos:
                if '_id' in doc:
                    doc['_id'] = str(doc['_id'])
            
            self.logger.info("✅ Encontrados %d documentos", len(documentos))
            return documentos
            
        except Exception as e:
            self.logger.error("❌ Error buscando documentos: %s", e)
            return []
    
    def buscar_por_texto(self, texto_busqueda: str, limite: int = 10) -> List[Dict[str, Any]]:
        """
        Buscar documentos por texto completo
        
        Args:
            texto_busqueda: Texto a buscar
            limite: Número máximo de resultados
            
        Returns:
            Lista de documentos encontrados
        """
        try:
            cursor = self.collection.find(
                {"$text": {"$search": texto_busqueda}},
                {"score": {"$meta": "textScore"}}
            ).sort([("score", {"$meta": "textScore"})]).limit(limite)
            
            documentos = list(cursor)
            
            # Convertir ObjectId a string
            for doc in documentos:
                if '_id' in doc:
                    doc['_id'] = str(doc['_id'])
            
            self.logger.info("✅ Búsqueda de texto encontró %d documentos", len(documentos))
            return documentos
            
        except Exception as e:
            self.logger.error("❌ Error en búsqueda de texto: %s", e)
            return []
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """
        Obtener estadísticas de la colección
        
        Returns:
            Diccionario con estadísticas
        """
        if not self.collection:
            return {}
        
        try:
            # Estadísticas básicas
            total_documentos = self.collection.count_documents({})
            
            # Estadísticas por tipo de documento
            pipeline_tipos = [
                {"$group": {
                    "_id": "$tipo_documento",
                    "count": {"$sum": 1}
                }},
                {"$sort": {"count": -1}}
            ]
            tipos_documento = list(self.collection.aggregate(pipeline_tipos))
            
            # Estadísticas por fecha
            pipeline_fechas = [
                {"$group": {
                    "_id": {"$dateToString": {
                        "format": "%Y-%m-%d",
                        "date": {"$dateFromString": {"dateString": "$fecha_extraccion"}}
                    }},
                    "count": {"$sum": 1}
                }},
                {"$sort": {"_id": -1}},
                {"$limit": 10}
            ]
            extracciones_por_fecha = list(self.collection.aggregate(pipeline_fechas))
            
            estadisticas = {
                'total_documentos': total_documentos,
                'tipos_documento': tipos_documento,
                'extracciones_recientes': extracciones_por_fecha,
                'fecha_consulta': datetime.now().isoformat()
            }
            
            self.logger.info("✅ Estadísticas obtenidas correctamente")
            return estadisticas
            
        except Exception as e:
            self.logger.error("❌ Error obteniendo estadísticas: %s", e)
            return {}
    
    def exportar_datos(self, formato: str = 'json', 
                      filtro: Optional[Dict[str, Any]] = None,
                      archivo_salida: Optional[str] = None) -> str:
        """
        Exportar datos a archivo
        
        Args:
            formato: Formato de exportación ('json' o 'csv')
            filtro: Filtros para la exportación (opcional)
            archivo_salida: Nombre del archivo de salida (opcional)
            
        Returns:
            Ruta del archivo generado
        """
        if not self.collection:
            raise ValueError("No hay conexión activa a MongoDB")
        
        try:
            # Obtener datos
            documentos = self.buscar_documentos(filtro, limite=1000)
            
            # Generar nombre de archivo si no se proporciona
            if not archivo_salida:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                archivo_salida = f"export_adres_{timestamp}.{formato}"
            
            # Crear directorio de salida si no existe
            os.makedirs('exports', exist_ok=True)
            ruta_completa = os.path.join('exports', archivo_salida)
            
            if formato.lower() == 'json':
                with open(ruta_completa, 'w', encoding='utf-8') as f:
                    json.dump(documentos, f, indent=2, ensure_ascii=False, default=str)
            
            elif formato.lower() == 'csv':
                import pandas as pd
                df = pd.DataFrame(documentos)
                df.to_csv(ruta_completa, index=False, encoding='utf-8')
            
            else:
                raise ValueError(f"Formato no soportado: {formato}")
            
            self.logger.info("✅ Datos exportados a: %s", ruta_completa)
            return ruta_completa
            
        except Exception as e:
            self.logger.error("❌ Error exportando datos: %s", e)
            raise
    
    def crear_backup(self) -> str:
        """
        Crear backup completo de la colección
        
        Returns:
            Ruta del archivo de backup
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.exportar_datos(
            formato='json',
            archivo_salida=f'backup_adres_{timestamp}.json'
        )
    
    def cerrar_conexion(self):
        """Cerrar la conexión a MongoDB"""
        if self.client:
            self.client.close()
            self.logger.info("✅ Conexión a MongoDB cerrada")


def crear_instancia_mongodb(connection_string: Optional[str] = None) -> MongoDBManager:
    """
    Función auxiliar para crear una instancia de MongoDB Manager
    
    Args:
        connection_string: String de conexión opcional
        
    Returns:
        Instancia configurada de MongoDBManager
    """
    if connection_string:
        config = ConfiguracionMongoDB(connection_string=connection_string)
    else:
        # Usar configuración por defecto (MongoDB local)
        config = ConfiguracionMongoDB()
    
    return MongoDBManager(config)


def main():
    """Función de prueba del módulo MongoDB"""
    print("🧪 Probando conexión y funcionalidad de MongoDB...")
    
    try:
        # Crear gestor
        mongo_manager = crear_instancia_mongodb()
        
        # Conectar
        if mongo_manager.conectar():
            print("✅ Conexión exitosa a MongoDB")
            
            # Obtener estadísticas
            stats = mongo_manager.obtener_estadisticas()
            print(f"📊 Total de documentos: {stats.get('total_documentos', 0)}")
            
            # Cerrar conexión
            mongo_manager.cerrar_conexion()
        else:
            print("❌ No se pudo conectar a MongoDB")
            print("💡 Asegúrate de que MongoDB esté ejecutándose localmente")
            print("   o proporciona un string de conexión válido.")
    
    except ImportError:
        print("❌ PyMongo no está instalado")
        print("💡 Instala con: pip install pymongo dnspython")
    
    except Exception as e:
        print(f"❌ Error: {e}")

# Bloque de ejecución removido - módulo de librería
