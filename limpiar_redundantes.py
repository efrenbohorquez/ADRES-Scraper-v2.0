#!/usr/bin/env python3
"""
Script para limpiar archivos redundantes del proyecto ADRES Scraper.

Este script identifica y opcionalmente elimina archivos duplicados
y obsoletos del proyecto después de la refactorización.
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict


def identificar_archivos_redundantes() -> Dict[str, List[str]]:
    """
    Identifica archivos redundantes en el proyecto.
    
    Returns:
        Diccionario con categorías de archivos redundantes
    """
    base_path = Path(__file__).parent
    
    redundantes = {
        'scripts_prueba': [
            'probar_atlas.py',
            'probar_atlas_corregido.py', 
            'probar_conexion_nueva.py',
            'probar_sistema.py',
            'prueba_descarga.py',
            'pruebas_avanzadas_atlas.py',
            'reintentar_atlas.py'
        ],
        'scripts_verificacion': [
            'verificar_atlas.py',
            'verificar_atlas_simple.py'
        ],
        'demos_antiguos': [
            'demo_completa.py',
            'demo_completa_mongodb.py',
            'demo_sistema_completo.py',
            'demo_sistema_simplificado.py'
        ],
        'configuracion_antigua': [
            'configurar_atlas.py',
            'configurar_mongodb_local.py',
            'config_atlas.py',
            'conexion_manual_atlas.py'
        ],
        'scrapers_antiguos': [
            'scraper_adres_optimizado.py',
            'descargador_adres_atlas.py'
        ],
        'diagnosticos': [
            'diagnostico_atlas_completo.py'
        ],
        'resumenes_antiguos': [
            'resumen_ejecutivo.py',
            'resumen_modulo_adres.py',
            'mostrar_resumen_proyecto.py'
        ],
        'archivos_backup': [
            'adres_scraper/utils/helpers_old.py'
        ],
        'logs_antiguos': [
            'scraper_adres.log',
            'web_scraper_adres.log'
        ]
    }
    
    # Verificar qué archivos existen realmente
    redundantes_existentes = {}
    
    for categoria, archivos in redundantes.items():
        archivos_existentes = []
        for archivo in archivos:
            ruta_archivo = base_path / archivo
            if ruta_archivo.exists():
                archivos_existentes.append(str(ruta_archivo))
        
        if archivos_existentes:
            redundantes_existentes[categoria] = archivos_existentes
    
    return redundantes_existentes


def mostrar_resumen_redundantes(redundantes: Dict[str, List[str]]) -> None:
    """Muestra un resumen de archivos redundantes encontrados."""
    
    print("🔍 ANÁLISIS DE ARCHIVOS REDUNDANTES")
    print("=" * 50)
    
    total_archivos = sum(len(archivos) for archivos in redundantes.values())
    
    if total_archivos == 0:
        print("✅ No se encontraron archivos redundantes")
        return
    
    print(f"📊 Total archivos redundantes encontrados: {total_archivos}")
    print()
    
    for categoria, archivos in redundantes.items():
        print(f"📁 {categoria.replace('_', ' ').title()}:")
        for archivo in archivos:
            tamaño = Path(archivo).stat().st_size if Path(archivo).exists() else 0
            print(f"   • {Path(archivo).name} ({tamaño:,} bytes)")
        print()


def crear_backup_archivos(archivos: List[str], directorio_backup: str = "backup_redundantes") -> bool:
    """
    Crea backup de archivos antes de eliminarlos.
    
    Args:
        archivos: Lista de rutas de archivos
        directorio_backup: Directorio donde crear el backup
        
    Returns:
        True si el backup fue exitoso
    """
    try:
        backup_path = Path(directorio_backup)
        backup_path.mkdir(exist_ok=True)
        
        print(f"📦 Creando backup en: {backup_path.absolute()}")
        
        for archivo in archivos:
            archivo_path = Path(archivo)
            if archivo_path.exists():
                destino = backup_path / archivo_path.name
                shutil.copy2(archivo, destino)
                print(f"   ✅ Backup: {archivo_path.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creando backup: {e}")
        return False


def eliminar_archivos_redundantes(archivos: List[str]) -> int:
    """
    Elimina archivos redundantes.
    
    Args:
        archivos: Lista de rutas de archivos a eliminar
        
    Returns:
        Número de archivos eliminados exitosamente
    """
    eliminados = 0
    
    for archivo in archivos:
        try:
            archivo_path = Path(archivo)
            if archivo_path.exists():
                archivo_path.unlink()
                print(f"   🗑️ Eliminado: {archivo_path.name}")
                eliminados += 1
        except Exception as e:
            print(f"   ❌ Error eliminando {archivo}: {e}")
    
    return eliminados


def main():
    """Función principal del script de limpieza."""
    print("🧹 LIMPIEZA DE ARCHIVOS REDUNDANTES - ADRES Scraper v2.0")
    print("=" * 60)
    
    # 1. Identificar archivos redundantes
    redundantes = identificar_archivos_redundantes()
    
    # 2. Mostrar resumen
    mostrar_resumen_redundantes(redundantes)
    
    if not redundantes:
        return
    
    # 3. Confirmar acción
    print("⚠️  ADVERTENCIA: Esta acción eliminará archivos del proyecto")
    print("💡 Se creará un backup antes de eliminar")
    print()
    
    respuesta = input("¿Deseas continuar con la limpieza? (s/N): ").lower().strip()
    
    if respuesta not in ['s', 'si', 'sí', 'y', 'yes']:
        print("❌ Operación cancelada")
        return
    
    # 4. Crear backup
    todos_los_archivos = []
    for archivos in redundantes.values():
        todos_los_archivos.extend(archivos)
    
    if not crear_backup_archivos(todos_los_archivos):
        print("❌ No se pudo crear backup. Operación cancelada.")
        return
    
    # 5. Eliminar archivos por categoría
    print("\n🗑️ Eliminando archivos redundantes...")
    total_eliminados = 0
    
    for categoria, archivos in redundantes.items():
        print(f"\n📁 Eliminando {categoria.replace('_', ' ')}...")
        eliminados = eliminar_archivos_redundantes(archivos)
        total_eliminados += eliminados
    
    # 6. Resumen final
    print(f"\n✅ Limpieza completada:")
    print(f"   🗑️ Archivos eliminados: {total_eliminados}")
    print(f"   📦 Backup creado en: backup_redundantes/")
    print(f"   🏗️ Estructura optimizada lista para Git")
    
    print("\n📋 Próximos pasos recomendados:")
    print("   1. Verificar funcionamiento con: python ejemplo_uso_optimizado.py")
    print("   2. Ejecutar tests: python -m pytest tests/")
    print("   3. Inicializar repositorio Git: git init")
    print("   4. Hacer primer commit: git add . && git commit -m 'Proyecto refactorizado v2.0'")


if __name__ == "__main__":
    main()