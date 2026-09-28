import os

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv


load_dotenv()

app = FastAPI(
    title="Backend API 2 Seguritizado",
    description="Segundo backend protegido con Bearer Token"
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
        "service": "Backend API 2"
    }


@app.get("/productos")
def productos(
    token: str = Depends(validar_token)
):
    return {
        "productos": [
            {"id": 1, "nombre": "Mouse", "precio": 25000},
            {"id": 2, "nombre": "Audifonos", "precio": 50000},
            {"id": 3, "nombre": "Webcam", "precio": 40000}
        ]
    }


@app.get("/ordenes")
def ordenes(
    token: str = Depends(validar_token)
):
    return {
        "ordenes": [
            {"id": 2001, "status": "pagada"},
            {"id": 2002, "status": "pendiente"}
        ]
    }