# 🚀 Guía de Inicio Rápido - Taller Big Data

## ⚡ Instalación Rápida (5 minutos)

### Windows (PowerShell)
```powershell
# Clonar o descargar el proyecto
cd C:\
git clone https://github.com/tu-usuario/web_scraping_adres_taller

# Navegar al directorio
cd web_scraping_adres_taller

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### Linux/macOS (Bash)
```bash
# Clonar el proyecto
cd ~/
git clone https://github.com/tu-usuario/web_scraping_adres_taller

# Navegar al directorio
cd web_scraping_adres_taller

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

## 🎯 Ejecución Inmediata

### Opción 1: Demo Completa (Recomendado)
```bash
python demo_completa.py
```

### Opción 2: Scripts Individuales
```bash
# 1. Validar principios éticos
python src/validador_etico.py

# 2. Ejecutar web scraping
python src/web_scraper_adres.py

# 3. Analizar contenido extraído
python src/analizador_contenido.py
```

## 📊 Resultados Esperados

Después de la ejecución exitosa encontrarás:

```
web_scraping_adres_output/
├── concepto_adres_20241005_153045.json    # Datos extraídos
├── analisis_20241005_153120.json          # Análisis detallado
├── analisis_20241005_153120_resumen.md    # Resumen legible
└── validacion_etica_20241005_153001.json  # Reporte ético
```

## 🆘 Solución de Problemas Rápida

### Error: "No module named 'requests'"
```bash
pip install requests beautifulsoup4 lxml
```

### Error: "Connection refused" o timeout
- ✅ Verificar conexión a internet
- ✅ Intentar más tarde (el servidor puede estar ocupado)
- ✅ Aumentar timeout en configuración

### Error: "Permission denied"
- ✅ Ejecutar como administrador (Windows) o con sudo (Linux)
- ✅ Verificar permisos del directorio

## 🎓 Para Instructores del Taller

### Preparación Pre-Taller (10 minutos)
1. **Verificar instalación**: `python demo_completa.py`
2. **Testear conectividad**: El script debe completar los 3 pasos
3. **Preparar ejemplos**: Los resultados se guardan automáticamente

### Durante el Taller
- **Mostrar código en vivo**: Usar VS Code o tu editor favorito
- **Ejecutar paso a paso**: Usar scripts individuales para explicar conceptos
- **Discutir resultados**: Abrir archivos JSON/MD generados

### Puntos de Discusión Clave
1. **Principios éticos**: ¿Por qué el delay de 0.5 segundos?
2. **Manejo de errores**: ¿Qué pasa si el servidor no responde?
3. **Análisis de datos**: ¿Qué insights podemos extraer?
4. **Aplicaciones reales**: ¿Dónde más podríamos aplicar esto?

## 📚 Recursos Adicionales de 1 Minuto

### Modificar la URL objetivo
```python
# En src/web_scraper_adres.py, línea 38
URL_OBJETIVO = "https://tu-nueva-url.com"
```

### Cambiar configuración ética
```python
# En src/web_scraper_adres.py, línea 53
DELAY_SECONDS = 1.0  # Aumentar delay
REQUEST_TIMEOUT = 15  # Aumentar timeout
```

### Ejecutar tests
```bash
pip install pytest
python -m pytest tests/ -v
```

## 🏆 Objetivos de Aprendizaje (Checklist)

Al completar este taller, los estudiantes deberán:

- [ ] **Entender web scraping ético** vs agresivo
- [ ] **Implementar delays y timeouts** apropiados  
- [ ] **Manejar errores HTTP** gracefully
- [ ] **Extraer y limpiar datos** de HTML
- [ ] **Analizar texto** con métricas básicas
- [ ] **Generar reportes** estructurados
- [ ] **Validar principios éticos** automáticamente

## 💡 Extensiones Rápidas (15-30 min cada una)

### Extensión 1: Múltiples URLs
```python
urls = [
    "https://normograma.adres.gov.co/doc1.html",
    "https://normograma.adres.gov.co/doc2.html"
]
for url in urls:
    scraper.procesar_documento(url)
```

### Extensión 2: Análisis Avanzado
```bash
pip install nltk matplotlib wordcloud
# Agregar al analizador_contenido.py
```

### Extensión 3: Base de Datos
```bash
pip install sqlite3
# Guardar resultados en DB local
```

---

## 🆘 Contacto y Soporte

- **Issues del proyecto**: [GitHub Issues]
- **Documentación completa**: Ver `README.md`
- **Principios éticos**: Ver `docs/principios_eticos.md`

**¡Listo para empezar! 🚀 Ejecuta `python demo_completa.py` ahora.**