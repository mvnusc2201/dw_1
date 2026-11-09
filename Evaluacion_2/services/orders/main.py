from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from bson import ObjectId
import httpx


app = FastAPI(
    title="Orders Service",
    description="Microservicio privado de pedidos"
)


client = MongoClient("mongodb://localhost:27017/")

db = client["UNAB"]
pedidos_collection = db["pedidos"]


INVENTORY_URL = "http://127.0.0.1:9102"


def serialize_pedido(pedido):
    return {
        "id": str(pedido["_id"]),
        "cliente_id": pedido.get("cliente_id"),
        "producto_id": pedido.get("producto_id"),
        "cantidad": pedido.get("cantidad"),
        "estado": pedido.get("estado"),
        "total": pedido.get("total")
    }


@app.get("/health")
def health():
    return {
        "status": "OK",
        "service": "orders"
    }


@app.get("/pedidos")
def obtener_pedidos():

    pedidos = []

    for pedido in pedidos_collection.find():
        pedidos.append(
            serialize_pedido(pedido)
        )

    return pedidos


@app.get("/pedidos/{pedido_id}")
def obtener_pedido(pedido_id: str):

    if not ObjectId.is_valid(pedido_id):
        raise HTTPException(
            status_code=400,
            detail="ID de pedido invalido"
        )

    pedido = pedidos_collection.find_one(
        {
            "_id": ObjectId(pedido_id)
        }
    )

    if not pedido:
        raise HTTPException(
            status_code=404,
            detail="Pedido no encontrado"
        )

    return serialize_pedido(pedido)


@app.post("/pedidos")
async def crear_pedido(pedido: dict):

    producto_id = pedido.get("producto_id")
    cantidad = pedido.get("cantidad", 1)

    if not producto_id:
        raise HTTPException(
            status_code=400,
            detail="producto_id es obligatorio"
        )

    if cantidad <= 0:
        raise HTTPException(
            status_code=400,
            detail="La cantidad debe ser mayor a 0"
        )

    try:
        async with httpx.AsyncClient() as http_client:
            response = await http_client.get(
                f"{INVENTORY_URL}/productos/{producto_id}"
            )
    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Inventory Service no disponible"
        )

    if response.status_code == 404:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado"
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail="Error consultando inventario"
        )

    producto = response.json()

    if not producto.get("disponible"):
        raise HTTPException(
            status_code=409,
            detail="Producto no disponible"
        )

    stock = producto.get("stock", 0)

    if stock < cantidad:
        raise HTTPException(
            status_code=409,
            detail="Stock insuficiente"
        )

    total = producto.get("precio", 0) * cantidad

    nuevo_pedido = {
        "cliente_id": pedido.get("cliente_id"),
        "producto_id": producto_id,
        "cantidad": cantidad,
        "estado": "pendiente",
        "total": total
    }

    resultado = pedidos_collection.insert_one(
        nuevo_pedido
    )

    pedido_creado = pedidos_collection.find_one(
        {
            "_id": resultado.inserted_id
        }
    )

    return serialize_pedido(
        pedido_creado
    )


@app.put("/pedidos/{pedido_id}/estado")
def actualizar_estado(
    pedido_id: str,
    data: dict
):

    if not ObjectId.is_valid(pedido_id):
        raise HTTPException(
            status_code=400,
            detail="ID de pedido invalido"
        )

    nuevo_estado = data.get("estado")

    estados_validos = [
        "pendiente",
        "pagado",
        "preparando",
        "enviado",
        "entregado",
        "cancelado"
    ]

    if nuevo_estado not in estados_validos:
        raise HTTPException(
            status_code=400,
            detail="Estado invalido"
        )

    resultado = pedidos_collection.update_one(
        {
            "_id": ObjectId(pedido_id)
        },
        {
            "$set": {
                "estado": nuevo_estado
            }
        }
    )

    if resultado.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Pedido no encontrado"
        )

    pedido_actualizado = pedidos_collection.find_one(
        {
            "_id": ObjectId(pedido_id)
        }
    )

    return serialize_pedido(
        pedido_actualizado
    )