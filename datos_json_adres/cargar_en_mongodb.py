
# SCRIPT PARA CARGAR DATOS EN MONGODB
# Ejecutar después de instalar MongoDB

from pymongo import MongoClient
import json

# Conectar a MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['taller_bigdata_adres']
collection = db['documentos_json']

# Cargar colección completa
with open('datos_json_adres/coleccion_completa_adres.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Insertar documentos
for documento in data['documentos']:
    resultado = collection.insert_one(documento)
    print(f"Insertado: {documento['titulo']}")

print(f"Total documentos en MongoDB: {collection.count_documents({})}")

# Ejemplos de consultas
print("\nEjemplos de consultas:")
print("1. Por categoría:")
for doc in collection.find({"analisis.categoria_principal": "habilitacion_servicios"}):
    print(f"  - {doc['titulo']}")

print("\n2. Por año:")
for doc in collection.find({"metadatos.año": 2013}):
    print(f"  - {doc['titulo']}")
