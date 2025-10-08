#!/usr/bin/env python3
"""
Gestor MongoDB Unificado para ADRES Scraper
==========================================
Gestión centralizada de operaciones con MongoDB Atlas
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
import hashlib

try:
    import pymongo
    from pymongo import MongoClient
    from pymongo.collection import Collection
    from pymongo.database import Database
    from pymongo.errors import ConnectionFailure, DuplicateKeyError, BulkWriteError
    import gridfs
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    MongoClient = None


@dataclass
class DocumentMetadata:
    """Metadatos para documentos almacenados"""
    url_original: str
    titulo: str
    fecha_extraccion: str
    tipo_documento: str
    longitud_caracteres: int
    longitud_palabras: int
    hash_contenido: str
    estado: str = "procesado"


class MongoDBManager:
    """
    Gestor unificado para operaciones con MongoDB Atlas
    """
    
    def __init__(self, connection_string: str, database_name: str):
        """
        Inicializar gestor MongoDB
        
        Args:
            connection_string: URI de conexión a MongoDB
            database_name: Nombre de la base de datos
        """
        if not MONGODB_AVAILABLE:
            raise ImportError("PyMongo no está disponible. Instala con: pip install pymongo")
        
        self.connection_string = connection_string
        self.database_name = database_name
        self.client: Optional[MongoClient] = None
        self.database: Optional[Database] = None
        self.gridfs: Optional[gridfs.GridFS] = None
        
        self.logger = logging.getLogger(__name__)
        
        # Nombres de colecciones
        self.collections = {
            'documents': 'resoluciones_adres',
            'pdf_files': 'pdfs_archivos', 
            'pdf_metadata': 'pdfs_metadatos',
            'download_sessions': 'metadatos_descargas',
            'analysis_results': 'resultados_analisis'
        }
    
    def connect(self) -> bool:
        """
        Establecer conexión con MongoDB
        
        Returns:
            True si la conexión es exitosa
        """
        try:
            self.client = MongoClient(self.connection_string, serverSelectionTimeoutMS=5000)
            
            # Verificar conexión
            self.client.admin.command('ping')
            
            # Configurar base de datos y GridFS
            self.database = self.client[self.database_name]
            self.gridfs = gridfs.GridFS(self.database, collection=self.collections['pdf_files'])
            
            self.logger.info(f"Conectado exitosamente a MongoDB: {self.database_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error conectando a MongoDB: {e}")
            return False
    
    def disconnect(self):
        """Cerrar conexión con MongoDB"""
        if self.client:
            self.client.close()
            self.client = None
            self.database = None
            self.gridfs = None
            self.logger.info("Conexión MongoDB cerrada")
    
    def is_connected(self) -> bool:
        """Verificar si hay conexión activa"""
        try:
            if self.client:
                self.client.admin.command('ping')
                return True
        except Exception:
            pass
        return False
    
    def store_document(self, document_data: Dict[str, Any]) -> Optional[str]:
        """
        Almacenar documento de texto en MongoDB
        
        Args:
            document_data: Datos del documento extraído
            
        Returns:
            ID del documento insertado o None si falla
        """
        if not self.is_connected():
            if not self.connect():
                return None
        
        try:
            collection = self.database[self.collections['documents']]
            
            # Preparar documento para inserción
            doc_to_insert = {
                **document_data,
                'fecha_almacenamiento': datetime.now().isoformat(),
                'hash_contenido': self._calculate_content_hash(document_data.get('texto_completo', '')),
                'version_scraper': '2.0.0'
            }
            
            # Verificar duplicados por hash
            existing = collection.find_one({'hash_contenido': doc_to_insert['hash_contenido']})
            if existing:
                self.logger.warning(f"Documento duplicado encontrado: {existing['_id']}")
                return str(existing['_id'])
            
            # Insertar documento
            result = collection.insert_one(doc_to_insert)
            
            self.logger.info(f"Documento almacenado con ID: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            self.logger.error(f"Error almacenando documento: {e}")
            return None
    
    def store_pdf_file(self, pdf_path: str, metadata: Dict[str, Any]) -> Optional[str]:
        """
        Almacenar archivo PDF en GridFS
        
        Args:
            pdf_path: Ruta al archivo PDF
            metadata: Metadatos del archivo
            
        Returns:
            ID del archivo en GridFS o None si falla
        """
        if not self.is_connected():
            if not self.connect():
                return None
        
        try:
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"Archivo no encontrado: {pdf_path}")
            
            # Leer archivo PDF
            with open(pdf_path, 'rb') as pdf_file:
                # Almacenar en GridFS con metadatos
                file_id = self.gridfs.put(
                    pdf_file.read(),
                    filename=os.path.basename(pdf_path),
                    contentType='application/pdf',
                    metadata={
                        **metadata,
                        'fecha_carga_mongodb': datetime.now().isoformat(),
                        'tamaño_bytes': os.path.getsize(pdf_path),
                        'hash_sha256': self._calculate_file_hash(pdf_path)
                    }
                )
            
            # Almacenar metadatos en colección separada
            metadata_doc = {
                'gridfs_id': str(file_id),
                'nombre_archivo': os.path.basename(pdf_path),
                'ruta_original': pdf_path,
                'fecha_carga': datetime.now().isoformat(),
                **metadata
            }
            
            metadata_collection = self.database[self.collections['pdf_metadata']]
            metadata_result = metadata_collection.insert_one(metadata_doc)
            
            self.logger.info(f"PDF almacenado - GridFS ID: {file_id}, Metadata ID: {metadata_result.inserted_id}")
            return str(file_id)
            
        except Exception as e:
            self.logger.error(f"Error almacenando PDF: {e}")
            return None
    
    def store_download_session(self, session_data: Dict[str, Any]) -> Optional[str]:
        """
        Almacenar información de sesión de descarga
        
        Args:
            session_data: Datos de la sesión de descarga
            
        Returns:
            ID de la sesión insertada o None si falla
        """
        if not self.is_connected():
            if not self.connect():
                return None
        
        try:
            collection = self.database[self.collections['download_sessions']]
            
            session_doc = {
                **session_data,
                'fecha_registro': datetime.now().isoformat(),
                'version_sistema': '2.0.0'
            }
            
            result = collection.insert_one(session_doc)
            
            self.logger.info(f"Sesión de descarga registrada: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            self.logger.error(f"Error registrando sesión: {e}")
            return None
    
    def get_documents(self, query: Dict[str, Any] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Obtener documentos de texto de la base de datos
        
        Args:
            query: Filtro de búsqueda (opcional)
            limit: Límite de documentos a retornar
            
        Returns:
            Lista de documentos encontrados
        """
        if not self.is_connected():
            if not self.connect():
                return []
        
        try:
            collection = self.database[self.collections['documents']]
            cursor = collection.find(query or {}).limit(limit)
            
            documents = list(cursor)
            
            # Convertir ObjectId a string para serialización
            for doc in documents:
                doc['_id'] = str(doc['_id'])
            
            return documents
            
        except Exception as e:
            self.logger.error(f"Error obteniendo documentos: {e}")
            return []
    
    def get_pdf_files(self, query: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Obtener información de archivos PDF
        
        Args:
            query: Filtro de búsqueda (opcional)
            
        Returns:
            Lista de metadatos de archivos PDF
        """
        if not self.is_connected():
            if not self.connect():
                return []
        
        try:
            # Buscar en GridFS files
            files_collection = self.database[f"{self.collections['pdf_files']}.files"]
            cursor = files_collection.find(query or {})
            
            files_info = []
            for file_doc in cursor:
                file_info = {
                    '_id': str(file_doc['_id']),
                    'filename': file_doc.get('filename', ''),
                    'uploadDate': file_doc.get('uploadDate'),
                    'length': file_doc.get('length', 0),
                    'contentType': file_doc.get('contentType', ''),
                    'metadata': file_doc.get('metadata', {})
                }
                files_info.append(file_info)
            
            return files_info
            
        except Exception as e:
            self.logger.error(f"Error obteniendo archivos PDF: {e}")
            return []
    
    def download_pdf_file(self, file_id: str, output_path: str) -> bool:
        """
        Descargar archivo PDF desde GridFS
        
        Args:
            file_id: ID del archivo en GridFS
            output_path: Ruta donde guardar el archivo
            
        Returns:
            True si la descarga es exitosa
        """
        if not self.is_connected():
            if not self.connect():
                return False
        
        try:
            from bson import ObjectId
            
            # Obtener archivo desde GridFS
            file_data = self.gridfs.get(ObjectId(file_id))
            
            # Crear directorio si no existe
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Escribir archivo
            with open(output_path, 'wb') as output_file:
                output_file.write(file_data.read())
            
            self.logger.info(f"Archivo descargado: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error descargando archivo PDF: {e}")
            return False
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Obtener estadísticas de la base de datos
        
        Returns:
            Diccionario con estadísticas
        """
        if not self.is_connected():
            if not self.connect():
                return {}
        
        try:
            stats = {}
            
            # Estadísticas generales de la base de datos
            db_stats = self.database.command("dbStats")
            stats['database'] = {
                'name': self.database_name,
                'collections': db_stats.get('collections', 0),
                'dataSize': db_stats.get('dataSize', 0),
                'storageSize': db_stats.get('storageSize', 0),
                'objects': db_stats.get('objects', 0)
            }
            
            # Estadísticas por colección
            stats['collections'] = {}
            for col_name in self.collections.values():
                try:
                    count = self.database[col_name].count_documents({})
                    stats['collections'][col_name] = count
                except Exception:
                    stats['collections'][col_name] = 0
            
            # Estadísticas de GridFS
            try:
                gridfs_files_count = self.database[f"{self.collections['pdf_files']}.files"].count_documents({})
                gridfs_chunks_count = self.database[f"{self.collections['pdf_files']}.chunks"].count_documents({})
                stats['gridfs'] = {
                    'files': gridfs_files_count,
                    'chunks': gridfs_chunks_count
                }
            except Exception:
                stats['gridfs'] = {'files': 0, 'chunks': 0}
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas: {e}")
            return {}
    
    def _calculate_content_hash(self, content: str) -> str:
        """Calcular hash del contenido para detectar duplicados"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calcular hash SHA256 de un archivo"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def search_documents(self, search_term: str, collection_type: str = 'documents') -> List[Dict[str, Any]]:
        """
        Buscar documentos por término de búsqueda
        
        Args:
            search_term: Término a buscar
            collection_type: Tipo de colección donde buscar
            
        Returns:
            Lista de documentos encontrados
        """
        if not self.is_connected():
            if not self.connect():
                return []
        
        try:
            collection = self.database[self.collections[collection_type]]
            
            # Búsqueda por texto
            query = {
                "$or": [
                    {"texto_completo": {"$regex": search_term, "$options": "i"}},
                    {"titulo": {"$regex": search_term, "$options": "i"}},
                    {"url_original": {"$regex": search_term, "$options": "i"}}
                ]
            }
            
            cursor = collection.find(query).limit(50)
            results = []
            
            for doc in cursor:
                doc['_id'] = str(doc['_id'])
                results.append(doc)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error en búsqueda: {e}")
            return []


def create_mongodb_manager(connection_string: str, database_name: str) -> Optional[MongoDBManager]:
    """
    Factory function para crear instancia de MongoDBManager
    
    Args:
        connection_string: URI de conexión
        database_name: Nombre de la base de datos
        
    Returns:
        Instancia de MongoDBManager o None si falla
    """
    try:
        manager = MongoDBManager(connection_string, database_name)
        if manager.connect():
            return manager
        return None
    except Exception as e:
        logging.error(f"Error creando MongoDB manager: {e}")
        return None