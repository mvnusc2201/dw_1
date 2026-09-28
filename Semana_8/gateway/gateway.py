import os

import httpx

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv


load_dotenv()

app = FastAPI(
    title="API Gateway Seguritizado",
    description="Gateway protegido con Bearer Token y conexión segura a backends"
)

security = HTTPBearer()

BACKEND_URL = "http://localhost:9000"
BACKEND_URL2 = "http://localhost:9100"

TOKEN_GATEWAY = os.getenv("TOKEN_GATEWAY")
TOKEN_BACKEND_1 = os.getenv("TOKEN_BACKEND_1")
TOKEN_BACKEND_2 = os.getenv("TOKEN_BACKEND_2")


def validar_token_gateway(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    if credentials.credentials != TOKEN_GATEWAY:
        raise HTTPException(
            status_code=403,
            detail="Token del gateway inválido"
        )

    return credentials.credentials


@app.get("/")
def inicio():
    return {
        "mensaje": "API Gateway seguritizado funcionando"
    }


@app.get("/api/products")
async def products(
    token: str = Depends(validar_token_gateway)
):
    try:
        headers = {
            "Authorization": f"Bearer {TOKEN_BACKEND_1}"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BACKEND_URL}/products",
                headers=headers
            )

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail="Error al acceder al Backend API 1"
            )

        return response.json()

    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Backend API 1 no disponible"
        )


@app.get("/api/orders")
async def orders(
    token: str = Depends(validar_token_gateway)
):
    try:
        headers = {
            "Authorization": f"Bearer {TOKEN_BACKEND_1}"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BACKEND_URL}/orders",
                headers=headers
            )

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail="Error al acceder al Backend API 1"
            )

        return response.json()

    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Backend API 1 no disponible"
        )


@app.get("/api/productos")
async def productos(
    token: str = Depends(validar_token_gateway)
):
    try:
        headers = {
            "Authorization": f"Bearer {TOKEN_BACKEND_2}"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BACKEND_URL2}/productos",
                headers=headers
            )

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail="Error al acceder al Backend API 2"
            )

        return response.json()

    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Backend API 2 no disponible"
        )


@app.get("/api/ordenes")
async def ordenes(
    token: str = Depends(validar_token_gateway)
):
    try:
        headers = {
            "Authorization": f"Bearer {TOKEN_BACKEND_2}"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BACKEND_URL2}/ordenes",
                headers=headers
            )

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail="Error al acceder al Backend API 2"
            )

        return response.json()

    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Backend API 2 no disponible"
        )