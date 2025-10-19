# 🕷️ Web Scraping Ético ADRES - Taller Big Data# ADRES Scraper 🇨🇴



[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)

[![BeautifulSoup4](https://img.shields.io/badge/BeautifulSoup4-4.12+-green.svg)](https://www.crummy.com/software/BeautifulSoup/)[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)



**Proyecto educativo de Web Scraping Ético** aplicado al sitio web de ADRES (Administradora de Recursos del Sistema General de Seguridad Social en Salud).Web scraping ético para documentos oficiales de ADRES (Administradora de los Recursos del Sistema General de Seguridad Social en Salud) de Colombia.



## 👨‍🎓 Información Académica## 📋 Descripción



- **Universidad**: Universidad Central de ColombiaEste proyecto proporciona una solución completa para la descarga y almacenamiento ético de documentos PDF de ADRES (Administradora de los Recursos del Sistema General de Seguridad Social en Salud), la entidad colombiana encargada de administrar los recursos financieros del sistema de salud. Respeta las políticas del sitio web e implementa buenas prácticas de web scraping.

- **Curso**: Taller de Big Data

- **Autor**: Efren Bohorquez Vargas### Características principales

- **Instructor**: Luis Fernando Castellanos

- **Año**: 2024-2025- ✅ **Scraping Ético**: Implementa delays apropiados y respeta el robots.txt

- 📄 **Descarga de PDFs**: Descarga automática de documentos oficiales

## 📋 Descripción- 🗄️ **Almacenamiento MongoDB**: Guarda documentos y metadatos en MongoDB Atlas

- 🔍 **Análisis de Contenido**: Extrae información relevante de documentos

Este proyecto implementa técnicas de web scraping ético para extraer y analizar información del portal de ADRES, respetando:- 📊 **Monitoreo Visual**: Interfaz para seguimiento de procesos

- 🛡️ **Validación Ética**: Verificación automática de cumplimiento normativo

- ✅ Robots.txt y políticas del sitio

- ✅ Delays entre peticiones (3 segundos mínimo)## 🚀 Instalación Rápida

- ✅ User-Agent identificado

- ✅ Límites de tasa de solicitudes```bash

- ✅ Sin sobrecarga del servidor# Clonar el repositorio

git clone https://github.com/tu-usuario/adres-scraper.git

## 🎯 Característicascd adres-scraper



- **Scraping Ético**: Configuración profesional con principios éticos# Crear entorno virtual

- **Análisis de Contenido**: Extracción de keywords y metadatapython -m venv venv

- **Detección de PDFs**: Identificación automática de documentossource venv/bin/activate  # En Windows: venv\Scripts\activate

- **MongoDB Atlas**: Almacenamiento estructurado opcional

- **Jupyter Notebook**: Tutorial interactivo completo# Instalar dependencias

pip install -r requirements.txt

## 📁 Estructura del Proyecto```



```## 📖 Uso Básico

web_scraping_adres_taller/

│```python

├── 📓 Taller_WebScraping_ADRES.ipynb    # Notebook educativo principalfrom adres_scraper import ADREScraper, MongoDBManager, PDFDownloader, Config

├── 📄 Taller_WebScraping_ADRES.html     # Exportación HTML

├── 📄 Taller_WebScraping_ADRES.pdf      # Documentación PDF# Cargar configuración

│config = Config.from_file('config/config_mongodb_atlas.json')

├── src/                                  # Módulos core

│   ├── web_scraper_adres.py             # Scraper principal# Inicializar componentes

│   ├── validador_etico.py               # Validación éticascraper = ADREScraper(config)

│   ├── mongodb_manager.py               # Gestión MongoDBdb_manager = MongoDBManager(config)

│   └── analizador_contenido.py          # Análisis de contenidopdf_downloader = PDFDownloader(config)

│

├── config/                               # Configuraciones# Realizar scraping

├── data/                                 # Datos extraídosurl = "https://www.adres.gov.co/biblioteca-y-publicaciones/resoluciones"

├── docs/                                 # Documentación adicionalresultado = scraper.scrape_document(url)

├── logs/                                 # Logs del sistema

├── tests/                                # Tests unitariosif resultado['exito']:

├── archive_tests/                        # Scripts archivados    # Descargar PDFs encontrados

│    pdfs_descargados = pdf_downloader.download_pdfs_from_page(url)

├── requirements.txt                      # Dependencias Python    

├── setup.py                              # Instalación del paquete    # Almacenar en MongoDB

├── .gitignore                           # Archivos ignorados por Git    for pdf_info in pdfs_descargados:

└── README.md                            # Este archivo        db_manager.store_pdf_file(

            pdf_content=pdf_info['contenido'],

```            filename=pdf_info['nombre_archivo'],

            metadata=pdf_info['metadata']

## 🚀 Instalación Rápida        )

```

### 1. Clonar el repositorio

## 🏗️ Arquitectura

```bash

git clone https://github.com/efrenbohorquez/ADRES-Scraper-v2.0.git```

cd ADRES-Scraper-v2.0adres_scraper/

```├── core/                   # Núcleo del sistema

├── mongodb/               # Gestión de base de datos  

### 2. Crear entorno virtual├── downloaders/           # Descargadores especializados

├── config/                # Configuración del sistema

```bash└── utils/                 # Utilidades auxiliares

# Windows PowerShell```

python -m venv venv

.\venv\Scripts\Activate.ps1## ⚙️ Configuración



# Linux/MacCrear archivo de configuración:

python3 -m venv venv```json

source venv/bin/activate{

```  "mongodb": {

    "connection_string": "mongodb+srv://...",

### 3. Instalar dependencias    "database_name": "adres_scraper"

  },

```bash  "scraping": {

pip install -r requirements.txt    "delay_between_requests": 2.0,

```    "max_retries": 3,

    "timeout": 30

### 4. Ejecutar el Notebook  }

}

```bash```

jupyter notebook Taller_WebScraping_ADRES.ipynb

```## 🤝 Ética y Cumplimiento



## 📦 Dependencias Principales- **Respeto al robots.txt**: Verificación automática

- **Delays apropiados**: 2+ segundos entre requests

```- **User-Agent identificado**: Transparencia total

beautifulsoup4>=4.12.0   # Parsing HTML- **Solo contenido público**: Sin acceso restringido

requests>=2.31.0          # Peticiones HTTP- **Propósito educativo**: Uso académico únicamente

lxml>=4.9.0              # Parser rápido

pymongo>=4.5.0           # MongoDB (opcional)## 📝 Licencia

jupyter>=1.0.0           # Notebooks interactivos

```MIT License - Ver [LICENSE](LICENSE) para más detalles.



## 💻 Uso Básico## 👥 Autores



### Desde Python**Taller Big Data 2025** - Desarrollo inicial



```python---

from src.web_scraper_adres import scraping_etico, analizar_contenido

**🇨🇴 Hecho con ❤️ para la comunidad de datos colombiana**
# URL objetivo
url = "https://www.adres.gov.co/"

# Realizar scraping ético
resultado = scraping_etico(url, delay=3)

if resultado["exito"]:
    # Analizar contenido
    analisis = analizar_contenido(
        resultado["contenido"],
        resultado["url_final"]
    )
    
    print(f"Caracteres extraídos: {analisis['longitud_texto']}")
    print(f"Keywords encontradas: {analisis['keywords_relevantes']}")
    print(f"PDFs detectados: {len(analisis['enlaces_pdfs'])}")
```

### Desde Jupyter Notebook

Abrir `Taller_WebScraping_ADRES.ipynb` y ejecutar todas las celdas secuencialmente.

## 🔧 Configuración Ética

El proyecto incluye configuración ética predefinida:

```python
CONFIGURACION_ETICA = {
    "delay_entre_peticiones": 3,      # 3 segundos mínimo
    "timeout": 15,                     # Timeout de 15 segundos
    "max_reintentos": 3,               # Máximo 3 reintentos
    "identificacion": "TallerBigData", # User-Agent identificado
    "respetar_robots_txt": True        # Verificar robots.txt
}
```

## 📊 Resultados del Scraping

El scraping de ADRES proporciona:

- **Texto extraído**: ~37,000+ caracteres
- **Keywords identificadas**: "salud", "afiliación", "prestadores", etc.
- **PDFs encontrados**: Guías, resoluciones, normativa
- **Metadata**: Fecha, URL, código de respuesta

## 🧪 Tests

```bash
# Ejecutar todos los tests
pytest tests/

# Con cobertura
pytest tests/ --cov=src --cov-report=html
```

## 📈 Análisis de Datos

Los datos extraídos se pueden analizar con:

- **Pandas**: Análisis estructurado
- **WordCloud**: Nube de palabras
- **Matplotlib/Seaborn**: Visualizaciones
- **NLTK**: Procesamiento de lenguaje natural

## 🔐 MongoDB Atlas (Opcional)

Para almacenar los resultados en MongoDB:

1. Crear cuenta en [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Configurar `config/config_mongodb_atlas.json`
3. Ejecutar las funciones de conexión en el notebook

## 📚 Recursos Adicionales

- **ADRES**: https://www.adres.gov.co/
- **Normograma ADRES**: https://normograma.adres.gov.co/
- **BeautifulSoup Docs**: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
- **Ethical Web Scraping**: https://towardsdatascience.com/ethics-in-web-scraping-b96b18136f01

## 📝 Principios Éticos Aplicados

1. **Respeto a robots.txt**: Verificación previa obligatoria
2. **Identificación clara**: User-Agent con propósito educativo
3. **Rate limiting**: Delays configurados entre peticiones
4. **Uso responsable**: Solo extracción de información pública
5. **No sobrecarga**: Límites de peticiones y timeouts
6. **Transparencia**: Código abierto y documentado

## 🤝 Contribuciones

Este es un proyecto educativo. Para sugerencias:

1. Fork el repositorio
2. Crea una rama (`git checkout -b feature/mejora`)
3. Commit cambios (`git commit -m 'Agregar mejora'`)
4. Push a la rama (`git push origin feature/mejora`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo [LICENSE](LICENSE) para más detalles.

## ⚠️ Disclaimer

Este proyecto es **únicamente para fines educativos**. El web scraping debe realizarse de manera ética y respetando:

- Términos de servicio del sitio web
- Leyes de propiedad intelectual
- Políticas de privacidad de datos
- Normativa legal aplicable

**No utilizar para fines comerciales sin autorización.**

## 📧 Contacto

**Efren Bohorquez Vargas**
- 🎓 Universidad Central de Colombia
- 📧 Email: [Tu correo institucional]
- 💼 LinkedIn: [Tu perfil]
- 🐙 GitHub: [@efrenbohorquez](https://github.com/efrenbohorquez)

---

**Desarrollado con ❤️ para el Taller de Big Data**

*Universidad Central de Colombia - 2024-2025*
