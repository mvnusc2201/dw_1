from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from bson import ObjectId
import httpx


app = FastAPI(
    title="Payments Service",
    description="Microservicio privado de pagos"
)


client = MongoClient("mongodb://localhost:27017/")

db = client["UNAB"]
pagos_collection = db["pagos"]


ORDERS_URL = "http://127.0.0.1:9103"


def serialize_pago(pago):
    return {
        "id": str(pago["_id"]),
        "pedido_id": pago.get("pedido_id"),
        "monto": pago.get("monto"),
        "estado": pago.get("estado"),
        "proveedor": pago.get("proveedor")
    }


@app.get("/health")
def health():
    return {
        "status": "OK",
        "service": "payments"
    }


@app.get("/pagos")
def obtener_pagos():

    pagos = []

    for pago in pagos_collection.find():
        pagos.append(
            serialize_pago(pago)
        )

    return pagos


@app.get("/pagos/{pago_id}")
def obtener_pago(pago_id: str):

    if not ObjectId.is_valid(pago_id):
        raise HTTPException(
            status_code=400,
            detail="ID de pago invalido"
        )

    pago = pagos_collection.find_one(
        {
            "_id": ObjectId(pago_id)
        }
    )

    if not pago:
        raise HTTPException(
            status_code=404,
            detail="Pago no encontrado"
        )

    return serialize_pago(pago)


@app.post("/pagos")
async def crear_pago(data: dict):

    pedido_id = data.get("pedido_id")

    if not pedido_id:
        raise HTTPException(
            status_code=400,
            detail="pedido_id es obligatorio"
        )

    try:
        async with httpx.AsyncClient() as http_client:
            response = await http_client.get(
                f"{ORDERS_URL}/pedidos/{pedido_id}"
            )
    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Orders Service no disponible"
        )

    if response.status_code == 404:
        raise HTTPException(
            status_code=404,
            detail="Pedido no encontrado"
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail="Error consultando pedido"
        )

    pedido = response.json()

    monto = pedido.get("total")

    nuevo_pago = {
        "pedido_id": pedido_id,
        "monto": monto,
        "estado": "pendiente",
        "proveedor": "simulado"
    }

    resultado = pagos_collection.insert_one(
        nuevo_pago
    )

    pago_creado = pagos_collection.find_one(
        {
            "_id": resultado.inserted_id
        }
    )

    return serialize_pago(
        pago_creado
    )


@app.put("/pagos/{pago_id}/confirmar")
async def confirmar_pago(pago_id: str):

    if not ObjectId.is_valid(pago_id):
        raise HTTPException(
            status_code=400,
            detail="ID de pago invalido"
        )

    pago = pagos_collection.find_one(
        {
            "_id": ObjectId(pago_id)
        }
    )

    if not pago:
        raise HTTPException(
            status_code=404,
            detail="Pago no encontrado"
        )

    if pago.get("estado") == "pagado":
        raise HTTPException(
            status_code=409,
            detail="El pago ya fue confirmado"
        )

    pagos_collection.update_one(
        {
            "_id": ObjectId(pago_id)
        },
        {
            "$set": {
                "estado": "pagado"
            }
        }
    )

    pedido_id = pago["pedido_id"]

    try:
        async with httpx.AsyncClient() as http_client:
            await http_client.put(
                f"{ORDERS_URL}/pedidos/{pedido_id}/estado",
                json={
                    "estado": "pagado"
                }
            )
    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="No fue posible actualizar el pedido"
        )

    pago_actualizado = pagos_collection.find_one(
        {
            "_id": ObjectId(pago_id)
        }
    )

    return serialize_pago(
        pago_actualizado
    )