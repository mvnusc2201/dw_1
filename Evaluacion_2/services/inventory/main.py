from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from bson import ObjectId


app = FastAPI(
    title="Inventory Service",
    description="Microservicio privado de inventario y catalogo"
)


client = MongoClient("mongodb://localhost:27017/")

db = client["UNAB"]
productos_collection = db["productos"]


def serialize_producto(producto):
    return {
        "id": str(producto["_id"]),
        "nombre": producto.get("nombre"),
        "descripcion": producto.get("descripcion"),
        "precio": producto.get("precio"),
        "stock": producto.get("stock"),
        "disponible": producto.get("disponible")
    }


@app.get("/health")
def health():
    return {
        "status": "OK",
        "service": "inventory"
    }


@app.get("/productos")
def obtener_productos():

    productos = []

    for producto in productos_collection.find():
        productos.append(
            serialize_producto(producto)
        )

    return productos


@app.get("/productos/{producto_id}")
def obtener_producto(producto_id: str):

    if not ObjectId.is_valid(producto_id):
        raise HTTPException(
            status_code=400,
            detail="ID de producto invalido"
        )

    producto = productos_collection.find_one(
        {
            "_id": ObjectId(producto_id)
        }
    )

    if not producto:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado"
        )

    return serialize_producto(producto)


@app.post("/productos")
def crear_producto(producto: dict):

    nuevo_producto = {
        "nombre": producto.get("nombre"),
        "descripcion": producto.get("descripcion"),
        "precio": producto.get("precio"),
        "stock": producto.get("stock", 0),
        "disponible": producto.get("disponible", True)
    }

    resultado = productos_collection.insert_one(
        nuevo_producto
    )

    producto_creado = productos_collection.find_one(
        {
            "_id": resultado.inserted_id
        }
    )

    return serialize_producto(
        producto_creado
    )


@app.put("/productos/{producto_id}")
def actualizar_producto(
    producto_id: str,
    producto: dict
):

    if not ObjectId.is_valid(producto_id):
        raise HTTPException(
            status_code=400,
            detail="ID de producto invalido"
        )

    resultado = productos_collection.update_one(
        {
            "_id": ObjectId(producto_id)
        },
        {
            "$set": producto
        }
    )

    if resultado.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado"
        )

    producto_actualizado = productos_collection.find_one(
        {
            "_id": ObjectId(producto_id)
        }
    )

    return serialize_producto(
        producto_actualizado
    )


@app.delete("/productos/{producto_id}")
def eliminar_producto(producto_id: str):

    if not ObjectId.is_valid(producto_id):
        raise HTTPException(
            status_code=400,
            detail="ID de producto invalido"
        )

    resultado = productos_collection.delete_one(
        {
            "_id": ObjectId(producto_id)
        }
    )

    if resultado.deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado"
        )

    return {
        "message": "Producto eliminado correctamente"
    }