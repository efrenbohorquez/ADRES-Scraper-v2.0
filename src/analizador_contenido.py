#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analizador de Contenido Extraído - Taller Big Data
================================================

Este script proporciona herramientas de análisis para el contenido extraído
del web scraping de ADRES, demostrando técnicas básicas de procesamiento
de lenguaje natural y análisis de datos aplicadas a documentos normativos.

Funcionalidades:
- Análisis estadístico básico del texto
- Extracción de palabras clave y términos frecuentes
- Generación de métricas de legibilidad
- Creación de reportes en formato JSON y Markdown
"""

import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import os


class AnalizadorContenidoADRES:
    """
    Clase para analizar el contenido extraído de documentos de ADRES
    """
    
    def __init__(self, archivo_json: str = None):
        """
        Inicializar el analizador
        
        Args:
            archivo_json: Ruta al archivo JSON con el contenido extraído
        """
        self.archivo_json = archivo_json
        self.datos_originales = None
        self.texto_limpio = ""
        self.palabras = []
        self.oraciones = []
        
        if archivo_json and os.path.exists(archivo_json):
            self.cargar_datos(archivo_json)
    
    def cargar_datos(self, archivo_json: str) -> bool:
        """
        Cargar datos desde archivo JSON de scraping
        
        Args:
            archivo_json: Ruta al archivo JSON
            
        Returns:
            True si la carga fue exitosa, False en caso contrario
        """
        try:
            with open(archivo_json, 'r', encoding='utf-8') as f:
                self.datos_originales = json.load(f)
                
            if self.datos_originales.get('status') == 'OK':
                self.texto_limpio = self.datos_originales.get('texto_completo', '')
                self._preprocesar_texto()
                print(f"✅ Datos cargados exitosamente desde: {archivo_json}")
                return True
            else:
                print(f"❌ El archivo JSON contiene errores: {self.datos_originales.get('detalle', 'Error desconocido')}")
                return False
                
        except Exception as e:
            print(f"❌ Error al cargar el archivo JSON: {e}")
            return False
    
    def _preprocesar_texto(self):
        """
        Preprocesar el texto para análisis posterior
        """
        if not self.texto_limpio:
            return
            
        # Limpiar y normalizar texto
        texto_normalizado = self._limpiar_texto(self.texto_limpio)
        
        # Extraer palabras
        self.palabras = self._extraer_palabras(texto_normalizado)
        
        # Extraer oraciones
        self.oraciones = self._extraer_oraciones(texto_normalizado)
    
    def _limpiar_texto(self, texto: str) -> str:
        """
        Limpiar y normalizar el texto
        
        Args:
            texto: Texto original
            
        Returns:
            Texto limpio y normalizado
        """
        # Remover caracteres especiales excesivos
        texto = re.sub(r'\s+', ' ', texto)  # Múltiples espacios a uno solo
        texto = re.sub(r'\n+', '\n', texto)  # Múltiples saltos de línea a uno solo
        
        # Limpiar caracteres no deseados pero mantener puntuación importante
        texto = re.sub(r'[^\w\s\.\,\;\:\!\?\(\)\-\ñ\á\é\í\ó\ú\ü]', ' ', texto, flags=re.UNICODE)
        
        return texto.strip()
    
    def _extraer_palabras(self, texto: str) -> List[str]:
        """
        Extraer palabras individuales del texto
        
        Args:
            texto: Texto normalizado
            
        Returns:
            Lista de palabras en minúsculas
        """
        # Extraer solo palabras (sin números ni puntuación)
        palabras = re.findall(r'\b[a-záéíóúüñ]{3,}\b', texto.lower(), flags=re.UNICODE)
        
        # Filtrar palabras comunes (stop words) básicas
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'de', 'del', 'al',
            'en', 'con', 'por', 'para', 'que', 'como', 'cuando', 'donde', 'quien',
            'este', 'esta', 'estos', 'estas', 'ese', 'esa', 'esos', 'esas',
            'aquel', 'aquella', 'aquellos', 'aquellas', 'ser', 'estar', 'tener',
            'hacer', 'decir', 'dar', 'ver', 'saber', 'poder', 'querer', 'venir',
            'muy', 'mas', 'pero', 'también', 'solo', 'hasta', 'sin', 'sobre',
            'todo', 'todos', 'toda', 'todas', 'otro', 'otra', 'otros', 'otras'
        }
        
        palabras_filtradas = [palabra for palabra in palabras if palabra not in stop_words and len(palabra) > 2]
        
        return palabras_filtradas
    
    def _extraer_oraciones(self, texto: str) -> List[str]:
        """
        Extraer oraciones del texto
        
        Args:
            texto: Texto normalizado
            
        Returns:
            Lista de oraciones
        """
        # Dividir por puntos, pero considerar abreviaciones comunes
        oraciones = re.split(r'(?<![A-Z][a-z])\.\s+', texto)
        oraciones = [oracion.strip() for oracion in oraciones if len(oracion.strip()) > 10]
        
        return oraciones
    
    def generar_estadisticas_basicas(self) -> Dict[str, Any]:
        """
        Generar estadísticas básicas del texto
        
        Returns:
            Diccionario con estadísticas del texto
        """
        if not self.texto_limpio:
            return {}
        
        estadisticas = {
            'caracteres_total': len(self.texto_limpio),
            'caracteres_sin_espacios': len(self.texto_limpio.replace(' ', '')),
            'palabras_total': len(self.palabras) if self.palabras else 0,
            'palabras_unicas': len(set(self.palabras)) if self.palabras else 0,
            'oraciones_total': len(self.oraciones) if self.oraciones else 0,
            'promedio_palabras_por_oracion': round(len(self.palabras) / len(self.oraciones), 2) if self.oraciones else 0,
            'promedio_caracteres_por_palabra': round(sum(len(palabra) for palabra in self.palabras) / len(self.palabras), 2) if self.palabras else 0,
        }
        
        return estadisticas
    
    def obtener_palabras_frecuentes(self, top_n: int = 20) -> List[tuple]:
        """
        Obtener las palabras más frecuentes
        
        Args:
            top_n: Número de palabras top a retornar
            
        Returns:
            Lista de tuplas (palabra, frecuencia)
        """
        if not self.palabras:
            return []
        
        contador = Counter(self.palabras)
        return contador.most_common(top_n)
    
    def calcular_metricas_legibilidad(self) -> Dict[str, float]:
        """
        Calcular métricas básicas de legibilidad del texto
        
        Returns:
            Diccionario con métricas de legibilidad
        """
        if not self.palabras or not self.oraciones:
            return {}
        
        # Índice de facilidad de lectura de Flesch (adaptado para español)
        palabras_por_oracion = len(self.palabras) / len(self.oraciones)
        silabas_por_palabra = self._estimar_silabas_promedio()
        
        # Fórmula adaptada de Flesch para español
        flesch_score = 206.84 - (1.02 * palabras_por_oracion) - (0.60 * silabas_por_palabra)
        
        # Índice de complejidad de oraciones
        oraciones_complejas = sum(1 for oracion in self.oraciones if len(oracion.split()) > 25)
        complejidad_oraciones = (oraciones_complejas / len(self.oraciones)) * 100
        
        return {
            'flesch_score': round(flesch_score, 2),
            'palabras_por_oracion': round(palabras_por_oracion, 2),
            'silabas_por_palabra': round(silabas_por_palabra, 2),
            'complejidad_oraciones_pct': round(complejidad_oraciones, 2)
        }
    
    def _estimar_silabas_promedio(self) -> float:
        """
        Estimar el promedio de sílabas por palabra (método simplificado)
        
        Returns:
            Promedio estimado de sílabas por palabra
        """
        if not self.palabras:
            return 0
        
        total_silabas = 0
        vocales = 'aeiouáéíóúü'
        
        for palabra in self.palabras:
            silabas = 0
            vocal_anterior = False
            
            for char in palabra.lower():
                if char in vocales:
                    if not vocal_anterior:
                        silabas += 1
                    vocal_anterior = True
                else:
                    vocal_anterior = False
            
            # Mínimo de 1 sílaba por palabra
            total_silabas += max(1, silabas)
        
        return total_silabas / len(self.palabras)
    
    def extraer_terminos_juridicos(self) -> List[tuple]:
        """
        Extraer términos jurídicos y administrativos comunes en documentos de ADRES
        
        Returns:
            Lista de tuplas (término, frecuencia)
        """
        terminos_juridicos = {
            'resolución', 'decreto', 'concepto', 'artículo', 'parágrafo', 'literal',
            'normatividad', 'reglamentación', 'disposición', 'procedimiento',
            'administración', 'superintendencia', 'ministerio', 'entidad',
            'beneficiario', 'afiliado', 'cotizante', 'prestador', 'eps',
            'régimen', 'contributivo', 'subsidiado', 'salud', 'seguridad',
            'social', 'recursos', 'presupuesto', 'financiación', 'upc',
            'copago', 'cuota', 'moderadora', 'pos', 'pbs', 'cups'
        }
        
        texto_lower = self.texto_limpio.lower()
        frecuencias = []
        
        for termino in terminos_juridicos:
            # Buscar el término como palabra completa
            patron = r'\b' + re.escape(termino) + r'\b'
            coincidencias = len(re.findall(patron, texto_lower))
            if coincidencias > 0:
                frecuencias.append((termino, coincidencias))
        
        # Ordenar por frecuencia descendente
        return sorted(frecuencias, key=lambda x: x[1], reverse=True)
    
    def generar_reporte_completo(self, archivo_salida: str = None) -> Dict[str, Any]:
        """
        Generar un reporte completo del análisis
        
        Args:
            archivo_salida: Ruta del archivo donde guardar el reporte (opcional)
            
        Returns:
            Diccionario con el reporte completo
        """
        reporte = {
            'metadatos': {
                'fecha_analisis': datetime.now().isoformat(),
                'archivo_fuente': self.archivo_json,
                'version_analizador': '1.0'
            },
            'datos_originales': {
                'url_fuente': self.datos_originales.get('url_original', 'No disponible') if self.datos_originales else 'No disponible',
                'fecha_extraccion': self.datos_originales.get('fecha_extraccion', 'No disponible') if self.datos_originales else 'No disponible',
                'status_extraccion': self.datos_originales.get('status', 'No disponible') if self.datos_originales else 'No disponible'
            },
            'estadisticas_basicas': self.generar_estadisticas_basicas(),
            'palabras_frecuentes': self.obtener_palabras_frecuentes(15),
            'metricas_legibilidad': self.calcular_metricas_legibilidad(),
            'terminos_juridicos': self.extraer_terminos_juridicos()
        }
        
        if archivo_salida:
            self._guardar_reporte(reporte, archivo_salida)
        
        return reporte
    
    def _guardar_reporte(self, reporte: Dict[str, Any], archivo_salida: str):
        """
        Guardar el reporte en archivo JSON y generar resumen en Markdown
        
        Args:
            reporte: Diccionario con el reporte completo
            archivo_salida: Ruta base del archivo de salida
        """
        try:
            # Guardar en formato JSON
            ruta_json = archivo_salida if archivo_salida.endswith('.json') else f"{archivo_salida}.json"
            with open(ruta_json, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=4, ensure_ascii=False)
            
            # Generar resumen en Markdown
            ruta_md = ruta_json.replace('.json', '_resumen.md')
            self._generar_markdown(reporte, ruta_md)
            
            print(f"✅ Reporte guardado en:")
            print(f"   📊 JSON detallado: {ruta_json}")
            print(f"   📝 Resumen Markdown: {ruta_md}")
            
        except Exception as e:
            print(f"❌ Error al guardar el reporte: {e}")
    
    def _generar_markdown(self, reporte: Dict[str, Any], archivo_md: str):
        """
        Generar un resumen en formato Markdown del análisis
        
        Args:
            reporte: Diccionario con el reporte completo
            archivo_md: Ruta del archivo Markdown
        """
        contenido_md = f"""# 📊 Análisis de Contenido ADRES

**Fecha de análisis**: {reporte['metadatos']['fecha_analisis']}  
**Archivo fuente**: {reporte['metadatos']['archivo_fuente']}  
**URL original**: {reporte['datos_originales']['url_fuente']}

## 📈 Estadísticas Básicas

| Métrica | Valor |
|---------|-------|
| **Caracteres totales** | {reporte['estadisticas_basicas'].get('caracteres_total', 'N/A'):,} |
| **Palabras totales** | {reporte['estadisticas_basicas'].get('palabras_total', 'N/A'):,} |
| **Palabras únicas** | {reporte['estadisticas_basicas'].get('palabras_unicas', 'N/A'):,} |
| **Oraciones totales** | {reporte['estadisticas_basicas'].get('oraciones_total', 'N/A'):,} |
| **Palabras por oración** | {reporte['estadisticas_basicas'].get('promedio_palabras_por_oracion', 'N/A')} |

## 🎯 Métricas de Legibilidad

| Métrica | Valor | Interpretación |
|---------|-------|----------------|
| **Índice Flesch** | {reporte['metricas_legibilidad'].get('flesch_score', 'N/A')} | {'Muy fácil' if reporte['metricas_legibilidad'].get('flesch_score', 0) > 80 else 'Fácil' if reporte['metricas_legibilidad'].get('flesch_score', 0) > 65 else 'Moderado' if reporte['metricas_legibilidad'].get('flesch_score', 0) > 50 else 'Difícil'} |
| **Sílabas por palabra** | {reporte['metricas_legibilidad'].get('silabas_por_palabra', 'N/A')} | {'Normal' if reporte['metricas_legibilidad'].get('silabas_por_palabra', 0) < 3 else 'Complejo'} |
| **Oraciones complejas** | {reporte['metricas_legibilidad'].get('complejidad_oraciones_pct', 'N/A')}% | {'Aceptable' if reporte['metricas_legibilidad'].get('complejidad_oraciones_pct', 0) < 30 else 'Alto'} |

## 🔤 Palabras Más Frecuentes

"""
        
        for i, (palabra, freq) in enumerate(reporte['palabras_frecuentes'][:10], 1):
            contenido_md += f"{i}. **{palabra}** ({freq} veces)\n"
        
        contenido_md += "\n## ⚖️ Términos Jurídicos Identificados\n\n"
        
        if reporte['terminos_juridicos']:
            for termino, freq in reporte['terminos_juridicos'][:10]:
                contenido_md += f"- **{termino.title()}**: {freq} menciones\n"
        else:
            contenido_md += "No se identificaron términos jurídicos específicos.\n"
        
        contenido_md += f"""
## 📋 Resumen Ejecutivo

Este documento contiene **{reporte['estadisticas_basicas'].get('palabras_total', 0):,} palabras** distribuidas en **{reporte['estadisticas_basicas'].get('oraciones_total', 0)} oraciones**. 

**Nivel de complejidad**: {'Alto - Requiere conocimientos especializados' if reporte['metricas_legibilidad'].get('flesch_score', 50) < 50 else 'Moderado - Accesible para público general'}

**Características del texto**:
- Vocabulario técnico especializado en {'alto grado' if len(reporte['terminos_juridicos']) > 10 else 'moderado grado' if len(reporte['terminos_juridicos']) > 5 else 'bajo grado'}
- Estructura {'compleja' if reporte['metricas_legibilidad'].get('palabras_por_oracion', 0) > 20 else 'simple'} de oraciones
- Contenido {'normativo y administrativo' if any('resoluci' in t[0] or 'decreto' in t[0] for t in reporte['terminos_juridicos']) else 'informativo'}

---
*Análisis generado por Analizador de Contenido ADRES v{reporte['metadatos']['version_analizador']}*
"""
        
        with open(archivo_md, 'w', encoding='utf-8') as f:
            f.write(contenido_md)


def main():
    """
    Función principal para ejecutar el análisis
    """
    print("=" * 70)
    print("📊 ANALIZADOR DE CONTENIDO ADRES - TALLER BIG DATA")
    print("=" * 70)
    
    # Buscar archivos JSON en el directorio de salida del scraper
    directorio_busqueda = 'web_scraping_adres_output'
    
    if not os.path.exists(directorio_busqueda):
        print(f"❌ No se encontró el directorio: {directorio_busqueda}")
        print("   Asegúrate de ejecutar primero el web scraper.")
        return 1
    
    # Buscar archivos JSON
    archivos_json = [f for f in os.listdir(directorio_busqueda) if f.endswith('.json')]
    
    if not archivos_json:
        print(f"❌ No se encontraron archivos JSON en: {directorio_busqueda}")
        return 1
    
    # Usar el archivo más reciente
    archivo_mas_reciente = max(archivos_json, key=lambda x: os.path.getctime(os.path.join(directorio_busqueda, x)))
    ruta_archivo = os.path.join(directorio_busqueda, archivo_mas_reciente)
    
    print(f"📂 Analizando archivo: {archivo_mas_reciente}")
    
    # Crear analizador y procesar
    analizador = AnalizadorContenidoADRES(ruta_archivo)
    
    if not analizador.datos_originales:
        print("❌ No se pudieron cargar los datos del archivo JSON")
        return 1
    
    # Generar reporte
    archivo_salida = os.path.join(directorio_busqueda, f"analisis_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    reporte = analizador.generar_reporte_completo(archivo_salida)
    
    # Mostrar resumen en consola
    print(f"\n📈 RESUMEN DEL ANÁLISIS:")
    print(f"   • Palabras totales: {reporte['estadisticas_basicas'].get('palabras_total', 0):,}")
    print(f"   • Palabras únicas: {reporte['estadisticas_basicas'].get('palabras_unicas', 0):,}")
    print(f"   • Oraciones: {reporte['estadisticas_basicas'].get('oraciones_total', 0)}")
    print(f"   • Índice de legibilidad: {reporte['metricas_legibilidad'].get('flesch_score', 'N/A')}")
    print(f"   • Términos jurídicos encontrados: {len(reporte['terminos_juridicos'])}")
    
    print(f"\n🎯 Palabras más frecuentes:")
    for i, (palabra, freq) in enumerate(reporte['palabras_frecuentes'][:5], 1):
        print(f"   {i}. {palabra} ({freq} veces)")
    
    print(f"\n✅ Análisis completado exitosamente")
    
    return 0

# Bloque de ejecución removido - módulo de librería
