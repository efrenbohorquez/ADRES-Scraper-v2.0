#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validador de Web Scraping Ético - Taller Big Data
==============================================

Este script proporciona herramientas para validar que el proceso de web scraping
cumple con los principios éticos establecidos en el taller. Incluye verificaciones
automáticas de configuración, análisis de robots.txt, y validación de buenas prácticas.
"""

import requests
import urllib.robotparser
import time
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin, urlparse


class ValidadorEtico:
    """
    Clase para validar el cumplimiento de principios éticos en web scraping
    """
    
    def __init__(self):
        """
        Inicializar el validador ético
        """
        self.resultados_validacion = {}
        self.puntuacion_total = 0
        self.puntuacion_maxima = 100
    
    def verificar_robots_txt(self, url: str, user_agent: str = '*') -> Dict[str, Any]:
        """
        Verificar el archivo robots.txt del sitio web objetivo
        
        Args:
            url: URL del sitio web a verificar
            user_agent: User-Agent a verificar (por defecto '*')
            
        Returns:
            Diccionario con los resultados de la verificación
        """
        try:
            parsed_url = urlparse(url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            robots_url = urljoin(base_url, '/robots.txt')
            
            # Crear parser de robots.txt
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(robots_url)
            
            try:
                rp.read()
                puede_acceder = rp.can_fetch(user_agent, url)
                delay = rp.crawl_delay(user_agent)
                
                resultado = {
                    'robots_txt_existe': True,
                    'url_robots': robots_url,
                    'puede_acceder': puede_acceder,
                    'delay_recomendado': delay,
                    'puntuacion': 20 if puede_acceder else 0,
                    'observaciones': []
                }
                
                if not puede_acceder:
                    resultado['observaciones'].append("⚠️ El robots.txt prohíbe el acceso a esta URL")
                elif delay:
                    resultado['observaciones'].append(f"ℹ️ Delay recomendado: {delay} segundos")
                else:
                    resultado['observaciones'].append("✅ Acceso permitido sin restricciones específicas")
                    
            except Exception:
                # Si no se puede leer robots.txt, asumir que no existe o no es accesible
                resultado = {
                    'robots_txt_existe': False,
                    'url_robots': robots_url,
                    'puede_acceder': True,  # Asumir permitido si no hay robots.txt
                    'delay_recomendado': None,
                    'puntuacion': 15,  # Puntuación menor por falta de robots.txt
                    'observaciones': ["ℹ️ No se encontró robots.txt o no es accesible"]
                }
                
        except Exception as e:
            resultado = {
                'robots_txt_existe': False,
                'error': str(e),
                'puede_acceder': False,
                'puntuacion': 0,
                'observaciones': [f"❌ Error al verificar robots.txt: {e}"]
            }
        
        return resultado
    
    def validar_headers_eticos(self, headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Validar que los headers HTTP sean éticos y apropiados
        
        Args:
            headers: Diccionario de headers HTTP
            
        Returns:
            Diccionario con los resultados de la validación
        """
        puntuacion = 0
        observaciones = []
        
        # Verificar User-Agent apropiado
        user_agent = headers.get('User-Agent', '')
        if not user_agent:
            observaciones.append("❌ Falta el header User-Agent")
        elif 'bot' in user_agent.lower() or 'crawler' in user_agent.lower():
            observaciones.append("⚠️ User-Agent se identifica como bot - considerar más descriptivo")
            puntuacion += 5
        elif any(keyword in user_agent.lower() for keyword in ['academic', 'research', 'education', 'taller']):
            observaciones.append("✅ User-Agent identifica propósito académico/educativo")
            puntuacion += 15
        else:
            observaciones.append("ℹ️ User-Agent genérico - considerar identificar propósito educativo")
            puntuacion += 10
        
        # Verificar otros headers importantes
        headers_recomendados = {
            'Accept': 'Especifica tipos de contenido aceptados',
            'Accept-Language': 'Especifica idiomas preferidos',
            'Connection': 'Gestión de conexiones HTTP'
        }
        
        for header, descripcion in headers_recomendados.items():
            if header in headers:
                observaciones.append(f"✅ Header {header} presente")
                puntuacion += 3
            else:
                observaciones.append(f"ℹ️ Header {header} ausente - {descripcion}")
        
        # Verificar headers problemáticos
        headers_problematicos = ['X-Forwarded-For', 'X-Real-IP']
        for header in headers_problematicos:
            if header in headers:
                observaciones.append(f"⚠️ Header {header} presente - puede ser problemático")
                puntuacion -= 5
        
        return {
            'puntuacion': max(0, min(puntuacion, 25)),
            'observaciones': observaciones,
            'headers_analizados': len(headers)
        }
    
    def validar_configuracion_delays(self, delay_segundos: float, timeout: int) -> Dict[str, Any]:
        """
        Validar la configuración de delays y timeouts
        
        Args:
            delay_segundos: Segundos de delay entre peticiones
            timeout: Timeout en segundos para las peticiones
            
        Returns:
            Diccionario con los resultados de la validación
        """
        puntuacion = 0
        observaciones = []
        
        # Validar delay
        if delay_segundos <= 0:
            observaciones.append("❌ Sin delay entre peticiones - puede saturar el servidor")
            puntuacion += 0
        elif delay_segundos < 0.5:
            observaciones.append("⚠️ Delay muy bajo - considerar aumentar a 0.5s mínimo")
            puntuacion += 10
        elif 0.5 <= delay_segundos <= 2.0:
            observaciones.append("✅ Delay apropiado para web scraping ético")
            puntuacion += 20
        else:
            observaciones.append("ℹ️ Delay muy alto - puede ser excesivo pero es ético")
            puntuacion += 15
        
        # Validar timeout
        if timeout <= 0:
            observaciones.append("❌ Sin timeout configurado - puede causar conexiones colgadas")
        elif timeout < 5:
            observaciones.append("⚠️ Timeout muy bajo - puede causar errores en conexiones lentas")
            puntuacion += 5
        elif 5 <= timeout <= 30:
            observaciones.append("✅ Timeout apropiado")
            puntuacion += 10
        else:
            observaciones.append("ℹ️ Timeout muy alto - puede ser excesivo")
            puntuacion += 8
        
        return {
            'puntuacion': puntuacion,
            'observaciones': observaciones,
            'delay_segundos': delay_segundos,
            'timeout_segundos': timeout
        }
    
    def validar_manejo_errores(self, codigo_scraper: str) -> Dict[str, Any]:
        """
        Validar que el código incluya manejo apropiado de errores
        
        Args:
            codigo_scraper: Código fuente del scraper como string
            
        Returns:
            Diccionario con los resultados de la validación
        """
        puntuacion = 0
        observaciones = []
        
        # Verificar manejo de excepciones HTTP
        if 'HTTPError' in codigo_scraper or 'http' in codigo_scraper.lower():
            observaciones.append("✅ Manejo de errores HTTP detectado")
            puntuacion += 10
        else:
            observaciones.append("⚠️ No se detectó manejo específico de errores HTTP")
        
        # Verificar manejo de excepciones de conexión
        if 'ConnectionError' in codigo_scraper or 'RequestException' in codigo_scraper:
            observaciones.append("✅ Manejo de errores de conexión detectado")
            puntuacion += 10
        else:
            observaciones.append("⚠️ No se detectó manejo de errores de conexión")
        
        # Verificar logging
        if 'logging' in codigo_scraper or 'log' in codigo_scraper.lower():
            observaciones.append("✅ Sistema de logging detectado")
            puntuacion += 8
        else:
            observaciones.append("ℹ️ No se detectó sistema de logging")
        
        # Verificar try-catch genérico
        if 'try:' in codigo_scraper and 'except' in codigo_scraper:
            observaciones.append("✅ Bloques try-except presentes")
            puntuacion += 7
        else:
            observaciones.append("❌ No se detectaron bloques try-except")
        
        return {
            'puntuacion': min(puntuacion, 25),
            'observaciones': observaciones
        }
    
    def verificar_impacto_servidor(self, url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Realizar una verificación básica del impacto en el servidor
        
        Args:
            url: URL a verificar
            headers: Headers a usar en la petición
            
        Returns:
            Diccionario con los resultados de la verificación
        """
        try:
            # Hacer una petición de prueba para medir tiempo de respuesta
            start_time = time.time()
            response = requests.head(url, headers=headers, timeout=10)
            end_time = time.time()
            
            tiempo_respuesta = end_time - start_time
            
            observaciones = []
            puntuacion = 10  # Base
            
            # Evaluar tiempo de respuesta
            if tiempo_respuesta < 1.0:
                observaciones.append(f"✅ Servidor responde rápidamente ({tiempo_respuesta:.2f}s)")
                puntuacion += 10
            elif tiempo_respuesta < 3.0:
                observaciones.append(f"ℹ️ Tiempo de respuesta normal ({tiempo_respuesta:.2f}s)")
                puntuacion += 7
            else:
                observaciones.append(f"⚠️ Servidor responde lentamente ({tiempo_respuesta:.2f}s)")
                puntuacion += 5
            
            # Verificar código de estado
            if response.status_code == 200:
                observaciones.append("✅ Servidor acepta la petición (200 OK)")
                puntuacion += 5
            elif response.status_code == 429:
                observaciones.append("⚠️ Servidor indica límite de velocidad (429)")
                puntuacion -= 5
            else:
                observaciones.append(f"ℹ️ Código de estado: {response.status_code}")
            
            return {
                'puntuacion': puntuacion,
                'tiempo_respuesta': tiempo_respuesta,
                'status_code': response.status_code,
                'observaciones': observaciones,
                'servidor_disponible': True
            }
            
        except Exception as e:
            return {
                'puntuacion': 0,
                'error': str(e),
                'observaciones': [f"❌ Error al conectar con el servidor: {e}"],
                'servidor_disponible': False
            }
    
    def generar_reporte_validacion(self, configuracion: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generar un reporte completo de validación ética
        
        Args:
            configuracion: Diccionario con la configuración del scraper
            
        Returns:
            Diccionario con el reporte completo
        """
        reporte = {
            'fecha_validacion': datetime.now().isoformat(),
            'configuracion_analizada': configuracion,
            'validaciones': {},
            'puntuacion_total': 0,
            'puntuacion_maxima': 100,
            'calificacion': '',
            'recomendaciones': []
        }
        
        # Validar robots.txt
        if 'url' in configuracion:
            reporte['validaciones']['robots_txt'] = self.verificar_robots_txt(
                configuracion['url']
            )
        
        # Validar headers
        if 'headers' in configuracion:
            reporte['validaciones']['headers'] = self.validar_headers_eticos(
                configuracion['headers']
            )
        
        # Validar configuración de delays
        reporte['validaciones']['delays'] = self.validar_configuracion_delays(
            configuracion.get('delay_segundos', 0),
            configuracion.get('timeout', 0)
        )
        
        # Validar manejo de errores si se proporciona código
        if 'codigo_fuente' in configuracion:
            reporte['validaciones']['manejo_errores'] = self.validar_manejo_errores(
                configuracion['codigo_fuente']
            )
        
        # Verificar impacto en servidor
        if 'url' in configuracion and 'headers' in configuracion:
            reporte['validaciones']['impacto_servidor'] = self.verificar_impacto_servidor(
                configuracion['url'],
                configuracion['headers']
            )
        
        # Calcular puntuación total
        puntuacion_total = sum(
            validacion.get('puntuacion', 0) 
            for validacion in reporte['validaciones'].values()
        )
        
        reporte['puntuacion_total'] = puntuacion_total
        
        # Determinar calificación
        porcentaje = (puntuacion_total / 100) * 100
        if porcentaje >= 90:
            reporte['calificacion'] = '🏆 Excelente - Cumple completamente con principios éticos'
        elif porcentaje >= 75:
            reporte['calificacion'] = '✅ Bueno - Cumple con la mayoría de principios éticos'
        elif porcentaje >= 60:
            reporte['calificacion'] = '⚠️ Regular - Necesita mejoras en algunos aspectos'
        else:
            reporte['calificacion'] = '❌ Insuficiente - Requiere mejoras significativas'
        
        # Generar recomendaciones generales
        if porcentaje < 90:
            reporte['recomendaciones'].extend([
                "Revisar y mejorar los aspectos identificados con puntuación baja",
                "Consultar la documentación de principios éticos del proyecto",
                "Considerar implementar las observaciones específicas de cada validación"
            ])
        
        return reporte
    
    def guardar_reporte(self, reporte: Dict[str, Any], archivo_salida: str):
        """
        Guardar el reporte de validación en archivo
        
        Args:
            reporte: Diccionario con el reporte de validación
            archivo_salida: Ruta del archivo donde guardar
        """
        try:
            with open(archivo_salida, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=4, ensure_ascii=False)
            
            print(f"✅ Reporte de validación guardado en: {archivo_salida}")
            
        except Exception as e:
            print(f"❌ Error al guardar el reporte: {e}")


def validar_scraper_adres():
    """
    Función para validar la configuración específica del scraper de ADRES
    """
    print("=" * 70)
    print("🛡️ VALIDADOR ÉTICO - WEB SCRAPING ADRES")
    print("=" * 70)
    
    # Configuración del scraper de ADRES (basada en el código del taller)
    configuracion = {
        'url': 'https://normograma.adres.gov.co/compilacion/docs/concepto_adres_20241209688471_2024.html',
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        },
        'delay_segundos': 0.5,
        'timeout': 10
    }
    
    # Leer el código fuente si existe
    script_path = 'src/web_scraper_adres.py'
    if os.path.exists(script_path):
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                configuracion['codigo_fuente'] = f.read()
        except Exception:
            pass
    
    # Crear validador y generar reporte
    validador = ValidadorEtico()
    reporte = validador.generar_reporte_validacion(configuracion)
    
    # Mostrar resultados en consola
    print(f"\n📊 RESULTADOS DE VALIDACIÓN ÉTICA")
    print(f"Puntuación total: {reporte['puntuacion_total']}/100")
    print(f"Calificación: {reporte['calificacion']}")
    
    print(f"\n🔍 DETALLES POR CATEGORÍA:")
    for categoria, resultados in reporte['validaciones'].items():
        print(f"\n{categoria.upper().replace('_', ' ')}:")
        print(f"  Puntuación: {resultados.get('puntuacion', 0)}")
        for obs in resultados.get('observaciones', []):
            print(f"  {obs}")
    
    # Guardar reporte
    os.makedirs('web_scraping_adres_output', exist_ok=True)
    archivo_reporte = f"web_scraping_adres_output/validacion_etica_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    validador.guardar_reporte(reporte, archivo_reporte)
    
    return reporte['puntuacion_total']


def main():
    """
    Función principal del validador ético
    """
    puntuacion = validar_scraper_adres()
    
    print(f"\n📋 RESUMEN EJECUTIVO:")
    if puntuacion >= 90:
        print("🏆 ¡Excelente! Tu scraper cumple con los más altos estándares éticos.")
    elif puntuacion >= 75:
        print("✅ Buen trabajo. Tu scraper es éticamente sólido con algunas mejoras menores.")
    elif puntuacion >= 60:
        print("⚠️ Tu scraper necesita algunas mejoras para ser completamente ético.")
    else:
        print("❌ Tu scraper requiere mejoras significativas en aspectos éticos.")
    
    print("\n💡 Recuerda: El web scraping ético no solo es técnicamente correcto,")
    print("    sino que también respeta los recursos y la privacidad.")
    
    return 0

# Bloque de ejecución removido - módulo de librería
