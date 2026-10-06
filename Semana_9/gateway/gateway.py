import os

import httpx

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI(
    title="API Gateway Semana 9",
    description="Gateway con login, sesion, introspection, Vault y autorizacion"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

VAULT_ADDR = os.getenv(
    "VAULT_ADDR",
    "http://127.0.0.1:8200"
)

VAULT_TOKEN = os.getenv("VAULT_TOKEN")

AUTH_SERVICE_URL = os.getenv(
    "AUTH_SERVICE_URL",
    "http://127.0.0.1:8100"
)

BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:9000"
)


if not VAULT_TOKEN:
    raise RuntimeError(
        "VAULT_TOKEN no esta configurado"
    )


class LoginRequest(BaseModel):
    username: str
    password: str


async def get_vault_secrets():
    url = f"{VAULT_ADDR}/v1/secret/data/gateway"

    headers = {
        "X-Vault-Token": VAULT_TOKEN
    }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                url,
                headers=headers
            )
    except httpx.RequestError:
        raise HTTPException(
            status_code=500,
            detail="Vault no disponible"
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=500,
            detail="No fue posible acceder a Vault"
        )

    data = response.json()

    return data["data"]["data"]


async def introspect_token(token: str):
    secrets_data = await get_vault_secrets()

    auth_secret = secrets_data[
        "auth_introspection_secret"
    ]

    headers = {
        "X-Auth-Secret": auth_secret
    }

    body = {
        "token": token
    }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                f"{AUTH_SERVICE_URL}/introspect",
                json=body,
                headers=headers
            )
    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Servicio de autenticacion no disponible"
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=503,
            detail="Error al validar la sesion"
        )

    identity = response.json()

    if not identity.get("active"):
        raise HTTPException(
            status_code=401,
            detail="Sesion invalida o expirada"
        )

    return identity


async def get_current_user(request: Request):

    token = request.cookies.get("session_token")

    if not token:
        raise HTTPException(
            status_code=401,
            detail="No existe una sesion activa"
        )

    return await introspect_token(token)


async def call_backend(
    method: str,
    path: str,
    identity: dict,
    body: bytes | None = None
):
    secrets_data = await get_vault_secrets()

    backend_secret = secrets_data[
        "backend_shared_secret"
    ]

    roles = ",".join(identity["roles"])

    headers = {
        "X-Gateway-Secret": backend_secret,
        "X-Authenticated-User": identity["user_id"],
        "X-Authenticated-Username": identity["username"],
        "X-Authenticated-Roles": roles
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.request(
                method=method,
                url=f"{BACKEND_URL}/{path}",
                content=body,
                headers=headers
            )
    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail="Backend no disponible"
        )

    return Response(
        content=response.content,
        status_code=response.status_code,
        media_type=response.headers.get(
            "content-type",
            "application/json"
        )
    )


@app.get("/health")
def health():
    return {
        "status": "OK",
        "service": "API Gateway"
    }


@app.post("/auth/login")
async def login(
    data: LoginRequest,
    response: Response
):
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            auth_response = await client.post(
                f"{AUTH_SERVICE_URL}/login",
                json=data.model_dump()
            )
    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Servicio de autenticacion no disponible"
        )

    if auth_response.status_code == 401:
        raise HTTPException(
            status_code=401,
            detail="Credenciales incorrectas"
        )

    if auth_response.status_code != 200:
        raise HTTPException(
            status_code=503,
            detail="Error en servicio de autenticacion"
        )

    result = auth_response.json()

    token = result["access_token"]

    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=result.get("expires_in", 900)
    )

    return {
        "message": "Login correcto"
    }


@app.get("/auth/me")
async def me(request: Request):

    identity = await get_current_user(request)

    return {
        "user_id": identity["user_id"],
        "username": identity["username"],
        "roles": identity["roles"]
    }


@app.post("/auth/logout")
async def logout(
    request: Request,
    response: Response
):
    token = request.cookies.get("session_token")

    if not token:
        raise HTTPException(
            status_code=401,
            detail="No existe una sesion activa"
        )

    secrets_data = await get_vault_secrets()

    auth_secret = secrets_data[
        "auth_introspection_secret"
    ]

    headers = {
        "X-Auth-Secret": auth_secret
    }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(
                f"{AUTH_SERVICE_URL}/logout",
                json={
                    "token": token
                },
                headers=headers
            )
    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Servicio de autenticacion no disponible"
        )

    response.delete_cookie(
        key="session_token"
    )

    return {
        "message": "Sesion cerrada correctamente"
    }


@app.get("/api/products")
async def products(request: Request):

    identity = await get_current_user(request)

    return await call_backend(
        method="GET",
        path="products",
        identity=identity
    )


@app.get("/api/orders")
async def orders(request: Request):

    identity = await get_current_user(request)

    return await call_backend(
        method="GET",
        path="orders",
        identity=identity
    )


@app.delete("/api/products/{product_id}")
async def delete_product(
    product_id: int,
    request: Request
):
    identity = await get_current_user(request)

    if "admin" not in identity["roles"]:
        raise HTTPException(
            status_code=403,
            detail="Se requiere rol administrador"
        )

    return await call_backend(
        method="DELETE",
        path=f"products/{product_id}",
        identity=identity
    )