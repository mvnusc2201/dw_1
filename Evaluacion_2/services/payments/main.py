
import os
import secrets
import math

import httpx

from bson import ObjectId
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pymongo import MongoClient, ReturnDocument
from pymongo.errors import DuplicateKeyError


# ==========================================
# CONFIGURACIÓN
# ==========================================

app = FastAPI(
    title="Payments Service",
    description="Microservicio privado de pagos - Doggy's"
)

MONGO_URL = os.getenv(
    "MONGO_URL",
    "mongodb://127.0.0.1:27017/"
)

ORDERS_URL = os.getenv(
    "ORDERS_URL",
    "http://127.0.0.1:9103"
)

client = MongoClient(
    MONGO_URL,
    serverSelectionTimeoutMS=5000
)

db = client["UNAB"]
pagos_collection = db["pagos"]


# ==========================================
# ÍNDICE ÚNICO - EVITAR PAGOS DUPLICADOS
# ==========================================

pagos_collection.create_index(
    "pedido_id",
    unique=True,
    name="uq_pago_pedido"
)


# ==========================================
# SEGURIDAD INTERNA
# ==========================================

@app.middleware("http")
async def proteger_payments(
    request: Request,
    call_next
):

    if request.url.path.startswith("/pagos"):

        clave_esperada = os.getenv(
            "PAYMENTS_INTERNAL_KEY",
            ""
        )

        clave_recibida = request.headers.get(
            "X-Internal-Key",
            ""
        )

        if (
            not clave_esperada
            or not secrets.compare_digest(
                clave_recibida,
                clave_esperada
            )
        ):
            return JSONResponse(
                status_code=403,
                content={
                    "detail": "Acceso interno no autorizado"
                }
            )

    return await call_next(request)


# ==========================================
# SERIALIZACIÓN
# ==========================================

def serialize_pago(pago):
    return {
        "id": str(pago["_id"]),
        "pedido_id": pago.get("pedido_id"),
        "monto": pago.get("monto"),
        "estado": pago.get("estado"),
        "proveedor": pago.get("proveedor")
    }


# ==========================================
# HEALTH CHECK
# ==========================================

@app.get("/health")
def health():
    return {
        "status": "OK",
        "service": "payments"
    }


# ==========================================
# OBTENER TODOS LOS PAGOS
# ==========================================

@app.get("/pagos")
def obtener_pagos():

    pagos = []

    for pago in pagos_collection.find():
        pagos.append(
            serialize_pago(pago)
        )

    return pagos


# ==========================================
# OBTENER PAGO POR ID
# ==========================================

@app.get("/pagos/{pago_id}")
def obtener_pago(pago_id: str):

    if not ObjectId.is_valid(pago_id):
        raise HTTPException(
            status_code=400,
            detail="ID de pago inválido"
        )

    pago = pagos_collection.find_one({
        "_id": ObjectId(pago_id)
    })

    if pago is None:
        raise HTTPException(
            status_code=404,
            detail="Pago no encontrado"
        )

    return serialize_pago(pago)


# ==========================================
# CREAR PAGO PENDIENTE
# ==========================================

@app.post("/pagos")
async def crear_pago(data: dict):

    # 1. Validar el identificador del pedido.

    pedido_id = data.get("pedido_id")

    if (
        not isinstance(pedido_id, str)
        or not ObjectId.is_valid(pedido_id)
    ):
        raise HTTPException(
            status_code=400,
            detail="pedido_id es obligatorio y debe ser válido"
        )

    # 2. Consultar el pedido real en Orders Service.

    try:
        async with httpx.AsyncClient(
            timeout=5.0
        ) as http_client:

            response = await http_client.get(
                f"{ORDERS_URL}/pedidos/{pedido_id}"
            )

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503,
            detail="Orders Service no disponible"
        ) from exc

    if response.status_code == 404:
        raise HTTPException(
            status_code=404,
            detail="Pedido no encontrado"
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail="Error consultando el pedido"
        )

    # 3. Obtener y validar los datos del pedido.

    try:
        pedido = response.json()

    except ValueError as exc:
        raise HTTPException(
            status_code=502,
            detail="Respuesta inválida de Orders Service"
        ) from exc

    if not isinstance(pedido, dict):
        raise HTTPException(
            status_code=502,
            detail="Formato de pedido inválido"
        )

    if pedido.get("id") != pedido_id:
        raise HTTPException(
            status_code=502,
            detail="Identificador de pedido inconsistente"
        )

    monto = pedido.get("total")

    if (
        isinstance(monto, bool)
        or not isinstance(monto, (int, float))
        or not math.isfinite(monto)
        or monto <= 0
    ):
        raise HTTPException(
            status_code=409,
            detail="El pedido no tiene un monto válido"
        )

    if pedido.get("estado") == "pagado":
        raise HTTPException(
            status_code=409,
            detail="El pedido ya está pagado"
        )

    # 4. Construir el documento del pago.

    nuevo_pago = {
        "pedido_id": pedido_id,
        "monto": monto,
        "estado": "pendiente",
        "proveedor": "simulado"
    }

    # 5. Registrar el pago.
    # El índice único impide duplicados simultáneos.

    try:
        resultado = pagos_collection.insert_one(
            nuevo_pago
        )

    except DuplicateKeyError as exc:
        raise HTTPException(
            status_code=409,
            detail="Este pedido ya tiene un pago registrado"
        ) from exc

    # 6. Recuperar el documento guardado.

    pago_creado = pagos_collection.find_one({
        "_id": resultado.inserted_id
    })

    if pago_creado is None:
        raise HTTPException(
            status_code=500,
            detail="No fue posible recuperar el pago"
        )

    return serialize_pago(pago_creado)


# ==========================================
# CONFIRMAR PAGO SIMULADO
# ==========================================

@app.put("/pagos/{pago_id}/confirmar")
async def confirmar_pago(pago_id: str):

    # 1. Validar identificador.

    if not ObjectId.is_valid(pago_id):
        raise HTTPException(
            status_code=400,
            detail="ID de pago inválido"
        )

    pago_object_id = ObjectId(pago_id)

    pago = pagos_collection.find_one({
        "_id": pago_object_id
    })

    if pago is None:
        raise HTTPException(
            status_code=404,
            detail="Pago no encontrado"
        )

    if pago.get("estado") == "pagado":
        raise HTTPException(
            status_code=409,
            detail="El pago ya fue confirmado"
        )

    # 2. Bloquear confirmaciones simultáneas.
    # Solo un proceso puede pasar de pendiente a confirmando.

    pago_bloqueado = pagos_collection.find_one_and_update(
        {
            "_id": pago_object_id,
            "estado": "pendiente"
        },
        {
            "$set": {
                "estado": "confirmando"
            }
        },
        return_document=ReturnDocument.AFTER
    )

    if pago_bloqueado is None:
        raise HTTPException(
            status_code=409,
            detail="El pago no está pendiente o ya se está confirmando"
        )

    pedido_id = pago_bloqueado["pedido_id"]

    # 3. Actualizar primero el estado del pedido.

    try:
        async with httpx.AsyncClient(
            timeout=5.0
        ) as http_client:

            response = await http_client.put(
                f"{ORDERS_URL}/pedidos/{pedido_id}/estado",
                json={
                    "estado": "pagado"
                }
            )

        if response.status_code not in (200, 204):
            raise HTTPException(
                status_code=502,
                detail="Orders Service rechazó la actualización"
            )

    except (httpx.RequestError, HTTPException) as exc:

        # Revertir el estado local si no se pudo
        # confirmar la respuesta de Orders Service.

        pagos_collection.update_one(
            {
                "_id": pago_object_id,
                "estado": "confirmando"
            },
            {
                "$set": {
                    "estado": "pendiente"
                }
            }
        )

        if isinstance(exc, HTTPException):
            raise

        raise HTTPException(
            status_code=503,
            detail="No fue posible actualizar el pedido"
        ) from exc

    # 4. Marcar el pago como pagado después de
    # comprobar la respuesta de Orders Service.

    pagos_collection.update_one(
        {
            "_id": pago_object_id,
            "estado": "confirmando"
        },
        {
            "$set": {
                "estado": "pagado"
            }
        }
    )

    # 5. Recuperar el pago actualizado.

    pago_actualizado = pagos_collection.find_one({
        "_id": pago_object_id
    })

    return serialize_pago(pago_actualizado)
