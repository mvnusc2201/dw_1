from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from bson import ObjectId

# Inicializar la aplicación
app = FastAPI(title="API Doggy's - FastAPI")

# Conexión a MongoDB (Usa la misma base de datos de la semana 5)
client = MongoClient("mongodb://localhost:27017/")
db = client["UNAB"] 
coleccion = db["clientes"]

@app.get("/")
def inicio():
    return {"mensaje": "Servidor FastAPI conectado a MongoDB"}

# 1. Consultar todos los registros
@app.get("/clientes")
def obtener_clientes():
    clientes = []
    for cliente in coleccion.find():
        cliente["_id"] = str(cliente["_id"]) # Convertir el ID de Mongo a texto
        clientes.append(cliente)
    return clientes

# 2. Consultar por ID
@app.get("/clientes/{cliente_id}")
def obtener_cliente_por_id(cliente_id: str):
    if not ObjectId.is_valid(cliente_id):
        raise HTTPException(status_code=400, detail="ID de MongoDB no válido")
    
    cliente = coleccion.find_one({"_id": ObjectId(cliente_id)})
    if cliente:
        cliente["_id"] = str(cliente["_id"])
        return cliente
    
    raise HTTPException(status_code=404, detail="Cliente no encontrado")

# 3. Insertar un cliente
@app.post("/clientes")
def insertar_cliente(cliente: dict):
    resultado = coleccion.insert_one(cliente)

    cliente["_id"] = str(resultado.inserted_id)

    return {
        "mensaje": "Cliente insertado correctamente",
        "cliente": cliente
    }


# 4. Actualizar un cliente por ID
@app.put("/clientes/{cliente_id}")
def actualizar_cliente(cliente_id: str, cliente: dict):
    if not ObjectId.is_valid(cliente_id):
        raise HTTPException(
            status_code=400,
            detail="ID de MongoDB no válido"
        )

    cliente.pop("_id", None)
    
    resultado = coleccion.update_one(
        {"_id": ObjectId(cliente_id)},
        {"$set": cliente}
    )

    if resultado.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Cliente no encontrado"
        )

    cliente_actualizado = coleccion.find_one(
        {"_id": ObjectId(cliente_id)}
    )

    cliente_actualizado["_id"] = str(cliente_actualizado["_id"])

    return {
        "mensaje": "Cliente actualizado correctamente",
        "cliente": cliente_actualizado
    }


# 5. Eliminar un cliente por ID
@app.delete("/clientes/{cliente_id}")
def eliminar_cliente(cliente_id: str):
    if not ObjectId.is_valid(cliente_id):
        raise HTTPException(
            status_code=400,
            detail="ID de MongoDB no válido"
        )

    resultado = coleccion.delete_one(
        {"_id": ObjectId(cliente_id)}
    )

    if resultado.deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Cliente no encontrado"
        )

    return {
        "mensaje": "Cliente eliminado correctamente"
    }
