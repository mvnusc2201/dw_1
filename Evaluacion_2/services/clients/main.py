from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from bson import ObjectId


app = FastAPI(
    title="Clients Service",
    description="Microservicio privado de clientes para Doggy's"
)


client = MongoClient("mongodb://localhost:27017/")

db = client["UNAB"]
clientes_collection = db["clientes"]


def serialize_cliente(cliente):
    return {
        "id": str(cliente["_id"]),
        "nombre": cliente.get("nombre"),
        "email": cliente.get("email"),
        "telefono": cliente.get("telefono"),
        "direccion": cliente.get("direccion")
    }


@app.get("/health")
def health():
    return {
        "status": "OK",
        "service": "clients"
    }


@app.get("/clientes")
def obtener_clientes():

    clientes = []

    for cliente in clientes_collection.find():
        clientes.append(
            serialize_cliente(cliente)
        )

    return clientes


@app.get("/clientes/{cliente_id}")
def obtener_cliente(cliente_id: str):

    if not ObjectId.is_valid(cliente_id):
        raise HTTPException(
            status_code=400,
            detail="ID de cliente invalido"
        )

    cliente = clientes_collection.find_one(
        {
            "_id": ObjectId(cliente_id)
        }
    )

    if not cliente:
        raise HTTPException(
            status_code=404,
            detail="Cliente no encontrado"
        )

    return serialize_cliente(cliente)


@app.post("/clientes")
def crear_cliente(cliente: dict):

    nuevo_cliente = {
        "nombre": cliente.get("nombre"),
        "email": cliente.get("email"),
        "telefono": cliente.get("telefono"),
        "direccion": cliente.get("direccion")
    }

    resultado = clientes_collection.insert_one(
        nuevo_cliente
    )

    cliente_creado = clientes_collection.find_one(
        {
            "_id": resultado.inserted_id
        }
    )

    return serialize_cliente(
        cliente_creado
    )


@app.put("/clientes/{cliente_id}")
def actualizar_cliente(
    cliente_id: str,
    cliente: dict
):

    if not ObjectId.is_valid(cliente_id):
        raise HTTPException(
            status_code=400,
            detail="ID de cliente invalido"
        )

    resultado = clientes_collection.update_one(
        {
            "_id": ObjectId(cliente_id)
        },
        {
            "$set": cliente
        }
    )

    if resultado.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Cliente no encontrado"
        )

    cliente_actualizado = clientes_collection.find_one(
        {
            "_id": ObjectId(cliente_id)
        }
    )

    return serialize_cliente(
        cliente_actualizado
    )


@app.delete("/clientes/{cliente_id}")
def eliminar_cliente(cliente_id: str):

    if not ObjectId.is_valid(cliente_id):
        raise HTTPException(
            status_code=400,
            detail="ID de cliente invalido"
        )

    resultado = clientes_collection.delete_one(
        {
            "_id": ObjectId(cliente_id)
        }
    )

    if resultado.deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Cliente no encontrado"
        )

    return {
        "message": "Cliente eliminado correctamente"
    }