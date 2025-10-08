#!/usr/bin/env python3
"""
Utilidades Comunes del ADRES Scraper
===================================
Funciones auxiliares y utilidades compartidas para todo el sistema ADRES Scraper.

Este módulo contiene funciones de apoyo que son utilizadas por diferentes
componentes del sistema, incluyendo validaciones, formateo de datos,
manejo de errores y funciones de logging.
"""

import os
import hashlib
import re
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Union
from urllib.parse import urlparse, urljoin
import requests
from pathlib import Path


def setup_logging(logger_name: str, logs_dir: str, level: int = logging.INFO) -> logging.Logger:
    """
    Configurar logging para el módulo especificado
    
    Args:
        logger_name: Nombre del logger
        logs_dir: Directorio para archivos de log
        level: Nivel de logging
        
    Returns:
        Instancia configurada del logger
    """
    # Crear directorio de logs si no existe
    os.makedirs(logs_dir, exist_ok=True)
    
    # Configurar logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    
    # Evitar duplicación de handlers
    if logger.handlers:
        return logger
    
    # Formatter común
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Handler para archivo
    log_file = os.path.join(logs_dir, f'{logger_name}.log')
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


def validate_url(url: str, allowed_domains: Optional[List[str]] = None) -> bool:
    """
    Validar URL y dominio
    
    Args:
        url: URL a validar
        allowed_domains: Lista de dominios permitidos
        
    Returns:
        True si la URL es válida
    """
    if not url or not isinstance(url, str):
        return False
    
    try:
        parsed = urlparse(url)
        
        # Verificar esquema
        if parsed.scheme not in ['http', 'https']:
            return False
        
        # Verificar dominio si se especifica
        if allowed_domains:
            return any(domain in parsed.netloc for domain in allowed_domains)
        
        return bool(parsed.netloc)
        
    except Exception:
        return False


def is_pdf_url(url: str) -> bool:
    """
    Determina si una URL apunta a un archivo PDF.
    
    Args:
        url: URL a verificar
        
    Returns:
        True si es URL de PDF, False caso contrario
    """
    if not url:
        return False
    
    # Verificar extensión
    if url.lower().endswith('.pdf'):
        return True
    
    # Verificar parámetros comunes de PDF
    pdf_indicators = ['filetype=pdf', 'format=pdf', '.pdf?']
    return any(indicator in url.lower() for indicator in pdf_indicators)


def calculate_file_hash(file_path: Union[str, Path]) -> str:
    """
    Calcula el hash SHA256 de un archivo.
    
    Args:
        file_path: Ruta al archivo
        
    Returns:
        Hash SHA256 del archivo
    """
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


def calculate_content_hash(content: str) -> str:
    """
    Calcula el hash SHA256 de contenido de texto.
    
    Args:
        content: Contenido a hashear
        
    Returns:
        Hash SHA256 del contenido
    """
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def build_absolute_url(base_url: str, relative_url: str) -> str:
    """
    Construye una URL absoluta a partir de una base y una relativa.
    
    Args:
        base_url: URL base
        relative_url: URL relativa
        
    Returns:
        URL absoluta
    """
    return urljoin(base_url, relative_url)


def clean_filename(filename: str, max_length: int = 255) -> str:
    """
    Limpia un nombre de archivo para que sea válido en el sistema de archivos.
    
    Args:
        filename: Nombre de archivo a limpiar
        max_length: Longitud máxima del nombre
        
    Returns:
        Nombre de archivo limpio
    """
    # Remover caracteres problemáticos
    cleaned = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remover espacios múltiples y reemplazar por guión bajo
    cleaned = re.sub(r'\s+', '_', cleaned.strip())
    
    # Truncar si es muy largo
    if len(cleaned) > max_length:
        name, ext = os.path.splitext(cleaned)
        max_name_length = max_length - len(ext)
        cleaned = name[:max_name_length] + ext
    
    return cleaned


def extract_resolution_number(text: str) -> Optional[str]:
    """
    Extrae el número de resolución del texto usando patrones comunes.
    
    Args:
        text: Texto donde buscar el número de resolución
        
    Returns:
        Número de resolución si se encuentra, None caso contrario
    """
    patterns = [
        r'resolución\s+(?:no\.?\s*)?(\d+)',
        r'resolution\s+(?:no\.?\s*)?(\d+)',
        r'res\.\s*(\d+)',
        r'número\s+(\d+)',
        r'n[°º]\s*(\d+)',
        r'(\d{4})\s*-\s*(\d+)',  # Formato año-número
    ]
    
    text_lower = text.lower()
    
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            if len(match.groups()) == 1:
                return match.group(1)
            else:
                # Para el patrón año-número, devolver número completo
                return f"{match.group(1)}-{match.group(2)}"
    
    return None


def format_file_size(size_bytes: int) -> str:
    """
    Formatea un tamaño de archivo en bytes a formato legible.
    
    Args:
        size_bytes: Tamaño en bytes
        
    Returns:
        Tamaño formateado (ej: "1.5 MB")
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def safe_get_text(element, default: str = "") -> str:
    """
    Extrae texto de un elemento BeautifulSoup de forma segura.
    
    Args:
        element: Elemento BeautifulSoup o None
        default: Valor por defecto si el elemento es None
        
    Returns:
        Texto del elemento o valor por defecto
    """
    if element is None:
        return default
    
    text = element.get_text(strip=True)
    return text if text else default


def ensure_directory(directory_path: Union[str, Path]) -> Path:
    """
    Asegura que un directorio existe, creándolo si es necesario.
    
    Args:
        directory_path: Ruta del directorio
        
    Returns:
        Path del directorio creado
    """
    path = Path(directory_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_json(data: Any, file_path: Union[str, Path], indent: int = 2) -> bool:
    """
    Guarda datos en formato JSON.
    
    Args:
        data: Datos a guardar
        file_path: Ruta del archivo
        indent: Indentación para el JSON
        
    Returns:
        True si se guardó exitosamente, False caso contrario
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)
        return True
    except Exception as e:
        logging.error(f"Error guardando JSON en {file_path}: {e}")
        return False


def validate_pdf_content(content: bytes) -> bool:
    """
    Valida si el contenido corresponde a un archivo PDF válido.
    
    Args:
        content: Contenido binario del archivo
        
    Returns:
        True si es PDF válido, False caso contrario
    """
    if not content:
        return False
    
    # Verificar header PDF
    pdf_headers = [b'%PDF-1.', b'%PDF-2.']
    return any(content.startswith(header) for header in pdf_headers)


class ProgressTracker:
    """
    Clase para rastrear el progreso de operaciones largas.
    """
    
    def __init__(self, total: int, description: str = "Procesando"):
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = datetime.now()
        
    def update(self, increment: int = 1, item_name: str = ""):
        """Actualiza el progreso."""
        self.current += increment
        percentage = (self.current / self.total) * 100 if self.total > 0 else 0
        
        elapsed = datetime.now() - self.start_time
        if self.current > 0:
            avg_time = elapsed.total_seconds() / self.current
            remaining_time = avg_time * (self.total - self.current)
            eta = f"ETA: {remaining_time:.1f}s"
        else:
            eta = "ETA: --"
        
        print(f"\r{self.description}: {self.current}/{self.total} "
              f"({percentage:.1f}%) {eta} {item_name}", end="", flush=True)
        
        if self.current >= self.total:
            print()  # Nueva línea al finalizar
    
    def finish(self):
        """Finaliza el seguimiento del progreso."""
        elapsed = datetime.now() - self.start_time
        print(f"\n✅ Completado en {elapsed.total_seconds():.1f}s")


# Funciones de compatibilidad para mantener la API existente
def obtener_hash_archivo(ruta_archivo: str) -> str:
    """Función de compatibilidad para calculate_file_hash."""
    return calculate_file_hash(ruta_archivo)


def es_url_pdf(url: str) -> bool:
    """Función de compatibilidad para is_pdf_url."""
    return is_pdf_url(url)


def create_timestamp() -> str:
    """
    Crear timestamp formateado
    
    Returns:
        String con timestamp en formato YYYYMMDD_HHMMSS
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def ensure_directory(directory_path: str) -> str:
    """
    Asegurar que un directorio existe, creándolo si es necesario
    
    Args:
        directory_path: Ruta del directorio
        
    Returns:
        Ruta del directorio (normalizada)
    """
    normalized_path = os.path.normpath(directory_path)
    os.makedirs(normalized_path, exist_ok=True)
    return normalized_path


def safe_filename(filename: str, max_length: int = 255) -> str:
    """
    Crear nombre de archivo seguro
    
    Args:
        filename: Nombre de archivo original
        max_length: Longitud máxima permitida
        
    Returns:
        Nombre de archivo seguro
    """
    # Caracteres no permitidos en nombres de archivo
    invalid_chars = '<>:"/\\|?*'
    
    # Reemplazar caracteres inválidos
    safe_name = ''.join(c if c not in invalid_chars else '_' for c in filename)
    
    # Limitar longitud
    if len(safe_name) > max_length:
        safe_name = safe_name[:max_length]
    
    return safe_name


def format_file_size(size_bytes: int) -> str:
    """
    Formatear tamaño de archivo en forma legible
    
    Args:
        size_bytes: Tamaño en bytes
        
    Returns:
        String formateado (ej: "1.5 MB")
    """
    if size_bytes == 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0
    size = float(size_bytes)
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    return f"{size:.1f} {units[unit_index]}"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncar texto a longitud específica
    
    Args:
        text: Texto a truncar
        max_length: Longitud máxima
        suffix: Sufijo para texto truncado
        
    Returns:
        Texto truncado
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def extract_domain(url: str) -> Optional[str]:
    """
    Extraer dominio de una URL
    
    Args:
        url: URL a procesar
        
    Returns:
        Dominio extraído o None si es inválido
    """
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except Exception:
        return None


def is_pdf_url(url: str) -> bool:
    """
    Verificar si una URL apunta a un archivo PDF
    
    Args:
        url: URL a verificar
        
    Returns:
        True si la URL termina en .pdf
    """
    try:
        parsed = urlparse(url)
        return parsed.path.lower().endswith('.pdf')
    except Exception:
        return False


def clean_text_basic(text: str) -> str:
    """
    Limpieza básica de texto
    
    Args:
        text: Texto a limpiar
        
    Returns:
        Texto limpio
    """
    if not text:
        return ""
    
    # Normalizar espacios en blanco
    import re
    text = re.sub(r'\s+', ' ', text)
    
    # Eliminar espacios al inicio y final
    text = text.strip()
    
    return text


def get_file_extension(filename: str) -> str:
    """
    Obtener extensión de archivo
    
    Args:
        filename: Nombre del archivo
        
    Returns:
        Extensión del archivo (con punto)
    """
    return os.path.splitext(filename)[1].lower()


def bytes_to_mb(bytes_count: int) -> float:
    """
    Convertir bytes a megabytes
    
    Args:
        bytes_count: Número de bytes
        
    Returns:
        Equivalente en MB
    """
    return bytes_count / (1024 * 1024)