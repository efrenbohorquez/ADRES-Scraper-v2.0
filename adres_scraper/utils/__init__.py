"""
Módulo de utilidades para ADRES Scraper.

Proporciona funciones auxiliares para manipulación de URLs, validación de archivos,
generación de hashes, normalización de texto y utilidades de sistema.
"""

from .helpers import (
    normalizar_url,
    validar_url_pdf,
    obtener_hash_archivo,
    normalizar_texto,
    extraer_numero_resolucion,
    formatear_fecha_actual,
    formatear_fecha_archivo,
    crear_directorio_seguro,
    obtener_tamano_archivo,
    formatear_bytes,
    limpiar_nombre_archivo,
    generar_metadatos_basicos,
    validar_estructura_directorio,
    obtener_extension_archivo,
    construir_url_completa,
    es_url_valida,
    extraer_info_url,
    generar_nombre_archivo_unico,
    contar_archivos_directorio
)

__all__ = [
    'normalizar_url',
    'validar_url_pdf',
    'obtener_hash_archivo',
    'normalizar_texto',
    'extraer_numero_resolucion',
    'formatear_fecha_actual',
    'formatear_fecha_archivo',
    'crear_directorio_seguro',
    'obtener_tamano_archivo',
    'formatear_bytes',
    'limpiar_nombre_archivo',
    'generar_metadatos_basicos',
    'validar_estructura_directorio',
    'obtener_extension_archivo',
    'construir_url_completa',
    'es_url_valida',
    'extraer_info_url',
    'generar_nombre_archivo_unico',
    'contar_archivos_directorio'
]