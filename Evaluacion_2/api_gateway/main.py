"""
Doggis - API Gateway (puerto 8000)

Responsabilidad: punto de entrada único. Valida la sesión contra el Auth
Service, simula el enrutamiento hacia los microservicios internos y sirve
el frontend.

Rutas:
    GET  /api/v1/products   -> pública
    GET  /api/v1/orders     -> protegida (cookie session_token)
    POST /api/v1/orders     -> protegida
    POST /graphql           -> protegida
    GET  /                  -> frontend estático (carpeta ../frontend)

Ejecutar (desde la raíz del proyecto):
    uvicorn api_gateway.main:app --host 127.0.0.1 --port 8000 --reload
"""

import os
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# --------------------------------------------------------------------------
# Configuración
# --------------------------------------------------------------------------
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8100")
COOKIE_NAME = "session_token"
FRONTEND_DIR = Path(
    os.getenv("FRONTEND_DIR", Path(__file__).resolve().parent.parent / "frontend")
)

ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:5500",  # Live Server de VS Code
    "http://127.0.0.1:5500",
]


# --------------------------------------------------------------------------
# Ciclo de vida: un único cliente HTTP reutilizable
# --------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http = httpx.AsyncClient(timeout=3.0)
    yield
    await app.state.http.aclose()


app = FastAPI(title="Doggy's - API Gateway", version="1.0.0", lifespan=lifespan)

# CORS con credenciales: no se puede usar "*" como origen.
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


# --------------------------------------------------------------------------
# Seguridad: dependencia que valida la sesión con el Auth Service
# --------------------------------------------------------------------------
@dataclass
class AuthContext:
    username: str
    roles: list[str]

    @property
    def downstream_headers(self) -> dict[str, str]:
        """Headers que el Gateway inyectaría hacia los microservicios internos.

        Se construyen SOLO a partir de la respuesta del Auth Service; cualquier
        X-Authenticated-* enviado por el cliente se ignora (anti-suplantación).
        """
        return {
            "X-Authenticated-User": self.username,
            "X-Authenticated-Roles": ",".join(self.roles),
        }


async def require_auth(request: Request) -> AuthContext:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise HTTPException(
            status_code=401,
            detail="No autenticado: falta la cookie de sesión",
            headers={"WWW-Authenticate": "Cookie"},
        )

    try:
        resp = await request.app.state.http.post(
            f"{AUTH_SERVICE_URL}/auth/introspect", json={"token": token}
        )
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Auth Service no disponible")

    if resp.status_code != 200:
        raise HTTPException(status_code=401, detail="Sesión no válida")

    data = resp.json()
    if not data.get("active"):
        raise HTTPException(
            status_code=401,
            detail="Sesión inválida o expirada",
            headers={"WWW-Authenticate": "Cookie"},
        )

return AuthContext(
    user_id=data["user_id"],
    username=data["username"],
    roles=data.get("roles", []),
)

# --------------------------------------------------------------------------
# Modelos
# --------------------------------------------------------------------------
class GraphQLRequest(BaseModel):
    query: str
    variables: dict[str, Any] | None = None
    operationName: str | None = None


# --------------------------------------------------------------------------
# Rutas
# --------------------------------------------------------------------------
@app.get("/health")
def health():
    return {"service": "api-gateway", "status": "ok"}


@app.get("/api/v1/products")
def list_products():
    """Ruta pública: no requiere cookie."""
    return {
        "products": [
            {"id": 1, "name": "Completo Italiano", "price_clp": 3200},
            {"id": 2, "name": "Completo As", "price_clp": 3500},
            {"id": 3, "name": "Hot Dog Americano", "price_clp": 2800},
            {"id": 4, "name": "Hot Dog Doble", "price_clp": 3900},
        ]
    }


@app.get("/api/v1/orders")
async def list_orders(ctx: AuthContext = Depends(require_auth)):
    """Protegida: simula el enrutamiento hacia el microservicio `orders`."""
    return {
        "routed_to": "orders-service (simulado)",
        "forwarded_headers": ctx.downstream_headers,
        "orders": [
            {"id": 101, "customer": ctx.username, "status": "EN_PREPARACION"},
        ],
    }


@app.post("/api/v1/orders", status_code=201)
async def create_order(
    payload: dict[str, Any], ctx: AuthContext = Depends(require_auth)
):
    return {
        "routed_to": "orders-service (simulado)",
        "forwarded_headers": ctx.downstream_headers,
        "created": {"id": 102, "customer": ctx.username, **payload},
    }


@app.post("/graphql")
async def graphql_endpoint(
    body: GraphQLRequest, ctx: AuthContext = Depends(require_auth)
):
    """Protegida: simula el reenvío hacia el servicio GraphQL interno."""
    return {
        "data": None,
        "extensions": {
            "routed_to": "graphql-service (simulado)",
            "forwarded_headers": ctx.downstream_headers,
            "received_query": body.query,
        },
    }


# --------------------------------------------------------------------------
# Frontend estático (debe montarse AL FINAL para no tapar las rutas de la API)
# --------------------------------------------------------------------------
FRONTEND_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")