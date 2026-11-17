import os
import hmac

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from bson import ObjectId
from fastapi import Response
from pydantic import BaseModel, Field
from pymongo.errors import DuplicateKeyError


app = FastAPI(
    title="Clients Service",
    description="Microservicio privado de clientes para Doggy's"
)

@app.middleware("http")
async def proteger_clientes(request: Request, call_next):

    if request.url.path.startswith("/clientes"):
        clave_esperada = os.getenv("CLIENTS_INTERNAL_KEY")
        clave_recibida = request.headers.get("X-Internal-Key")

        if not clave_esperada:
            return JSONResponse(
                status_code=503,
                content={"detail": "Credencial interna no configurada"}
            )

        if not clave_recibida or not hmac.compare_digest(
            clave_recibida, clave_esperada
        ):
            return JSONResponse(
                status_code=403,
                content={"detail": "Acceso interno no autorizado"}
            )

    return await call_next(request)

# --------------------------------------------------
# REGISTRO INTERNO DE PERFILES
# --------------------------------------------------

class InternalClientRegister(BaseModel):
    user_id: str = Field(
        pattern=r"^CLI-[A-Za-z0-9-]+$",
        max_length=70,
    )
    nombre: str = Field(min_length=2, max_length=80)
    correo: str = Field(
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    )
    telefono: str = Field(pattern=r"^\+569\d{8}$")


@app.post("/clientes/internal/register", status_code=201)
def registrar_perfil_interno(
    body: InternalClientRegister,
    response: Response,
):
    nuevo_cliente = {
        "user_id": body.user_id,
        "nombre": body.nombre.strip(),
        "email": body.correo.strip().lower(),
        "telefono": body.telefono,
        "direccion": None,
    }

    creado = False

    try:
        resultado = clientes_collection.update_one(
            {"user_id": body.user_id},
            {"$setOnInsert": nuevo_cliente},
            upsert=True,
        )
        creado = resultado.upserted_id is not None

    except DuplicateKeyError:
        # Otro intento pudo crear el perfil simultáneamente.
        pass

    perfil = clientes_collection.find_one({
        "user_id": body.user_id
    })

    if perfil is None:
        raise HTTPException(
            status_code=503,
            detail="No fue posible recuperar el perfil",
        )

    response.status_code = 201 if creado else 200

    return serialize_cliente(perfil)

client = MongoClient("mongodb://localhost:27017/")

db = client["UNAB"]
clientes_collection = db["clientes"]


def serialize_cliente(cliente):
    return {
        "id": str(cliente["_id"]),
        "user_id": cliente.get("user_id"),
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
        "user_id": cliente.get("user_id"),
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