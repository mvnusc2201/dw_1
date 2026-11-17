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
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# --------------------------------------------------------------------------
# Configuración
# --------------------------------------------------------------------------
AUTH_SERVICE_URL = os.getenv(
    "AUTH_SERVICE_URL",
    "http://127.0.0.1:8100"
)

# NUEVO: conexión con Inventory Service
INVENTORY_SERVICE_URL = os.getenv(
    "INVENTORY_SERVICE_URL",
    "http://127.0.0.1:9102"
)

ORDERS_SERVICE_URL = os.getenv(
    "ORDERS_SERVICE_URL",
    "http://127.0.0.1:9103"
)

GRAPHQL_SERVICE_URL = os.getenv(
    "GRAPHQL_SERVICE_URL",
    "http://127.0.0.1:9105"
)

PAYMENTS_SERVICE_URL = os.getenv(
    "PAYMENTS_SERVICE_URL",
    "http://127.0.0.1:9104"
)

PAYMENTS_INTERNAL_KEY = os.getenv(
    "PAYMENTS_INTERNAL_KEY",
    ""
)

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


app = FastAPI(title="Doggis - API Gateway", version="1.0.0", lifespan=lifespan)

# CORS con credenciales: no se puede usar "*" como origen.
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# --------------------------------------------------
# SEGURIDAD: IMPEDIR SUPLANTACIÓN DE IDENTIDAD
# --------------------------------------------------

@app.middleware("http")
async def proteger_cabeceras_identidad(request: Request, call_next):
    """
    Rechaza cabeceras de identidad enviadas por clientes externos.
    Solo el Gateway puede generar estas cabeceras para los servicios internos.
    """

    for nombre in request.headers.keys():
        if nombre.lower().startswith("x-authenticated-"):
            return JSONResponse(
                status_code=400,
                content={
                    "detail": "Cabeceras de identidad reservadas"
                },
            )

    return await call_next(request)


# --------------------------------------------------------------------------
# Seguridad: dependencia que valida la sesión con el Auth Service
# --------------------------------------------------------------------------
@dataclass
class AuthContext:
    user_id: str
    username: str
    roles: list[str]

    @property
    def downstream_headers(self) -> dict[str, str]:
        return {
            "X-Authenticated-User": self.user_id,
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

@app.post("/auth/register", status_code=201)
async def gateway_register(request: Request):
    """Reenvía el registro de usuarios al Auth Service."""

    try:
        upstream = await request.app.state.http.post(
            f"{AUTH_SERVICE_URL}/auth/register",
            content=await request.body(),
            headers={"Content-Type": "application/json"},
            timeout=10.0,
        )

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503,
            detail="Auth Service no disponible",
        ) from exc

    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        media_type="application/json",
        headers={"Cache-Control": "no-store"},
    )

@app.post("/auth/login")
async def gateway_login(request: Request):
    """Reenvía el login a Auth Service y conserva la cookie."""

    try:
        upstream = await request.app.state.http.post(
            f"{AUTH_SERVICE_URL}/auth/login",
            content=await request.body(),
            headers={"Content-Type": "application/json"},
        )

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503,
            detail="Auth Service no disponible",
        ) from exc

    response = Response(
        content=upstream.content,
        status_code=upstream.status_code,
        media_type="application/json",
    )

    # Transmitir al navegador la cookie HttpOnly
    # emitida por Auth Service.
    for cookie in upstream.headers.get_list("set-cookie"):
        response.raw_headers.append(
            (b"set-cookie", cookie.encode("latin-1"))
        )

    return response

@app.get("/auth/me")
async def gateway_me(ctx: AuthContext = Depends(require_auth)):
    """Devuelve los datos de la sesión autenticada."""
    return {
        "authenticated": True,
        "user_id": ctx.user_id,
        "username": ctx.username,
        "roles": ctx.roles,
    }

@app.post("/auth/logout")
async def gateway_logout(request: Request):
    """Revoca la sesión en Auth Service y elimina la cookie."""

    token = request.cookies.get(COOKIE_NAME)

    if not token:
        response = Response(
            content='{"detail":"Sesión cerrada"}',
            media_type="application/json",
        )
        response.delete_cookie(COOKIE_NAME, path="/")
        return response

    try:
        upstream = await request.app.state.http.post(
            f"{AUTH_SERVICE_URL}/auth/logout",
            cookies={COOKIE_NAME: token},
            json={"token": token},
        )

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503,
            detail="Auth Service no disponible",
        ) from exc

    if upstream.status_code not in (200, 204):
        raise HTTPException(
            status_code=502,
            detail="No se pudo confirmar el cierre de sesión",
        )

    response = Response(
        content=upstream.content,
        status_code=upstream.status_code,
        media_type=(
            "application/json"
            if upstream.status_code == 200
            else None
        ),
    )

    response.delete_cookie(COOKIE_NAME, path="/")
    return response


@app.get("/api/v1/products")
async def list_products(request: Request):
    """Consulta los productos reales desde Inventory Service."""

    try:
        respuesta = await request.app.state.http.get(
            f"{INVENTORY_SERVICE_URL}/productos"
        )

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503,
            detail="Inventory Service no disponible"
        ) from exc

    if respuesta.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail="Error al consultar el inventario"
        )

    try:
        productos = respuesta.json()
    except ValueError as exc:
        raise HTTPException(
            status_code=502,
            detail="Respuesta inválida del inventario"
        ) from exc

    if not isinstance(productos, list):
        raise HTTPException(
            status_code=502,
            detail="Formato de catálogo inválido"
        )

    return {
        "products": [
            {
                "id": producto.get("id"),
                "name": producto.get("nombre"),
                "description": producto.get("descripcion"),
                "price_clp": producto.get("precio"),
                "available": producto.get("disponible", False)
            }
            for producto in productos
        ]
    }



class CrearPedidoRequest(BaseModel):
    producto_id: str = Field(pattern=r"^[0-9a-fA-F]{24}$")
    cantidad: int = Field(ge=1, le=50)


@app.get("/api/v1/orders")
async def list_orders(
    request: Request,
    ctx: AuthContext = Depends(require_auth)
):
    """Lista únicamente los pedidos del usuario autenticado."""

    if "cliente" not in ctx.roles:
        raise HTTPException(status_code=403, detail="Acceso denegado")

    try:
        upstream = await request.app.state.http.get(
            f"{ORDERS_SERVICE_URL}/pedidos",
            headers=ctx.downstream_headers,
        )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503,
            detail="Orders Service no disponible"
        ) from exc

    if upstream.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail="Error consultando pedidos"
        )

    try:
        pedidos = upstream.json()
    except ValueError as exc:
        raise HTTPException(
            status_code=502,
            detail="Respuesta inválida de pedidos"
        ) from exc

    if not isinstance(pedidos, list):
        raise HTTPException(
            status_code=502,
            detail="Formato de pedidos inválido"
        )

    propios = [
        pedido for pedido in pedidos
        if pedido.get("cliente_id") == ctx.user_id
    ]

    return {"orders": propios}


@app.post("/api/v1/orders", status_code=201)
async def create_order(
    request: Request,
    body: CrearPedidoRequest,
    ctx: AuthContext = Depends(require_auth)
):
    """Crea un pedido con identidad y precio verificados."""

    if "cliente" not in ctx.roles:
        raise HTTPException(status_code=403, detail="Acceso denegado")

    datos = {
        "cliente_id": ctx.user_id,
        "producto_id": body.producto_id,
        "cantidad": body.cantidad
    }

    try:
        upstream = await request.app.state.http.post(
            f"{ORDERS_SERVICE_URL}/pedidos",
            json=datos,
            headers=ctx.downstream_headers,
            timeout=10.0
        )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503,
            detail="Orders Service no disponible"
        ) from exc

    if upstream.status_code >= 400:
        detalle = "No fue posible crear el pedido"
        try:
            detalle = upstream.json().get("detail", detalle)
        except ValueError:
            pass

        raise HTTPException(
            status_code=(
                upstream.status_code
                if upstream.status_code < 500 else 502
            ),
            detail=detalle
        )

    try:
        pedido = upstream.json()
    except ValueError as exc:
        raise HTTPException(
            status_code=502,
            detail="Respuesta inválida de Orders Service"
        ) from exc

    if pedido.get("cliente_id") != ctx.user_id:
        raise HTTPException(
            status_code=502,
            detail="Identidad del pedido inconsistente"
        )

    return {"created": pedido}


# ==========================================
# PAYMENTS SERVICE - API GATEWAY
# ==========================================

class CrearPagoRequest(BaseModel):
    pedido_id: str = Field(pattern=r"^[0-9a-fA-F]{24}$")


@app.post("/api/v1/payments", status_code=201)
async def crear_pago_gateway(
    # 3. Registrar pago pendiente.
try:
    pago_respuesta = await request.app.state.http.post(
        f"{PAYMENTS_SERVICE_URL}/pagos",
        json={"pedido_id": body.pedido_id},
        headers=ctx.downstream_headers
    )
    body: CrearPagoRequest,
    request: Request,
    ctx: AuthContext = Depends(require_auth)
):
    """Registra un pago pendiente para un pedido del usuario."""

    try:
        # 1. Consultar el pedido real.
        pedido_respuesta = await request.app.state.http.get(
            f"{ORDERS_SERVICE_URL}/pedidos/{body.pedido_id}",
            headers=ctx.downstream_headers
        )

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503,
            detail="Orders Service no disponible"
        ) from exc

    if pedido_respuesta.status_code == 404:
        raise HTTPException(
            status_code=404,
            detail="Pedido no encontrado"
        )

    if pedido_respuesta.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail="No se pudo consultar el pedido"
        )

    try:
        pedido = pedido_respuesta.json()
    except ValueError as exc:
        raise HTTPException(
            status_code=502,
            detail="Respuesta inválida de Orders Service"
        ) from exc

    # 2. Verificar que el pedido pertenece al usuario.
    if pedido.get("cliente_id") != ctx.user_id:
        raise HTTPException(
            status_code=403,
            detail="No puedes pagar un pedido de otro usuario"
        )

    monto = pedido.get("total")

    if (
        isinstance(monto, bool)
        or not isinstance(monto, (int, float))
        or monto <= 0
    ):
        raise HTTPException(
            status_code=409,
            detail="El pedido no tiene un monto válido"
        )

    # 3. Registrar pago pendiente.
    try:
        pago_respuesta = await request.app.state.http.post(
            f"{PAYMENTS_SERVICE_URL}/pagos",
            json={"pedido_id": body.pedido_id},
            headers=ctx.downstream_headers
        )

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503,
            detail="Payments Service no disponible"
        ) from exc

    if pago_respuesta.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail="No fue posible registrar el pago"
        )

    try:
        pago = pago_respuesta.json()
    except ValueError as exc:
        raise HTTPException(
            status_code=502,
            detail="Respuesta inválida de Payments Service"
        ) from exc

    # 4. Verificar consistencia.
    if (
        pago.get("pedido_id") != body.pedido_id
        or pago.get("estado") != "pendiente"
        or pago.get("monto") != monto
    ):
        raise HTTPException(
            status_code=502,
            detail="Los datos del pago no coinciden con el pedido"
        )

    return {"payment": pago}



@app.post("/graphql")
async def graphql_endpoint(
    body: GraphQLRequest,
    request: Request,
    ctx: AuthContext = Depends(require_auth)
):
    """Reenvía consultas autenticadas al GraphQL Gateway real."""

    clave_interna = os.getenv("GRAPHQL_INTERNAL_KEY", "")

    if not clave_interna:
        raise HTTPException(
            status_code=503,
            detail="GraphQL no está configurado"
        )

    headers = {
        **ctx.downstream_headers,
        "X-Internal-Key": clave_interna
    }

    try:
        upstream = await request.app.state.http.post(
            f"{GRAPHQL_SERVICE_URL}/graphql",
            json=body.model_dump(exclude_none=True),
            headers=headers,
            timeout=10.0
        )

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503,
            detail="GraphQL Service no disponible"
        ) from exc

    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        media_type="application/json"
    )



# --------------------------------------------------------------------------
# Frontend estático (debe montarse AL FINAL para no tapar las rutas de la API)
# --------------------------------------------------------------------------
FRONTEND_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")