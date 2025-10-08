"""
Módulo de utilidades para el sistema ADRES Scraper.

Este módulo proporciona funciones auxiliares para:
- Manipulación de URLs
- Validación de archivos PDF
- Generación de hashes
- Normalización de texto
- Manejo de fechas
- Utilidades de sistema
"""

import os
import re
import hashlib
import logging
from datetime import datetime
from urllib.parse import urljoin, urlparse, parse_qs
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple


def normalizar_url(url: str) -> str:
    """
    Normaliza una URL eliminando parámetros innecesarios.
    
    Args:
        url: URL a normalizar
        
    Returns:
        URL normalizada
    """
    if not url or not isinstance(url, str):
        return ""
    
    # Eliminar espacios en blanco
    url = url.strip()
    
    # Asegurar protocolo
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    return url


def validar_url_pdf(url: str) -> bool:
    """
    Valida si una URL apunta a un archivo PDF.
    
    Args:
        url: URL a validar
        
    Returns:
        True si la URL parece ser de un PDF
    """
    if not url:
        return False
    
    # Verificar extensión
    if url.lower().endswith('.pdf'):
        return True
    
    # Verificar parámetros de consulta
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)
    
    # Buscar indicadores de PDF en parámetros
    for param, values in query_params.items():
        for value in values:
            if 'pdf' in value.lower():
                return True
    
    return False


def obtener_hash_archivo(contenido: bytes, algoritmo: str = 'sha256') -> str:
    """
    Genera un hash del contenido del archivo.
    
    Args:
        contenido: Contenido del archivo en bytes
        algoritmo: Algoritmo de hash a usar ('md5', 'sha1', 'sha256')
        
    Returns:
        Hash hexadecimal del contenido
    """
    if not contenido:
        return ""
    
    hash_obj = hashlib.new(algoritmo)
    hash_obj.update(contenido)
    return hash_obj.hexdigest()


def normalizar_texto(texto: str) -> str:
    """
    Normaliza texto eliminando caracteres especiales y espacios extra.
    
    Args:
        texto: Texto a normalizar
        
    Returns:
        Texto normalizado
    """
    if not texto:
        return ""
    
    # Eliminar espacios extra
    texto = re.sub(r'\s+', ' ', texto.strip())
    
    # Eliminar caracteres de control
    texto = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', texto)
    
    return texto


def extraer_numero_resolucion(texto: str) -> Optional[str]:
    """
    Extrae el número de resolución de un texto.
    
    Args:
        texto: Texto que puede contener un número de resolución
        
    Returns:
        Número de resolución encontrado o None
    """
    if not texto:
        return None
    
    # Patrones comunes para resoluciones
    patrones = [
        r'resolución\s*(?:no\.?\s*)?(\d+)',
        r'resolution\s*(?:no\.?\s*)?(\d+)',
        r'res\.?\s*(\d+)',
        r'n[oº]\.?\s*(\d+)'
    ]
    
    texto_lower = texto.lower()
    for patron in patrones:
        match = re.search(patron, texto_lower)
        if match:
            return match.group(1)
    
    return None


def formatear_fecha_actual() -> str:
    """
    Obtiene la fecha actual en formato estándar.
    
    Returns:
        Fecha actual en formato YYYY-MM-DD HH:MM:SS
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def formatear_fecha_archivo() -> str:
    """
    Obtiene timestamp para nombres de archivo.
    
    Returns:
        Timestamp en formato YYYYMMDD_HHMMSS
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def crear_directorio_seguro(ruta: str) -> bool:
    """
    Crea un directorio de forma segura.
    
    Args:
        ruta: Ruta del directorio a crear
        
    Returns:
        True si se creó exitosamente o ya existe
    """
    try:
        Path(ruta).mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False


def obtener_tamano_archivo(ruta: str) -> int:
    """
    Obtiene el tamaño de un archivo en bytes.
    
    Args:
        ruta: Ruta del archivo
        
    Returns:
        Tamaño en bytes o 0 si no existe
    """
    try:
        return os.path.getsize(ruta)
    except (OSError, FileNotFoundError):
        return 0


def formatear_bytes(bytes_count: int) -> str:
    """
    Formatea un número de bytes en una cadena legible.
    
    Args:
        bytes_count: Número de bytes
        
    Returns:
        Cadena formateada (ej: "1.5 MB")
    """
    if bytes_count == 0:
        return "0 B"
    
    unidades = ['B', 'KB', 'MB', 'GB', 'TB']
    i = 0
    size = float(bytes_count)
    
    while size >= 1024 and i < len(unidades) - 1:
        size /= 1024
        i += 1
    
    return f"{size:.1f} {unidades[i]}"


def limpiar_nombre_archivo(nombre: str) -> str:
    """
    Limpia un nombre de archivo eliminando caracteres no válidos.
    
    Args:
        nombre: Nombre original del archivo
        
    Returns:
        Nombre de archivo limpio
    """
    if not nombre:
        return "archivo_sin_nombre"
    
    # Eliminar caracteres no válidos para nombres de archivo
    nombre_limpio = re.sub(r'[<>:"/\\|?*]', '_', nombre)
    
    # Eliminar espacios extra y puntos al final
    nombre_limpio = re.sub(r'\s+', '_', nombre_limpio.strip(' .'))
    
    # Limitar longitud
    if len(nombre_limpio) > 200:
        nombre_limpio = nombre_limpio[:200]
    
    return nombre_limpio or "archivo_sin_nombre"


def generar_metadatos_basicos(url: str, contenido: bytes) -> Dict[str, Any]:
    """
    Genera metadatos básicos para un archivo descargado.
    
    Args:
        url: URL de origen
        contenido: Contenido del archivo
        
    Returns:
        Diccionario con metadatos básicos
    """
    return {
        'url_origen': url,
        'hash_sha256': obtener_hash_archivo(contenido, 'sha256'),
        'hash_md5': obtener_hash_archivo(contenido, 'md5'),
        'tamano_bytes': len(contenido),
        'tamano_formateado': formatear_bytes(len(contenido)),
        'fecha_descarga': formatear_fecha_actual(),
        'timestamp': formatear_fecha_archivo()
    }


def validar_estructura_directorio(base_path: str) -> Dict[str, bool]:
    """
    Valida que existan los directorios necesarios.
    
    Args:
        base_path: Ruta base del proyecto
        
    Returns:
        Diccionario con estado de cada directorio
    """
    directorios = [
        'config',
        'data',
        'logs',
        'web_scraping_adres_output'
    ]
    
    estado = {}
    for directorio in directorios:
        ruta = os.path.join(base_path, directorio)
        estado[directorio] = os.path.exists(ruta) and os.path.isdir(ruta)
    
    return estado


def obtener_extension_archivo(url_o_nombre: str) -> str:
    """
    Obtiene la extensión de un archivo desde URL o nombre.
    
    Args:
        url_o_nombre: URL o nombre de archivo
        
    Returns:
        Extensión del archivo (sin punto)
    """
    if not url_o_nombre:
        return ""
    
    # Extraer nombre del archivo de la URL
    parsed = urlparse(url_o_nombre)
    path = parsed.path
    
    # Obtener extensión
    extension = os.path.splitext(path)[1].lower()
    return extension.lstrip('.')


def construir_url_completa(base_url: str, ruta_relativa: str) -> str:
    """
    Construye una URL completa desde una base y una ruta relativa.
    
    Args:
        base_url: URL base
        ruta_relativa: Ruta relativa o absoluta
        
    Returns:
        URL completa
    """
    if not base_url or not ruta_relativa:
        return ruta_relativa or ""
    
    return urljoin(base_url, ruta_relativa)


def es_url_valida(url: str) -> bool:
    """
    Verifica si una URL tiene un formato válido.
    
    Args:
        url: URL a verificar
        
    Returns:
        True si la URL es válida
    """
    if not url or not isinstance(url, str):
        return False
    
    try:
        resultado = urlparse(url)
        return bool(resultado.scheme and resultado.netloc)
    except Exception:
        return False


def extraer_info_url(url: str) -> Dict[str, str]:
    """
    Extrae información detallada de una URL.
    
    Args:
        url: URL a analizar
        
    Returns:
        Diccionario con información de la URL
    """
    if not url:
        return {}
    
    try:
        parsed = urlparse(url)
        return {
            'scheme': parsed.scheme,
            'netloc': parsed.netloc,
            'hostname': parsed.hostname or '',
            'port': str(parsed.port) if parsed.port else '',
            'path': parsed.path,
            'query': parsed.query,
            'fragment': parsed.fragment,
            'url_completa': url
        }
    except Exception:
        return {'url_completa': url}


def generar_nombre_archivo_unico(base_name: str, extension: str, directorio: str = "") -> str:
    """
    Genera un nombre de archivo único agregando timestamp.
    
    Args:
        base_name: Nombre base del archivo
        extension: Extensión del archivo
        directorio: Directorio donde se guardará (opcional)
        
    Returns:
        Nombre de archivo único
    """
    timestamp = formatear_fecha_archivo()
    base_limpio = limpiar_nombre_archivo(base_name)
    
    if not extension.startswith('.'):
        extension = '.' + extension
    
    nombre_unico = f"{base_limpio}_{timestamp}{extension}"
    
    if directorio:
        return os.path.join(directorio, nombre_unico)
    
    return nombre_unico


def contar_archivos_directorio(directorio: str, extension: str = "") -> int:
    """
    Cuenta archivos en un directorio, opcionalmente por extensión.
    
    Args:
        directorio: Ruta del directorio
        extension: Extensión a filtrar (opcional)
        
    Returns:
        Número de archivos encontrados
    """
    if not os.path.exists(directorio):
        return 0
    
    try:
        archivos = os.listdir(directorio)
        if extension:
            if not extension.startswith('.'):
                extension = '.' + extension
            archivos = [f for f in archivos if f.lower().endswith(extension.lower())]
        
        return len(archivos)
    except Exception:
        return 0


def setup_logging(name: str, log_dir: str = "logs", level: str = "INFO") -> logging.Logger:
    """
    Configura el sistema de logging para el proyecto.
    
    Args:
        name: Nombre del logger
        log_dir: Directorio para archivos de log
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR)
        
    Returns:
        Logger configurado
    """
    # Crear directorio de logs si no existe
    crear_directorio_seguro(log_dir)
    
    # Configurar logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Evitar duplicar handlers
    if logger.handlers:
        return logger
    
    # Handler para archivo
    log_file = os.path.join(log_dir, f"{name}.log")
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formato de logging
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Agregar handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def validate_url(url: str) -> bool:
    """
    Alias para es_url_valida para compatibilidad.
    
    Args:
        url: URL a validar
        
    Returns:
        True si la URL es válida
    """
    return es_url_valida(url)


def safe_filename(filename: str) -> str:
    """
    Alias para limpiar_nombre_archivo para compatibilidad.
    
    Args:
        filename: Nombre de archivo a limpiar
        
    Returns:
        Nombre de archivo seguro
    """
    return limpiar_nombre_archivo(filename)


def format_file_size(bytes_count: int) -> str:
    """
    Alias para formatear_bytes para compatibilidad.
    
    Args:
        bytes_count: Número de bytes
        
    Returns:
        Cadena formateada
    """
    return formatear_bytes(bytes_count)


def create_timestamp() -> str:
    """
    Alias para formatear_fecha_archivo para compatibilidad.
    
    Returns:
        Timestamp para archivos
    """
    return formatear_fecha_archivo()


def ensure_directory(path: str) -> bool:
    """
    Alias para crear_directorio_seguro para compatibilidad.
    
    Args:
        path: Ruta del directorio
        
    Returns:
        True si se creó o existe
    """
    return crear_directorio_seguro(path)