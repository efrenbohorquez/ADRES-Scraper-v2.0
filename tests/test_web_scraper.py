#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Suite para el Proyecto de Web Scraping ADRES
==============================================

Este módulo contiene tests básicos para validar la funcionalidad
del web scraper y sus componentes éticos.
"""

import pytest
import os
import sys
import json
from unittest.mock import Mock, patch, MagicMock

# Agregar el directorio src al path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from web_scraper_adres import WebScraperADRES, ConfiguracionEticaADRES
    from analizador_contenido import AnalizadorContenidoADRES
    from validador_etico import ValidadorEtico
except ImportError as e:
    pytest.skip(f"No se pudieron importar los módulos: {e}", allow_module_level=True)


class TestConfiguracionEticaADRES:
    """Tests para la configuración ética del scraper"""
    
    def test_configuracion_tiene_valores_apropiados(self):
        """Test que verifica valores éticos en la configuración"""
        config = ConfiguracionEticaADRES()
        
        # Verificar que existe delay mínimo
        assert config.DELAY_SECONDS >= 0.5, "Delay debe ser mínimo 0.5 segundos"
        
        # Verificar timeout apropiado
        assert 5 <= config.REQUEST_TIMEOUT <= 30, "Timeout debe estar entre 5-30 segundos"
        
        # Verificar headers apropiados
        assert 'User-Agent' in config.HEADERS, "Debe incluir User-Agent"
        assert len(config.HEADERS['User-Agent']) > 10, "User-Agent debe ser descriptivo"
    
    def test_url_objetivo_es_valida(self):
        """Test que verifica que la URL objetivo sea válida"""
        config = ConfiguracionEticaADRES()
        
        assert config.URL_OBJETIVO.startswith('https://'), "URL debe usar HTTPS"
        assert 'adres.gov.co' in config.URL_OBJETIVO, "URL debe ser del dominio de ADRES"


class TestWebScraperADRES:
    """Tests para la funcionalidad principal del scraper"""
    
    def setup_method(self):
        """Configurar cada test"""
        self.scraper = WebScraperADRES()
    
    @patch('requests.get')
    def test_manejo_error_http(self, mock_get):
        """Test del manejo de errores HTTP"""
        # Simular error HTTP 404
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("404 Not Found")
        mock_get.return_value = mock_response
        
        resultado = self.scraper.extraer_contenido_adres("https://ejemplo.com")
        
        assert resultado['status'] != 'OK', "Debe manejar errores HTTP apropiadamente"
        assert 'Error' in resultado['status'], "Status debe indicar error"
    
    @patch('requests.get')
    def test_extraccion_exitosa_simulada(self, mock_get):
        """Test de extracción exitosa con contenido simulado"""
        # Simular respuesta exitosa
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'<html><body><div id="main"><p>Contenido de prueba</p></div></body></html>'
        mock_response.headers = {'content-type': 'text/html; charset=utf-8'}
        mock_response.encoding = 'utf-8'
        mock_get.return_value = mock_response
        
        resultado = self.scraper.extraer_contenido_adres("https://ejemplo.com")
        
        assert resultado['status'] == 'OK', "Extracción debe ser exitosa"
        assert 'texto_completo' in resultado, "Debe incluir texto extraído"
        assert len(resultado['texto_completo']) > 0, "Debe extraer contenido"
    
    def test_limpieza_texto_funciona(self):
        """Test que la limpieza de texto funcione apropiadamente"""
        from bs4 import BeautifulSoup
        
        html_test = """
        <div>
            <script>alert('test');</script>
            <p>Texto válido</p>
            <style>.test { color: red; }</style>
            <p>Otro párrafo</p>
        </div>
        """
        
        soup = BeautifulSoup(html_test, 'html.parser')
        texto_limpio = self.scraper._limpiar_texto(soup)
        
        assert 'alert' not in texto_limpio, "Scripts deben ser removidos"
        assert 'color: red' not in texto_limpio, "Estilos deben ser removidos" 
        assert 'Texto válido' in texto_limpio, "Contenido válido debe mantenerse"


class TestAnalizadorContenido:
    """Tests para el analizador de contenido"""
    
    def setup_method(self):
        """Configurar cada test"""
        self.analizador = AnalizadorContenidoADRES()
    
    def test_extraccion_palabras(self):
        """Test de extracción de palabras"""
        texto_prueba = "Este es un texto de prueba para el análisis de contenido."
        palabras = self.analizador._extraer_palabras(texto_prueba)
        
        assert isinstance(palabras, list), "Debe retornar una lista"
        assert 'texto' in palabras, "Debe extraer palabras significativas"
        assert 'es' not in palabras, "Debe filtrar stop words"
    
    def test_extraccion_oraciones(self):
        """Test de extracción de oraciones"""
        texto_prueba = "Primera oración. Segunda oración con más contenido. Tercera oración final."
        oraciones = self.analizador._extraer_oraciones(texto_prueba)
        
        assert len(oraciones) >= 2, "Debe extraer múltiples oraciones"
        assert all(len(oracion) > 5 for oracion in oraciones), "Oraciones deben tener contenido sustancial"
    
    def test_estadisticas_basicas(self):
        """Test de generación de estadísticas"""
        self.analizador.texto_limpio = "Texto de prueba para estadísticas básicas del analizador."
        self.analizador._preprocesar_texto()
        
        stats = self.analizador.generar_estadisticas_basicas()
        
        assert 'caracteres_total' in stats, "Debe incluir conteo de caracteres"
        assert 'palabras_total' in stats, "Debe incluir conteo de palabras"
        assert stats['caracteres_total'] > 0, "Debe contar caracteres"
        assert stats['palabras_total'] > 0, "Debe contar palabras"


class TestValidadorEtico:
    """Tests para el validador ético"""
    
    def setup_method(self):
        """Configurar cada test"""
        self.validador = ValidadorEtico()
    
    def test_validacion_headers_eticos(self):
        """Test de validación de headers"""
        headers_buenos = {
            'User-Agent': 'Taller-BigData-Educativo/1.0 (academic@university.edu)',
            'Accept': 'text/html,application/xhtml+xml',
            'Accept-Language': 'es-ES,es;q=0.9'
        }
        
        resultado = self.validador.validar_headers_eticos(headers_buenos)
        
        assert resultado['puntuacion'] > 0, "Headers éticos deben tener puntuación positiva"
        assert any('académico' in obs.lower() or 'educativo' in obs.lower() 
                  for obs in resultado['observaciones']), "Debe reconocer propósito académico"
    
    def test_validacion_delays(self):
        """Test de validación de delays"""
        resultado = self.validador.validar_configuracion_delays(1.0, 10)
        
        assert resultado['puntuacion'] > 15, "Delay de 1 segundo debe tener buena puntuación"
        assert any('apropiado' in obs.lower() for obs in resultado['observaciones']), "Debe reconocer delay apropiado"
    
    def test_validacion_delay_insuficiente(self):
        """Test de detección de delay insuficiente"""
        resultado = self.validador.validar_configuracion_delays(0.1, 5)
        
        assert resultado['puntuacion'] < 15, "Delay muy bajo debe tener puntuación baja"


class TestIntegracion:
    """Tests de integración para flujo completo"""
    
    def test_flujo_completo_con_datos_simulados(self, tmp_path):
        """Test del flujo completo con datos simulados"""
        # Crear archivo JSON simulado
        datos_simulados = {
            'url_original': 'https://ejemplo.com/test',
            'fecha_extraccion': '2024-10-05T15:30:45.123456',
            'texto_completo': 'Este es un texto de prueba para el concepto de ADRES sobre normatividad y reglamentación.',
            'longitud_caracteres': 100,
            'longitud_palabras': 15,
            'status': 'OK'
        }
        
        archivo_json = tmp_path / "test_concepto.json"
        with open(archivo_json, 'w', encoding='utf-8') as f:
            json.dump(datos_simulados, f)
        
        # Probar análisis
        analizador = AnalizadorContenidoADRES(str(archivo_json))
        assert analizador.datos_originales is not None, "Debe cargar datos simulados"
        
        reporte = analizador.generar_reporte_completo()
        assert reporte['datos_originales']['status_extraccion'] == 'OK', "Debe procesar datos correctamente"


# Configuración de pytest
def pytest_configure(config):
    """Configuración global de pytest"""
    config.addinivalue_line(
        "markers", "slow: marca tests como lentos (puede requerir conexión a internet)"
    )


# Test de conectividad real (marcado como slow)
@pytest.mark.slow
class TestConectividadReal:
    """Tests que requieren conectividad real (opcionales)"""
    
    def test_verificacion_robots_txt_real(self):
        """Test de verificación real de robots.txt (requiere internet)"""
        validador = ValidadorEtico()
        resultado = validador.verificar_robots_txt('https://normograma.adres.gov.co')
        
        # Este test puede fallar si no hay conexión, pero no debería causar error
        assert 'robots_txt_existe' in resultado, "Debe intentar verificar robots.txt"


if __name__ == '__main__':
    # Ejecutar tests si se llama directamente
    pytest.main([__file__, '-v'])