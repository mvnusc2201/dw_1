from fastapi import FastAPI, HTTPException
import httpx

app = FastAPI(
    title="API Gateway - Semana 7",
    description="Gateway encargado de comunicar diferentes APIs"
)

BACKEND_URL = "http://localhost:9000"
BACKEND_URL2 = "http://localhost:9100"


@app.get("/")
def inicio():
    return {
        "mensaje": "API Gateway funcionando correctamente"
    }


@app.get("/api/products")
async def products():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BACKEND_URL}/products"
            )

        return response.json()

    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Backend API 1 no disponible"
        )


@app.get("/api/productos")
async def productos():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BACKEND_URL2}/productos"
            )

        return response.json()

    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Backend API 2 no disponible"
        )


@app.get("/api/orders")
async def orders():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BACKEND_URL}/orders"
            )

        return response.json()

    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Backend API 1 no disponible"
        )


@app.get("/api/ordenes")
async def ordenes():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BACKEND_URL2}/ordenes"
            )

        return response.json()

    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Backend API 2 no disponible"
        )