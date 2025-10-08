# Guía de Instalación - ADRES Scraper v2.0

## Requisitos del Sistema

### Software Requerido
- **Python 3.8+**: [Descargar Python](https://www.python.org/downloads/)
- **Git**: [Descargar Git](https://git-scm.com/downloads)
- **MongoDB Atlas**: [Crear cuenta gratuita](https://www.mongodb.com/cloud/atlas)

### Verificar Instalación
```bash
python --version  # Debe mostrar Python 3.8 o superior
git --version    # Verificar Git instalado
```

## Instalación Paso a Paso

### 1. Clonar el Repositorio
```bash
git clone https://github.com/tu-usuario/adres-scraper.git
cd adres-scraper
```

### 2. Crear Entorno Virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar MongoDB Atlas

#### Crear Cluster
1. Registrarse en [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Crear un cluster gratuito (M0)
3. Configurar usuario de base de datos
4. Obtener string de conexión

#### Configurar Acceso de Red
1. En Atlas, ir a Network Access
2. Agregar IP Address: `0.0.0.0/0` (para desarrollo)
3. Confirmar cambios

### 5. Configurar Proyecto
```bash
# Copiar template de configuración
cp config/config_template.json config/config_mongodb_atlas.json

# Editar con tus credenciales
notepad config/config_mongodb_atlas.json  # Windows
nano config/config_mongodb_atlas.json     # Linux
```

#### Configuración Mínima
```json
{
  "mongodb": {
    "connection_string": "mongodb+srv://usuario:password@cluster.mongodb.net/",
    "database_name": "adres_scraper"
  },
  "scraping": {
    "delay_between_requests": 2.0,
    "user_agent": "ADRES-Scraper/2.0"
  }
}
```

## Verificación de Instalación

### Probar Configuración
```bash
python ejemplo_uso_optimizado.py --help
```

### Test de Conexión MongoDB
```bash
python -c "from adres_scraper import MongoDBManager, Config; config = Config.from_file('config/config_mongodb_atlas.json'); db = MongoDBManager(config); print('✅ Conexión exitosa' if db.connect() else '❌ Error de conexión')"
```

### Ejecutar Ejemplo Completo
```bash
python ejemplo_uso_optimizado.py
```

## Solución de Problemas

### Error: ModuleNotFoundError
```bash
# Verificar que el entorno virtual esté activado
pip list | grep requests

# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

### Error de Conexión MongoDB
1. Verificar string de conexión en config
2. Confirmar acceso de red en Atlas
3. Validar credenciales de usuario

### Error de Permisos
```bash
# Windows: ejecutar como administrador
# Linux: verificar permisos del directorio
chmod +w config/
```

### Problemas de Red/Firewall
- Verificar conexión a Internet
- Configurar proxy si es necesario
- Comprobar puertos 443 y 27017

## Configuración Avanzada

### Variables de Entorno (Opcional)
```bash
# Windows
set MONGODB_CONNECTION_STRING=mongodb+srv://...
set ADRES_SCRAPER_LOG_LEVEL=INFO

# Linux/Mac
export MONGODB_CONNECTION_STRING="mongodb+srv://..."
export ADRES_SCRAPER_LOG_LEVEL="INFO"
```

### Configuración de Proxy
```json
{
  "network": {
    "proxy": {
      "http": "http://proxy:8080",
      "https": "https://proxy:8080"
    }
  }
}
```

## Siguiente Paso

Una vez completada la instalación:
1. Lee la [documentación principal](README.md)
2. Revisa los [principios éticos](docs/principios_eticos.md)
3. Ejecuta el ejemplo básico
4. Explora las funcionalidades avanzadas