#!/usr/bin/env python3
"""
🔍 DIAGNÓSTICO COMPLETO MONGODB ATLAS
Análisis exhaustivo de problemas de conectividad
"""

import ssl
import socket
import dns.resolver
from urllib.parse import urlparse, quote_plus
import time
from datetime import datetime

# Configuraciones a probar
CONFIGURACIONES = [
    {
        "nombre": "Config Original",
        "usuario": "efrenbohorquezv_db_user",
        "password": "Central2025*",
        "host": "cluster0.ljpppvo.mongodb.net",
        "db": "taller_bigdata_adres"
    }
]

def diagnostico_dns():
    """Probar resolución DNS"""
    print("🔍 DIAGNÓSTICO DNS")
    print("=" * 40)
    
    host = "cluster0.ljpppvo.mongodb.net"
    
    try:
        # Resolver SRV records
        srv_records = dns.resolver.resolve(f"_mongodb._tcp.{host}", 'SRV')
        print("✅ Registros SRV encontrados:")
        for srv in srv_records:
            print(f"   📋 {srv.target}:{srv.port} (prioridad: {srv.priority})")
        
        # Resolver TXT records
        try:
            txt_records = dns.resolver.resolve(host, 'TXT')
            print("✅ Registros TXT:")
            for txt in txt_records:
                print(f"   📋 {txt}")
        except:
            print("⚠️  Sin registros TXT")
        
        return True
        
    except Exception as e:
        print(f"❌ Error DNS: {e}")
        return False

def diagnostico_ssl():
    """Probar conectividad SSL"""
    print("\n🔒 DIAGNÓSTICO SSL")
    print("=" * 40)
    
    # Servidores a probar (de los SRV records)
    servidores = [
        ("ac-xvxmroc-shard-00-00.ljpppvo.mongodb.net", 27017),
        ("ac-xvxmroc-shard-00-01.ljpppvo.mongodb.net", 27017),
        ("ac-xvxmroc-shard-00-02.ljpppvo.mongodb.net", 27017)
    ]
    
    for host, puerto in servidores:
        print(f"\n🔌 Probando {host}:{puerto}")
        
        try:
            # Crear socket TCP
            sock = socket.create_connection((host, puerto), timeout=10)
            print("  ✅ Conexión TCP exitosa")
            
            # Intentar handshake SSL
            context = ssl.create_default_context()
            # Intentar sin verificación de certificado
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            ssl_sock = context.wrap_socket(sock, server_hostname=host)
            print(f"  ✅ Handshake SSL exitoso")
            print(f"  📋 Versión SSL: {ssl_sock.version()}")
            print(f"  🔒 Cipher: {ssl_sock.cipher()}")
            
            ssl_sock.close()
            
        except socket.timeout:
            print(f"  ❌ Timeout de conexión")
        except ssl.SSLError as e:
            print(f"  ❌ Error SSL: {e}")
        except Exception as e:
            print(f"  ❌ Error: {e}")

def diagnostico_pymongo():
    """Probar diferentes configuraciones PyMongo"""
    print("\n🐍 DIAGNÓSTICO PYMONGO")
    print("=" * 40)
    
    import pymongo
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure, ConfigurationError
    
    print(f"📦 Versión PyMongo: {pymongo.version}")
    
    for config in CONFIGURACIONES:
        print(f"\n🧪 Probando: {config['nombre']}")
        
        # Lista de configuraciones SSL a probar
        ssl_configs = [
            {
                "nombre": "SSL por defecto",
                "params": {}
            },
            {
                "nombre": "SSL deshabilitado",
                "params": {"ssl": False, "tls": False}
            },
            {
                "nombre": "TLS sin verificación",
                "params": {
                    "tls": True,
                    "tlsInsecure": True,
                    "tlsAllowInvalidCertificates": True,
                    "tlsAllowInvalidHostnames": True
                }
            },
            {
                "nombre": "Sin SRV",
                "params": {"directConnection": True}
            }
        ]
        
        for ssl_config in ssl_configs:
            print(f"\n  🔧 {ssl_config['nombre']}")
            
            try:
                # Construir URI de conexión
                usuario = quote_plus(config['usuario'])
                password = quote_plus(config['password'])
                
                if ssl_config['nombre'] == "Sin SRV":
                    # Usar conexión directa a un nodo
                    uri = f"mongodb://{usuario}:{password}@ac-xvxmroc-shard-00-00.ljpppvo.mongodb.net:27017/{config['db']}"
                else:
                    uri = f"mongodb+srv://{usuario}:{password}@{config['host']}/{config['db']}"
                
                # Parámetros adicionales
                params = {
                    "serverSelectionTimeoutMS": 5000,
                    "connectTimeoutMS": 5000,
                    **ssl_config['params']
                }
                
                # Intentar conexión
                client = MongoClient(uri, **params)
                
                # Test rápido
                start_time = time.time()
                result = client.admin.command('ping')
                end_time = time.time()
                
                print(f"    ✅ ÉXITO en {(end_time - start_time)*1000:.0f}ms")
                print(f"    📊 Ping result: {result}")
                
                # Probar base de datos
                db = client[config['db']]
                collections = db.list_collection_names()
                print(f"    📁 Colecciones: {collections}")
                
                client.close()
                return True
                
            except ConnectionFailure as e:
                print(f"    ❌ Fallo de conexión: {str(e)[:100]}...")
            except ConfigurationError as e:
                print(f"    ❌ Error de configuración: {str(e)[:100]}...")
            except Exception as e:
                print(f"    ❌ Error: {str(e)[:100]}...")
    
    return False

def diagnostico_red():
    """Diagnosticar problemas de red"""
    print("\n🌐 DIAGNÓSTICO DE RED")
    print("=" * 40)
    
    # Verificar conectividad general
    hosts_test = [
        ("google.com", 443, "Google HTTPS"),
        ("mongodb.com", 443, "MongoDB sitio web"),
        ("cluster0.ljpppvo.mongodb.net", 27017, "Cluster MongoDB")
    ]
    
    for host, puerto, desc in hosts_test:
        print(f"\n🔌 {desc} ({host}:{puerto})")
        try:
            sock = socket.create_connection((host, puerto), timeout=5)
            print("  ✅ Conectado")
            sock.close()
        except Exception as e:
            print(f"  ❌ Error: {e}")

def mostrar_recomendaciones():
    """Mostrar recomendaciones para resolver problemas"""
    print("\n💡 RECOMENDACIONES PARA RESOLVER PROBLEMAS")
    print("=" * 60)
    
    print("🔧 SI HAY ERRORES SSL:")
    print("   1. Verificar que el cluster esté activo en Atlas")
    print("   2. Revisar la whitelist de IPs en Atlas")
    print("   3. Verificar credenciales de usuario")
    print("   4. Comprobar firewall corporativo")
    print("   5. Intentar desde otra red (móvil, VPN)")
    
    print("\n🌐 SI HAY ERRORES DNS:")
    print("   1. Cambiar servidores DNS (8.8.8.8, 1.1.1.1)")
    print("   2. Limpiar cache DNS: ipconfig /flushdns")
    print("   3. Intentar conexión directa sin SRV")
    
    print("\n🔐 SI HAY ERRORES DE AUTENTICACIÓN:")
    print("   1. Verificar usuario y contraseña en Atlas")
    print("   2. Verificar permisos del usuario")
    print("   3. Recrear usuario si es necesario")
    
    print("\n🏢 CONFIGURACIÓN ATLAS REQUERIDA:")
    print("   1. 🌐 Network Access → Add IP Address → 0.0.0.0/0 (todas las IPs)")
    print("   2. 👤 Database Access → Verificar usuario 'efrenbohorquezv_db_user'")
    print("   3. 🔐 Verificar contraseña: 'Central2025*'")
    print("   4. 📊 Verificar permisos: readWrite en taller_bigdata_adres")

def main():
    """Función principal de diagnóstico"""
    print("🏥 DIAGNÓSTICO COMPLETO MONGODB ATLAS")
    print("🕐 Iniciado:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 70)
    
    # Ejecutar diagnósticos
    dns_ok = diagnostico_dns()
    diagnostico_ssl()
    diagnostico_red()
    
    # Probar PyMongo solo si DNS está bien
    if dns_ok:
        pymongo_ok = diagnostico_pymongo()
        
        if pymongo_ok:
            print("\n🎉 ¡CONEXIÓN EXITOSA ENCONTRADA!")
            return
    
    print("\n❌ NO SE PUDO ESTABLECER CONEXIÓN")
    mostrar_recomendaciones()

if __name__ == "__main__":
    main()