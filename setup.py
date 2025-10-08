#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup script para ADRES Scraper v2.0
====================================

Paquete optimizado para web scraping ético de documentos ADRES.
"""

from setuptools import setup, find_packages
import os
import sys

# Verificar versión de Python
if sys.version_info < (3, 8):
    raise RuntimeError("ADRES Scraper requiere Python 3.8 o superior.")

# Leer el README para la descripción larga
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Taller de Web Scraping Ético aplicado a documentos de ADRES"

# Leer requirements.txt
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    requirements = []
    
    try:
        with open(req_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Ignorar comentarios y líneas vacías
                if line and not line.startswith('#'):
                    requirements.append(line)
    except FileNotFoundError:
        # Dependencias mínimas si no existe requirements.txt
        requirements = [
            'requests>=2.31.0',
            'beautifulsoup4>=4.12.2',
            'lxml>=4.9.3',
            'pandas>=2.0.3'
        ]
    
    return requirements

# Configuración del paquete
setup(
    # Información básica del proyecto
    name="web-scraping-adres-taller",
    version="1.0.0",
    description="Taller de Big Data: Web Scraping Ético para documentos de ADRES",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    
    # Información del autor
    author="Taller Big Data 2024",
    author_email="bigdata.taller@ejemplo.com",
    
    # URLs del proyecto
    url="https://github.com/ejemplo/web-scraping-adres-taller",
    project_urls={
        "Documentation": "https://github.com/ejemplo/web-scraping-adres-taller/wiki",
        "Issues": "https://github.com/ejemplo/web-scraping-adres-taller/issues",
        "Source": "https://github.com/ejemplo/web-scraping-adres-taller",
    },
    
    # Configuración de paquetes
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    
    # Scripts ejecutables
    entry_points={
        'console_scripts': [
            'scraper-adres=web_scraper_adres:main',
        ],
    },
    
    # Dependencias
    install_requires=read_requirements(),
    
    # Metadatos del proyecto
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: Developers",
        "Topic :: Education",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Natural Language :: Spanish",
    ],
    
    # Requisitos de Python
    python_requires=">=3.8",
    
    # Archivos adicionales a incluir
    include_package_data=True,
    package_data={
        '': ['*.md', '*.txt', '*.yml', '*.yaml', '*.json'],
    },
    
    # Keywords para búsqueda
    keywords=[
        "web-scraping", 
        "big-data", 
        "adres", 
        "etico", 
        "educacional", 
        "taller",
        "normograma",
        "beautifulsoup"
    ],
    
    # Dependencias opcionales para desarrollo
    extras_require={
        'dev': [
            'pytest>=7.4.0',
            'pytest-cov>=4.1.0',
            'black>=23.7.0',
            'flake8>=6.0.0',
            'mypy>=1.5.1',
        ],
        'docs': [
            'sphinx>=7.1.0',
            'sphinx-rtd-theme>=1.3.0',
        ],
        'analysis': [
            'matplotlib>=3.7.2',
            'seaborn>=0.12.2',
            'wordcloud>=1.9.2',
            'nltk>=3.8.1',
        ]
    },
    
    # Configuración de distribución
    zip_safe=False,
)