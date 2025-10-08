#!/usr/bin/env python3
"""
Analizador de Contenido para ADRES Scraper
==========================================
Análisis y procesamiento de contenido extraído
"""

import re
from datetime import datetime
from typing import Dict, List, Any, Tuple
from collections import Counter


class ContentAnalyzer:
    """
    Analizador de contenido para documentos de ADRES
    """
    
    def __init__(self):
        """Inicializar analizador"""
        # Palabras clave específicas de ADRES
        self.adres_keywords = [
            'adres', 'administradora', 'recursos', 'seguridad social',
            'salud', 'resolución', 'concepto', 'normograma',
            'eps', 'ips', 'prestadores', 'afiliados', 'cobertura',
            'pago', 'reclamaciones', 'tutela', 'derecho', 'fundamental'
        ]
        
        # Palabras clave legales
        self.legal_keywords = [
            'decreto', 'ley', 'resolución', 'circular', 'concepto',
            'jurisprudencia', 'normativa', 'reglamento', 'disposición',
            'artículo', 'parágrafo', 'inciso', 'literal'
        ]
    
    def analyze_content(self, text: str, url: str = "") -> Dict[str, Any]:
        """
        Realizar análisis completo del contenido
        
        Args:
            text: Texto a analizar
            url: URL de origen (opcional)
            
        Returns:
            Diccionario con análisis del contenido
        """
        if not text or not text.strip():
            return self._create_empty_analysis()
        
        analysis = {
            'estadisticas_basicas': self._analyze_basic_stats(text),
            'palabras_clave_adres': self._find_adres_keywords(text),
            'palabras_clave_legales': self._find_legal_keywords(text),
            'estructura_documento': self._analyze_document_structure(text),
            'metadata_extraccion': {
                'fecha_analisis': datetime.now().isoformat(),
                'url_origen': url,
                'version_analizador': '2.0.0'
            }
        }
        
        # Añadir clasificación del documento
        analysis['clasificacion'] = self._classify_document(analysis)
        
        return analysis
    
    def _analyze_basic_stats(self, text: str) -> Dict[str, Any]:
        """
        Análisis estadístico básico del texto
        
        Args:
            text: Texto a analizar
            
        Returns:
            Diccionario con estadísticas básicas
        """
        words = text.split()
        sentences = self._split_sentences(text)
        paragraphs = self._split_paragraphs(text)
        
        return {
            'caracteres_total': len(text),
            'caracteres_sin_espacios': len(text.replace(' ', '')),
            'palabras_total': len(words),
            'oraciones_total': len(sentences),
            'parrafos_total': len(paragraphs),
            'promedio_palabras_por_oracion': len(words) / max(len(sentences), 1),
            'promedio_caracteres_por_palabra': sum(len(word) for word in words) / max(len(words), 1)
        }
    
    def _find_adres_keywords(self, text: str) -> Dict[str, Any]:
        """
        Encontrar palabras clave específicas de ADRES
        
        Args:
            text: Texto a analizar
            
        Returns:
            Diccionario con palabras clave encontradas
        """
        text_lower = text.lower()
        found_keywords = {}
        total_matches = 0
        
        for keyword in self.adres_keywords:
            count = len(re.findall(r'\b' + re.escape(keyword.lower()) + r'\b', text_lower))
            if count > 0:
                found_keywords[keyword] = count
                total_matches += count
        
        return {
            'palabras_encontradas': found_keywords,
            'total_coincidencias': total_matches,
            'densidad_keywords': (total_matches / len(text.split())) * 100 if text.split() else 0
        }
    
    def _find_legal_keywords(self, text: str) -> Dict[str, Any]:
        """
        Encontrar términos legales y normativos
        
        Args:
            text: Texto a analizar
            
        Returns:
            Diccionario con términos legales encontrados
        """
        text_lower = text.lower()
        found_keywords = {}
        
        for keyword in self.legal_keywords:
            count = len(re.findall(r'\b' + re.escape(keyword.lower()) + r'\b', text_lower))
            if count > 0:
                found_keywords[keyword] = count
        
        # Buscar patrones de números de normas
        norm_patterns = {
            'resoluciones': r'resolución\s+(?:número\s+)?(\d+)',
            'decretos': r'decreto\s+(?:número\s+)?(\d+)',
            'leyes': r'ley\s+(?:número\s+)?(\d+)',
            'articulos': r'artículo\s+(?:número\s+)?(\d+)'
        }
        
        found_norms = {}
        for norm_type, pattern in norm_patterns.items():
            matches = re.findall(pattern, text_lower)
            if matches:
                found_norms[norm_type] = list(set(matches))  # Eliminar duplicados
        
        return {
            'terminos_legales': found_keywords,
            'normas_identificadas': found_norms
        }
    
    def _analyze_document_structure(self, text: str) -> Dict[str, Any]:
        """
        Analizar la estructura del documento
        
        Args:
            text: Texto a analizar
            
        Returns:
            Diccionario con análisis de estructura
        """
        # Detectar posibles títulos (líneas cortas en mayúsculas o con patrones específicos)
        lines = text.split('\n')
        potential_titles = []
        
        for line in lines:
            line_clean = line.strip()
            if line_clean and (
                (len(line_clean) < 100 and line_clean.isupper()) or
                re.match(r'^[A-Z][^.]*[^.]$', line_clean) and len(line_clean.split()) <= 10
            ):
                potential_titles.append(line_clean)
        
        # Detectar listas (líneas que empiezan con números, letras o viñetas)
        list_items = []
        for line in lines:
            line_clean = line.strip()
            if re.match(r'^[\d\w)]\.|^[-•*]\s|^\w\)', line_clean):
                list_items.append(line_clean)
        
        # Detectar fechas
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{4}',
            r'\d{1,2} de \w+ de \d{4}',
            r'\w+ \d{1,2}, \d{4}'
        ]
        
        dates_found = []
        for pattern in date_patterns:
            dates_found.extend(re.findall(pattern, text))
        
        return {
            'posibles_titulos': potential_titles[:10],  # Limitar a 10
            'elementos_lista': len(list_items),
            'fechas_encontradas': list(set(dates_found)),
            'tiene_estructura_formal': len(potential_titles) > 0 and len(list_items) > 0
        }
    
    def _classify_document(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clasificar el tipo de documento basado en el análisis
        
        Args:
            analysis: Análisis previo del documento
            
        Returns:
            Diccionario con clasificación
        """
        adres_density = analysis['palabras_clave_adres']['densidad_keywords']
        legal_terms = len(analysis['palabras_clave_legales']['terminos_legales'])
        has_norms = bool(analysis['palabras_clave_legales']['normas_identificadas'])
        
        # Lógica de clasificación
        document_type = "documento_general"
        confidence = 0.5
        
        if adres_density > 2 and legal_terms > 3:
            document_type = "documento_normativo_adres"
            confidence = 0.9
        elif adres_density > 1:
            document_type = "documento_adres"
            confidence = 0.7
        elif legal_terms > 2 or has_norms:
            document_type = "documento_legal"
            confidence = 0.6
        
        return {
            'tipo_documento': document_type,
            'confianza': confidence,
            'es_documento_adres': adres_density > 0.5,
            'es_documento_legal': legal_terms > 1 or has_norms,
            'criterios_clasificacion': {
                'densidad_adres': adres_density,
                'terminos_legales': legal_terms,
                'tiene_normas': has_norms
            }
        }
    
    def _split_sentences(self, text: str) -> List[str]:
        """
        Dividir texto en oraciones
        
        Args:
            text: Texto a dividir
            
        Returns:
            Lista de oraciones
        """
        # Patrón simple para división de oraciones
        sentences = re.split(r'[.!?]+\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _split_paragraphs(self, text: str) -> List[str]:
        """
        Dividir texto en párrafos
        
        Args:
            text: Texto a dividir
            
        Returns:
            Lista de párrafos
        """
        paragraphs = text.split('\n\n')
        return [p.strip() for p in paragraphs if p.strip()]
    
    def _create_empty_analysis(self) -> Dict[str, Any]:
        """
        Crear análisis vacío para texto inexistente
        
        Returns:
            Diccionario con análisis vacío
        """
        return {
            'estadisticas_basicas': {
                'caracteres_total': 0,
                'palabras_total': 0,
                'oraciones_total': 0,
                'parrafos_total': 0
            },
            'palabras_clave_adres': {'palabras_encontradas': {}, 'total_coincidencias': 0},
            'palabras_clave_legales': {'terminos_legales': {}, 'normas_identificadas': {}},
            'estructura_documento': {'posibles_titulos': [], 'elementos_lista': 0},
            'clasificacion': {
                'tipo_documento': 'documento_vacio',
                'confianza': 0.0,
                'es_documento_adres': False
            },
            'metadata_extraccion': {
                'fecha_analisis': datetime.now().isoformat(),
                'error': 'Texto vacío o no válido'
            }
        }
    
    def extract_key_phrases(self, text: str, max_phrases: int = 10) -> List[Tuple[str, int]]:
        """
        Extraer frases clave del texto
        
        Args:
            text: Texto a analizar
            max_phrases: Número máximo de frases a retornar
            
        Returns:
            Lista de tuplas (frase, frecuencia)
        """
        if not text:
            return []
        
        # Extraer bigramas y trigramas
        words = re.findall(r'\b\w+\b', text.lower())
        
        phrases = []
        
        # Bigramas
        for i in range(len(words) - 1):
            phrase = f"{words[i]} {words[i+1]}"
            phrases.append(phrase)
        
        # Trigramas
        for i in range(len(words) - 2):
            phrase = f"{words[i]} {words[i+1]} {words[i+2]}"
            phrases.append(phrase)
        
        # Contar frecuencias
        phrase_counts = Counter(phrases)
        
        # Filtrar frases muy cortas o comunes
        filtered_phrases = [
            (phrase, count) for phrase, count in phrase_counts.items()
            if count > 1 and len(phrase) > 5
        ]
        
        # Ordenar por frecuencia
        filtered_phrases.sort(key=lambda x: x[1], reverse=True)
        
        return filtered_phrases[:max_phrases]