#!/usr/bin/env python3
"""
Ejemplo de uso del sistema ADRES Scraper refactorizado.

Este script demuestra cómo usar los módulos optimizados para:
1. Configurar el sistema
2. Realizar scraping ético
3. Descargar PDFs
4. Almacenar en MongoDB
5. Generar reportes
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path para importar el módulo
sys.path.insert(0, str(Path(__file__).parent))

from adres_scraper import ADREScraper, MongoDBManager, PDFDownloader, Config
from adres_scraper.utils import formatear_fecha_actual, crear_directorio_seguro


def main():
    """Función principal del ejemplo."""
    print("🇨🇴 ADRES Scraper v2.0 - Ejemplo de Uso")
    print("=" * 50)
    
    try:
        # 1. Cargar configuración
        print("📋 Cargando configuración...")
        config_path = "config/config_mongodb_atlas.json"
        
        if not os.path.exists(config_path):
            print(f"❌ Archivo de configuración no encontrado: {config_path}")
            print("💡 Copia config/config_template.json y configura tus credenciales")
            return False
        
        config = Config.from_file(config_path)
        print("✅ Configuración cargada exitosamente")
        
        # 2. Inicializar componentes
        print("\n🔧 Inicializando componentes...")
        scraper = ADREScraper(config)
        db_manager = MongoDBManager(config)
        pdf_downloader = PDFDownloader(config)
        
        print("✅ Componentes inicializados")
        
        # 3. Probar conexión MongoDB
        print("\n🗄️ Probando conexión a MongoDB...")
        if db_manager.connect():
            print("✅ Conexión MongoDB exitosa")
        else:
            print("❌ Error al conectar con MongoDB")
            return False
        
        # 4. Realizar scraping de ejemplo
        print("\n🔍 Realizando scraping de ejemplo...")
        url_ejemplo = config.urls['resoluciones']
        
        resultado = scraper.scrape_document(url_ejemplo)
        
        if resultado['exito']:
            print(f"✅ Scraping exitoso: {resultado['titulo'][:50]}...")
            
            # 5. Buscar y descargar PDFs
            print("\n📄 Buscando PDFs en la página...")
            pdfs_encontrados = pdf_downloader.download_pdfs_from_page(url_ejemplo, max_downloads=2)
            
            if pdfs_encontrados:
                print(f"✅ Encontrados {len(pdfs_encontrados)} PDFs")
                
                # 6. Almacenar en MongoDB
                print("\n💾 Almacenando en MongoDB...")
                for pdf_info in pdfs_encontrados:
                    resultado_almacen = db_manager.store_pdf_file(
                        pdf_content=pdf_info['contenido'],
                        filename=pdf_info['nombre_archivo'],
                        metadata=pdf_info['metadata']
                    )
                    
                    if resultado_almacen['exito']:
                        print(f"✅ Almacenado: {pdf_info['nombre_archivo']}")
                    else:
                        print(f"❌ Error almacenando: {pdf_info['nombre_archivo']}")
            else:
                print("⚠️ No se encontraron PDFs para descargar")
        
        else:
            print(f"❌ Error en scraping: {resultado['error']}")
            return False
        
        # 7. Mostrar estadísticas
        print("\n📊 Estadísticas de la base de datos:")
        stats = db_manager.get_database_stats()
        
        print(f"   📄 Total documentos: {stats['total_documents']}")
        print(f"   🗄️ PDFs almacenados: {stats['total_pdfs']}")
        print(f"   💾 Tamaño base de datos: {stats['database_size_formatted']}")
        
        print("\n✅ Ejemplo completado exitosamente")
        return True
        
    except Exception as e:
        print(f"\n❌ Error durante la ejecución: {str(e)}")
        print("💡 Verifica la configuración y conectividad")
        return False
    
    finally:
        # Limpiar conexiones
        try:
            if 'db_manager' in locals():
                db_manager.disconnect()
                print("🔒 Conexión MongoDB cerrada")
        except:
            pass


def mostrar_ayuda():
    """Muestra información de ayuda."""
    print("ADRES Scraper v2.0 - Ejemplo de Uso")
    print("\nPrerequisitos:")
    print("1. Configurar config/config_mongodb_atlas.json con credenciales")
    print("2. Instalar dependencias: pip install -r requirements.txt")
    print("3. Tener conectividad a Internet")
    
    print("\nUso:")
    print("python ejemplo_uso_optimizado.py")
    
    print("\nArquitectura del proyecto:")
    print("adres_scraper/")
    print("├── core/          # Scraper y analizador de contenido")
    print("├── mongodb/       # Gestión de base de datos")
    print("├── downloaders/   # Descargadores especializados") 
    print("├── config/        # Configuraciones centralizadas")
    print("└── utils/         # Utilidades auxiliares")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        mostrar_ayuda()
    else:
        success = main()
        sys.exit(0 if success else 1)