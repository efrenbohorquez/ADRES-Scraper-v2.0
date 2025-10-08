# ADRES Scraper 🇨🇴

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Web scraping ético para documentos oficiales de ADRES (Agencia de Regulación de Energía y Gas) de Colombia.

## 📋 Descripción

Este proyecto proporciona una solución completa para la descarga y almacenamiento ético de documentos PDF de ADRES, respetando las políticas del sitio web y implementando buenas prácticas de web scraping.

### Características principales

- ✅ **Scraping Ético**: Implementa delays apropiados y respeta el robots.txt
- 📄 **Descarga de PDFs**: Descarga automática de documentos oficiales
- 🗄️ **Almacenamiento MongoDB**: Guarda documentos y metadatos en MongoDB Atlas
- 🔍 **Análisis de Contenido**: Extrae información relevante de documentos
- 📊 **Monitoreo Visual**: Interfaz para seguimiento de procesos
- 🛡️ **Validación Ética**: Verificación automática de cumplimiento normativo

## 🚀 Instalación Rápida

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/adres-scraper.git
cd adres-scraper

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

## 📖 Uso Básico

```python
from adres_scraper import ADREScraper, MongoDBManager, PDFDownloader, Config

# Cargar configuración
config = Config.from_file('config/config_mongodb_atlas.json')

# Inicializar componentes
scraper = ADREScraper(config)
db_manager = MongoDBManager(config)
pdf_downloader = PDFDownloader(config)

# Realizar scraping
url = "https://www.adres.gov.co/biblioteca-y-publicaciones/resoluciones"
resultado = scraper.scrape_document(url)

if resultado['exito']:
    # Descargar PDFs encontrados
    pdfs_descargados = pdf_downloader.download_pdfs_from_page(url)
    
    # Almacenar en MongoDB
    for pdf_info in pdfs_descargados:
        db_manager.store_pdf_file(
            pdf_content=pdf_info['contenido'],
            filename=pdf_info['nombre_archivo'],
            metadata=pdf_info['metadata']
        )
```

## 🏗️ Arquitectura

```
adres_scraper/
├── core/                   # Núcleo del sistema
├── mongodb/               # Gestión de base de datos  
├── downloaders/           # Descargadores especializados
├── config/                # Configuración del sistema
└── utils/                 # Utilidades auxiliares
```

## ⚙️ Configuración

Crear archivo de configuración:
```json
{
  "mongodb": {
    "connection_string": "mongodb+srv://...",
    "database_name": "adres_scraper"
  },
  "scraping": {
    "delay_between_requests": 2.0,
    "max_retries": 3,
    "timeout": 30
  }
}
```

## 🤝 Ética y Cumplimiento

- **Respeto al robots.txt**: Verificación automática
- **Delays apropiados**: 2+ segundos entre requests
- **User-Agent identificado**: Transparencia total
- **Solo contenido público**: Sin acceso restringido
- **Propósito educativo**: Uso académico únicamente

## 📝 Licencia

MIT License - Ver [LICENSE](LICENSE) para más detalles.

## 👥 Autores

**Taller Big Data 2025** - Desarrollo inicial

---

**🇨🇴 Hecho con ❤️ para la comunidad de datos colombiana**