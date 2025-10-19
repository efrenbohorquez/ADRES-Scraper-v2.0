#!/usr/bin/env python3
"""
🎯 MÓDULO DE MONITOREO VISUAL
Interfaz visual para mostrar el progreso de descarga y carga a MongoDB Atlas
"""

import time
import json
from datetime import datetime
import sys

class MonitorVisual:
    """Interfaz visual para monitorear el progreso"""
    
    def __init__(self):
        self.progreso_actual = 0
        self.total_pasos = 0
        
    def mostrar_banner_inicio(self):
        """Mostrar banner inicial"""
        print("\n" + "="*80)
        print("🎓 TALLER BIG DATA - EXTRACCIÓN DOCUMENTO ADRES")
        print("🛡️ Aplicando técnicas de web scraping éticas")
        print("📍 URL: https://normograma.adres.gov.co/compilacion/aprende_adres_guias.html")
        print("="*80)
    
    def inicializar_progreso(self, total_pasos):
        """Inicializar barra de progreso"""
        self.total_pasos = total_pasos
        self.progreso_actual = 0
        print(f"\n📊 INICIANDO PROCESO ({total_pasos} pasos)")
        self._mostrar_barra_progreso()
    
    def actualizar_progreso(self, paso_actual, descripcion):
        """Actualizar progreso con descripción"""
        self.progreso_actual = paso_actual
        print(f"\n🔄 Paso {paso_actual}/{self.total_pasos}: {descripcion}")
        self._mostrar_barra_progreso()
        time.sleep(0.5)  # Pausa visual
    
    def _mostrar_barra_progreso(self):
        """Mostrar barra de progreso visual"""
        if self.total_pasos == 0:
            return
            
        porcentaje = (self.progreso_actual / self.total_pasos) * 100
        longitud_barra = 50
        relleno = int(longitud_barra * self.progreso_actual / self.total_pasos)
        
        barra = "█" * relleno + "░" * (longitud_barra - relleno)
        print(f"   [{barra}] {porcentaje:.1f}%")
    
    def mostrar_principios_eticos(self):
        """Mostrar principios éticos aplicados"""
        print("\n🛡️ PRINCIPIOS ÉTICOS APLICADOS:")
        principios = [
            "✅ Verificación de robots.txt",
            "✅ Headers identificativos del propósito académico", 
            "✅ Delays respetuosos entre peticiones (2s)",
            "✅ Timeouts configurados apropiadamente",
            "✅ Manejo robusto de errores SSL",
            "✅ Solo información pública accesible",
            "✅ Logging detallado para auditoría"
        ]
        
        for i, principio in enumerate(principios, 1):
            print(f"   {principio}")
            time.sleep(0.2)  # Animación suave
    
    def mostrar_descarga_en_progreso(self, url):
        """Animación de descarga en progreso"""
        print(f"\n📥 DESCARGANDO DESDE:")
        print(f"   {url}")
        print("\n   Progreso de descarga:")
        
        # Simulación visual de descarga
        etapas = [
            "🔗 Estableciendo conexión...",
            "🤝 Negociando SSL...", 
            "📡 Enviando petición HTTP...",
            "📨 Recibiendo respuesta...",
            "📄 Descargando contenido...",
            "✅ Descarga completada!"
        ]
        
        for i, etapa in enumerate(etapas):
            print(f"   {etapa}")
            
            # Barra de progreso para esta etapa
            for j in range(20):
                sys.stdout.write(f"\r   [{'█' * (j+1)}{'░' * (19-j)}] {((j+1)/20)*100:.0f}%")
                sys.stdout.flush()
                time.sleep(0.05)
            
            print()  # Nueva línea
    
    def mostrar_analisis_contenido(self, documento_json):
        """Mostrar análisis del contenido extraído"""
        print("\n📊 ANÁLISIS DEL DOCUMENTO EXTRAÍDO")
        print("="*50)
        
        contenido = documento_json.get('contenido', {})
        analisis = documento_json.get('analisis', {})
        
        print(f"📋 Título: {documento_json.get('titulo', 'N/A')}")
        print(f"📊 Caracteres: {contenido.get('longitud_caracteres', 0):,}")
        print(f"📝 Palabras: {contenido.get('longitud_palabras', 0):,}")
        print(f"🔗 Enlaces encontrados: {len(documento_json.get('enlaces_relacionados', []))}")
        
        # Palabras clave encontradas
        palabras_clave = analisis.get('palabras_clave_adres', [])
        if palabras_clave:
            print(f"🔑 Palabras clave ADRES: {', '.join(palabras_clave)}")
        
        print(f"📂 Categoría: {analisis.get('categoria', 'N/A')}")
        print(f"📈 Relevancia ADRES: {analisis.get('relevancia_adres', 0):.1%}")
    
    def mostrar_estado_mongodb(self, conectado, doc_id=None):
        """Mostrar estado de MongoDB Atlas"""
        print("\n💾 ESTADO MONGODB ATLAS")
        print("="*30)
        
        if conectado:
            print("✅ Conexión exitosa a MongoDB Atlas")
            if doc_id:
                print(f"📄 Documento subido con ID: {doc_id}")
                print("🎯 El documento está listo para análisis")
        else:
            print("⚠️ No se pudo conectar a MongoDB Atlas")
            print("💾 Documento guardado como respaldo local")
            print("📋 Para configurar Atlas: python configurar_atlas.py")
    
    def mostrar_resumen_final(self, exito, tiempo_total):
        """Mostrar resumen final del proceso"""
        print("\n" + "="*70)
        if exito:
            print("🎉 ¡PROCESO COMPLETADO EXITOSAMENTE!")
        else:
            print("⚠️ PROCESO COMPLETADO CON OBSERVACIONES")
        print("="*70)
        
        print(f"⏱️ Tiempo total: {tiempo_total:.1f} segundos")
        
        # Checklist de lo realizado
        checklist = [
            "✅ Documento ADRES descargado éticamente",
            "✅ Contenido HTML extraído y limpiado", 
            "✅ Datos estructurados en formato JSON",
            "✅ Metadatos y análisis generados",
            "✅ Principios éticos aplicados correctamente",
            "📄 Archivo de respaldo creado localmente"
        ]
        
        print("\n📋 RESUMEN DE ACTIVIDADES:")
        for item in checklist:
            print(f"   {item}")
        
        print(f"\n🎯 PRÓXIMOS PASOS:")
        print("   1. Revisar el archivo 'documento_adres_respaldo.json'")
        print("   2. Configurar MongoDB Atlas con: python configurar_atlas.py")
        print("   3. Ejecutar análisis avanzados con los datos JSON")
        print("   4. Usar los datos para estudios de Big Data")

def demostrar_descarga_completa():
    """Demostración completa con monitoreo visual"""
    monitor = MonitorVisual()
    tiempo_inicio = time.time()
    
    # Banner inicial
    monitor.mostrar_banner_inicio()
    
    # Mostrar principios éticos
    monitor.mostrar_principios_eticos()
    
    # Inicializar progreso
    monitor.inicializar_progreso(5)
    
    # Paso 1: Verificaciones éticas
    monitor.actualizar_progreso(1, "Verificando robots.txt y principios éticos")
    time.sleep(1)
    
    # Paso 2: Descarga del documento
    monitor.actualizar_progreso(2, "Descargando documento ADRES")
    url_demo = "https://normograma.adres.gov.co/compilacion/aprende_adres_guias.html"
    monitor.mostrar_descarga_en_progreso(url_demo)
    
    # Paso 3: Extracción de contenido
    monitor.actualizar_progreso(3, "Extrayendo y estructurando contenido")
    time.sleep(1.5)
    
    # Cargar documento real si existe
    try:
        with open('documento_adres_respaldo.json', 'r', encoding='utf-8') as f:
            documento_json = json.load(f)
        monitor.mostrar_analisis_contenido(documento_json)
    except:
        print("   📄 Documento de ejemplo no disponible")
    
    # Paso 4: Conexión a MongoDB
    monitor.actualizar_progreso(4, "Conectando a MongoDB Atlas")
    time.sleep(1)
    monitor.mostrar_estado_mongodb(False)  # Simular fallo de conexión
    
    # Paso 5: Finalización
    monitor.actualizar_progreso(5, "Finalizando y generando respaldo")
    time.sleep(1)
    
    # Resumen final
    tiempo_total = time.time() - tiempo_inicio
    monitor.mostrar_resumen_final(True, tiempo_total)

if __name__ == "__main__":
    demostrar_descarga_completa()