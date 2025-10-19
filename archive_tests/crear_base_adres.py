#!/usr/bin/env python3
"""
🚀 CREADOR DE BASE DE DATOS ADRES EN MONGODB ATLAS
Script para crear la base de datos 'taller_bigdata_adres' y poblarla con documentos
"""

from pymongo import MongoClient
from datetime import datetime
import ssl

# Tu configuración específica de Atlas
ATLAS_CONNECTION = "mongodb+srv://efrenbohorquezv_db_user:Central2025@cluster0.ljpppvo.mongodb.net/"
DATABASE_NAME = "taller_bigdata_adres"
COLLECTION_NAME = "documentos_adres"

def crear_conexion_atlas():
    """Crear conexión robusta a MongoDB Atlas"""
    print("🔧 CONECTANDO A MONGODB ATLAS")
    print("=" * 50)
    
    try:
        # Configurar cliente con múltiples opciones de conectividad
        client = MongoClient(
            ATLAS_CONNECTION,
            tls=True,
            tlsAllowInvalidCertificates=True,
            serverSelectionTimeoutMS=15000,   # 15 segundos
            connectTimeoutMS=15000,
            socketTimeoutMS=15000,
            maxPoolSize=10,
            retryWrites=True,
            w='majority'
        )
        
        # Probar conexión con ping
        print("📡 Probando conexión...")
        client.admin.command('ping')
        print("✅ Conexión EXITOSA a MongoDB Atlas")
        
        return client
        
    except Exception as e:
        print(f"❌ Error de conexión: {str(e)[:200]}...")
        
        # Intentar conexión alternativa sin SSL estricto
        try:
            print("🔄 Intentando conexión alternativa...")
            client = MongoClient(
                ATLAS_CONNECTION,
                ssl=True,
                ssl_cert_reqs=ssl.CERT_NONE,
                serverSelectionTimeoutMS=30000,
                connectTimeoutMS=30000
            )
            client.admin.command('ping')
            print("✅ Conexión alternativa EXITOSA")
            return client
        except Exception as e2:
            print(f"❌ Error en conexión alternativa: {str(e2)[:200]}...")
            return None

def crear_base_datos_adres(client):
    """Crear la base de datos y colección para ADRES"""
    print(f"\n📊 CREANDO BASE DE DATOS: {DATABASE_NAME}")
    print("=" * 50)
    
    try:
        # Obtener la base de datos (se crea automáticamente al insertar)
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        
        print(f"✅ Base de datos '{DATABASE_NAME}' lista")
        print(f"📁 Colección '{COLLECTION_NAME}' lista")
        
        return db, collection
        
    except Exception as e:
        print(f"❌ Error creando base de datos: {e}")
        return None, None

def crear_documentos_demo(collection):
    """Crear documentos de demostración para ADRES"""
    print(f"\n📄 CREANDO DOCUMENTOS DEMO")
    print("=" * 50)
    
    documentos_demo = [
        {
            "url_original": "https://normograma.adres.gov.co/demo/concepto_2024_001",
            "titulo": "Concepto ADRES 2024-001 - Régimen Subsidiado",
            "texto_completo": """
CONCEPTO TÉCNICO ADRES 2024-001

ASUNTO: Consulta sobre aplicación del régimen subsidiado en salud

CONSIDERACIONES:

El régimen subsidiado en salud tiene como finalidad garantizar el acceso 
a los servicios de salud a la población más vulnerable del país, mediante 
el aseguramiento y la prestación de servicios incluidos en el Plan 
Obligatorio de Salud Subsidiado - POSS.

CONCEPTO:

Por lo anterior, este Administrador conceptúa que es procedente la 
autorización solicitada, siempre y cuando se cumplan los requisitos 
establecidos en la Resolución 3047 de 2008 y demás normatividad aplicable.

FUNDAMENTOS JURÍDICOS:
- Ley 100 de 1993
- Decreto 780 de 2016
- Resolución 3047 de 2008
            """,
            "fecha_extraccion": datetime.now(),
            "longitud_caracteres": 756,
            "longitud_palabras": 108,
            "tipo_documento": "concepto_adres",
            "estado_procesamiento": "demo_creado",
            "metadatos_http": {
                "status_code": 200,
                "content_type": "text/html",
                "encoding": "utf-8"
            },
            "palabras_clave": ["régimen subsidiado", "POSS", "Ley 100", "Resolución 3047"],
            "terminos_juridicos": ["régimen subsidiado", "aseguramiento", "normatividad aplicable"],
            "es_documento_demo": True,
            "origen": "taller_bigdata_educativo"
        },
        {
            "url_original": "https://normograma.adres.gov.co/demo/concepto_2024_002",
            "titulo": "Concepto ADRES 2024-002 - Recursos de Inversión",
            "texto_completo": """
CONCEPTO TÉCNICO ADRES 2024-002

ASUNTO: Consulta sobre manejo de recursos de inversión en salud

ANTECEDENTES:

La entidad consultante solicita concepto sobre la correcta aplicación 
de los recursos destinados a la inversión en infraestructura de salud 
de primer nivel de atención.

ANÁLISIS:

Los recursos del Sistema General de Participaciones destinados a salud 
deben orientarse prioritariamente al aseguramiento de la población pobre 
no cubierta con subsidios a la demanda y a la prestación de servicios 
de salud a la población pobre en lo no cubierto con subsidios a la demanda.

CONCEPTO:

Se conceptúa que los recursos pueden utilizarse para la finalidad 
consultada, siempre que se cumplan las condiciones establecidas en 
el artículo 44 de la Ley 715 de 2001.

MARCO NORMATIVO:
- Ley 715 de 2001
- Decreto 028 de 2008
- Circular Externa 047 de 2015
            """,
            "fecha_extraccion": datetime.now(),
            "longitud_caracteres": 1024,
            "longitud_palabras": 142,
            "tipo_documento": "concepto_adres",
            "estado_procesamiento": "demo_creado", 
            "metadatos_http": {
                "status_code": 200,
                "content_type": "text/html",
                "encoding": "utf-8"
            },
            "palabras_clave": ["SGP", "inversión", "infraestructura", "primer nivel"],
            "terminos_juridicos": ["Sistema General de Participaciones", "subsidios a la demanda", "Ley 715"],
            "es_documento_demo": True,
            "origen": "taller_bigdata_educativo"
        },
        {
            "url_original": "https://normograma.adres.gov.co/demo/concepto_2024_003",
            "titulo": "Concepto ADRES 2024-003 - Afiliación al Régimen Subsidiado",
            "texto_completo": """
CONCEPTO TÉCNICO ADRES 2024-003

ASUNTO: Procedimientos para afiliación al régimen subsidiado

CONSULTA:

Se solicita concepto sobre los procedimientos y requisitos para la 
afiliación de población vulnerable al régimen subsidiado en salud.

MARCO LEGAL:

El artículo 157 de la Ley 100 de 1993 establece que tienen derecho 
al régimen subsidiado las personas que carezcan de capacidad de pago 
para afiliarse al régimen contributivo.

DESARROLLO:

La afiliación al régimen subsidiado se realizará mediante la aplicación 
de la encuesta del SISBEN, la cual permitirá identificar a la población 
objetivo del régimen subsidiado en salud.

CONCLUSIÓN:

Por lo expuesto, se conceptúa que los procedimientos consultados se 
ajustan a la normatividad vigente, especialmente lo dispuesto en el 
Decreto 1011 de 2006 y sus modificaciones.

NORMATIVIDAD CITADA:
- Ley 100 de 1993, art. 157
- Decreto 1011 de 2006
- Resolución 412 de 2000
            """,
            "fecha_extraccion": datetime.now(),
            "longitud_caracteres": 1156,
            "longitud_palabras": 163,
            "tipo_documento": "concepto_adres",
            "estado_procesamiento": "demo_creado",
            "metadatos_http": {
                "status_code": 200,
                "content_type": "text/html", 
                "encoding": "utf-8"
            },
            "palabras_clave": ["afiliación", "SISBEN", "población vulnerable", "capacidad de pago"],
            "terminos_juridicos": ["régimen subsidiado", "régimen contributivo", "normatividad vigente"],
            "es_documento_demo": True,
            "origen": "taller_bigdata_educativo"
        }
    ]
    
    try:
        # Insertar documentos
        resultado = collection.insert_many(documentos_demo)
        print(f"✅ {len(resultado.inserted_ids)} documentos insertados exitosamente")
        
        # Mostrar IDs insertados
        print(f"📋 IDs de documentos creados:")
        for i, doc_id in enumerate(resultado.inserted_ids, 1):
            print(f"   {i}. {doc_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error insertando documentos: {e}")
        return False

def crear_indices(collection):
    """Crear índices para optimizar búsquedas"""
    print(f"\n🔍 CREANDO ÍNDICES PARA BÚSQUEDAS")
    print("=" * 50)
    
    try:
        # Índice único por URL
        collection.create_index("url_original", unique=True)
        print("✅ Índice único creado para 'url_original'")
        
        # Índice por fecha
        collection.create_index("fecha_extraccion")
        print("✅ Índice creado para 'fecha_extraccion'")
        
        # Índice por tipo de documento
        collection.create_index("tipo_documento")
        print("✅ Índice creado para 'tipo_documento'")
        
        # Índice de texto completo para búsquedas
        collection.create_index([("titulo", "text"), ("texto_completo", "text")])
        print("✅ Índice de texto completo creado")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creando índices: {e}")
        return False

def verificar_base_datos(db, collection):
    """Verificar que la base de datos se creó correctamente"""
    print(f"\n🔍 VERIFICANDO BASE DE DATOS CREADA")
    print("=" * 50)
    
    try:
        # Listar colecciones en la base de datos
        colecciones = db.list_collection_names()
        print(f"📁 Colecciones en '{DATABASE_NAME}':")
        for col in colecciones:
            print(f"   • {col}")
        
        # Contar documentos
        total_docs = collection.count_documents({})
        print(f"\n📊 Total de documentos en '{COLLECTION_NAME}': {total_docs}")
        
        # Mostrar documentos de ejemplo
        if total_docs > 0:
            print(f"\n📄 DOCUMENTOS ALMACENADOS:")
            for i, doc in enumerate(collection.find().limit(3), 1):
                print(f"\n   {i}. 📋 {doc.get('titulo', 'Sin título')}")
                print(f"      🔗 {doc.get('url_original', 'Sin URL')}")
                print(f"      📊 {doc.get('longitud_caracteres', 0)} caracteres")
                print(f"      📅 {doc.get('fecha_extraccion', 'Sin fecha')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando: {e}")
        return False

def mostrar_instrucciones_atlas():
    """Mostrar cómo verificar en Atlas Web"""
    print(f"\n🌐 CÓMO VERIFICAR EN MONGODB ATLAS WEB")
    print("=" * 60)
    print("1. 🌐 Ve a: https://cloud.mongodb.com/")
    print("2. 🔐 Inicia sesión con tu cuenta")
    print("3. 📊 Haz clic en 'Browse Collections'")
    print(f"4. 📁 Busca la base de datos: '{DATABASE_NAME}'")
    print(f"5. 📑 Abre la colección: '{COLLECTION_NAME}'")
    print("6. 🎉 ¡Deberías ver tus 3 documentos demo!")
    print(f"\n🔍 FILTRO ÚTIL:")
    print('   {"es_documento_demo": true}')

def main():
    """Función principal"""
    print("🎓 CREADOR DE BASE DE DATOS TALLER ADRES")
    print("🛡️ MONGODB ATLAS - DOCUMENTOS NORMATIVOS")
    print("=" * 70)
    
    # Conectar a Atlas
    client = crear_conexion_atlas()
    if not client:
        print("\n❌ No se pudo conectar. Verifica:")
        print("   • Tu IP está en Network Access whitelist")
        print("   • Credenciales son correctas")
        print("   • Cluster está activo")
        return False
    
    try:
        # Crear base de datos y colección
        db, collection = crear_base_datos_adres(client)
        if not db or not collection:
            return False
        
        # Crear documentos demo
        if not crear_documentos_demo(collection):
            return False
        
        # Crear índices
        crear_indices(collection)
        
        # Verificar resultado
        verificar_base_datos(db, collection)
        
        print(f"\n🎉 ¡BASE DE DATOS '{DATABASE_NAME}' CREADA EXITOSAMENTE!")
        mostrar_instrucciones_atlas()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error en proceso principal: {e}")
        return False
        
    finally:
        client.close()
        print(f"\n🔌 Conexión cerrada")

if __name__ == "__main__":
    exito = main()
    if exito:
        print(f"\n✅ PROCESO COMPLETADO - Actualiza tu Atlas y verifica")
    else:
        print(f"\n❌ PROCESO FALLÓ - Revisa errores arriba")