import os

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv


load_dotenv()

app = FastAPI(
    title="Backend API 1 Seguritizado",
    description="Backend protegido con Bearer Token"
)

security = HTTPBearer()

TOKEN_BACKEND = os.getenv("TOKEN_BACKEND")


def validar_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    if credentials.credentials != TOKEN_BACKEND:
        raise HTTPException(
            status_code=403,
            detail="Token inválido"
        )

    return credentials.credentials


@app.get("/health")
def health(
    token: str = Depends(validar_token)
):
    return {
        "status": "OK",
        "service": "Backend API 1"
    }


@app.get("/products")
def products(
    token: str = Depends(validar_token)
):
    return {
        "products": [
            {"id": 1, "name": "Notebook", "price": 900000},
            {"id": 2, "name": "Monitor", "price": 250000},
            {"id": 3, "name": "Teclado", "price": 45000}
        ]
    }


@app.get("/orders")
def orders(
    token: str = Depends(validar_token)
):
    return {
        "orders": [
            {"id": 1001, "status": "paid"},
            {"id": 1002, "status": "pending"},
            {"id": 1003, "status": "pending"}
        ]
    }