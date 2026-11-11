"""
Doggis - Auth Service (puerto 8100)

Responsabilidad: manejar la identidad y emitir la cookie de sesión segura.

Rutas:
    POST /auth/login       -> valida credenciales y emite cookie `session_token`
    POST /auth/introspect  -> informa si un token es válido y qué roles tiene
    POST /auth/logout      -> invalida la sesión y elimina la cookie

Ejecutar (desde la raíz del proyecto):
    uvicorn auth_service.main:app --host 127.0.0.1 --port 8100 --reload
"""

import hashlib
import hmac
import os
import secrets
import time

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import AliasChoices, BaseModel, Field
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from pymongo.errors import DuplicateKeyError, PyMongoError

from auth_service.database import get_users_collection
from auth_service.security import hash_password
from pymongo.errors import PyMongoError
from auth_service.security import verify_password
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from collections import deque
from threading import Lock

from auth_service.clients_client import (
    ClientsServiceError,
    crear_perfil_cliente,
)

# --------------------------------------------------------------------------
# Configuración
# --------------------------------------------------------------------------
# En producción estos valores vendrían de Vault (p. ej. vault://doggys/auth/...).
COOKIE_NAME = "session_token"
SESSION_TTL_SECONDS = int(os.getenv("SESSION_TTL_SECONDS", "900")) # 30 min
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"  # True con HTTPS

# Orígenes del frontend que pueden llamar al Auth Service con cookies.
# (8000 = API Gateway sirviendo el frontend, 5500 = Live Server de VS Code)
ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
]

# --------------------------------------------------------------------------
# "Base de datos" en memoria
# --------------------------------------------------------------------------


def _hash_password(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)


def _make_user(user_id: str, password: str, roles: list[str]) -> dict:
    salt = os.urandom(16)
    return {
        "user_id": user_id,
        "salt": salt,
        "hash": _hash_password(password, salt),
        "roles": roles,
    }


# Usuarios temporales para pruebas locales
USERS_DB: dict[str, dict] = {
    "cliente": _make_user("CLI-0001", "cliente123", ["cliente"]),
    "operador": _make_user("EMP-0001", "operador123", ["operador"]),
}


# token -> {"username": str, "roles": list[str], "exp": float}
SESSIONS: dict[str, dict] = {}

# --------------------------------------------------------------------------
# Modelos
# --------------------------------------------------------------------------


class LoginRequest(BaseModel):
    # Se aceptan alias en español por si el formulario del portal los usa.
    username: str = Field(validation_alias=AliasChoices("username", "usuario"))
    password: str = Field(
        validation_alias=AliasChoices("password", "contrasena", "clave")
    )


class IntrospectRequest(BaseModel):
    token: str | None = None


class IntrospectResponse(BaseModel):
    active: bool
    user_id: str | None = None
    username: str | None = None
    roles: list[str] = Field(default_factory=list)
    exp: int | None = None

# --------------------------------------------------------------------------
# Lógica
# --------------------------------------------------------------------------


def _authenticate(username: str, password: str) -> dict | None:
    username = username.strip().lower()

    # Usuarios de prueba
    demo_user = USERS_DB.get(username)

    if demo_user is not None:
        candidate = _hash_password(password, demo_user["salt"])

        if not hmac.compare_digest(candidate, demo_user["hash"]):
            return None

        return {
            "user_id": demo_user["user_id"],
            "username": username,
            "roles": demo_user["roles"],
        }

    # Usuarios registrados en MongoDB
    try:
        user = get_users_collection().find_one(
            {"correo": username}
        )
    except PyMongoError as exc:
        raise HTTPException(
            status_code=503,
            detail="Servicio de identidades no disponible",
        ) from exc

    if user is None:
        return None

    if not verify_password(password, user.get("password_hash", "")):
        return None

    return {
        "user_id": user["user_id"],
        "username": user["username"],
        "roles": user["roles"],
    }


def _get_valid_session(token: str | None) -> dict | None:
    if not token:
        return None
    session = SESSIONS.get(token)
    if session is None:
        return None
    if session["exp"] <= time.time():
        SESSIONS.pop(token, None)
        return None
    return session


# --------------------------------------------------------------------------
# Aplicación
# --------------------------------------------------------------------------
app = FastAPI(title="Doggis - Auth Service", version="1.0.0")

# --------------------------------------------------
# SEGURIDAD: PROTEGER DATOS EN ERRORES DE VALIDACIÓN
# --------------------------------------------------

@app.exception_handler(RequestValidationError)
async def manejar_error_validacion(
    request: Request,
    exc: RequestValidationError,
):
    errores_seguros = []

    for error in exc.errors():
        errores_seguros.append({
            "type": error.get("type", "value_error"),
            "loc": list(error.get("loc", [])),
            "msg": error.get("msg", "Datos inválidos"),
        })

    return JSONResponse(
        status_code=422,
        content={"detail": errores_seguros},
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


@app.get("/health")
def health():
    return {"service": "auth", "status": "ok"}

# --------------------------------------------------
# SEGURIDAD: LIMITAR INTENTOS DE LOGIN
# --------------------------------------------------

MAX_LOGIN_ATTEMPTS = 5
LOGIN_WINDOW_SECONDS = 900  # 15 minutos

LOGIN_FAILURES = {}
LOGIN_FAILURES_LOCK = Lock()


def _login_key(username: str, request: Request):
    """Identifica los intentos por usuario y origen."""
    username = username.strip().lower()
    ip = request.client.host if request.client else "unknown"

    return (username, ip)


def _clean_attempts(attempts, now):
    """Elimina los intentos fuera de la ventana."""
    while attempts and now - attempts[0] >= LOGIN_WINDOW_SECONDS:
        attempts.popleft()


def _check_login_limit(key):
    """Rechaza solicitudes que superen el límite."""

    now = time.monotonic()

    with LOGIN_FAILURES_LOCK:
        attempts = LOGIN_FAILURES.get(key)

        if attempts is None:
            return

        _clean_attempts(attempts, now)

        if not attempts:
            del LOGIN_FAILURES[key]
            return

        if len(attempts) >= MAX_LOGIN_ATTEMPTS:
            retry_after = max(
                1,
                int(LOGIN_WINDOW_SECONDS - (now - attempts[0])) + 1
            )

            raise HTTPException(
                status_code=429,
                detail="Demasiados intentos. Intenta nuevamente más tarde.",
                headers={"Retry-After": str(retry_after)},
            )


def _record_failed_login(key):
    """Registra una autenticación fallida."""

    now = time.monotonic()

    with LOGIN_FAILURES_LOCK:
        attempts = LOGIN_FAILURES.setdefault(key, deque())

        _clean_attempts(attempts, now)

        attempts.append(now)


def _clear_login_failures(key):
    """Reinicia el contador después de un login válido."""

    with LOGIN_FAILURES_LOCK:
        LOGIN_FAILURES.pop(key, None)


@app.post("/auth/login")
def login(body: LoginRequest, response: Response, request: Request):

    key = _login_key(body.username, request)

    # Comprobar si alcanzó el límite
    _check_login_limit(key)

    # Validar credenciales
    user = _authenticate(body.username, body.password)

    if user is None:
        _record_failed_login(key)

        raise HTTPException(
            status_code=401,
            detail="Credenciales inválidas"
        )

    # Login correcto: limpiar intentos fallidos
    _clear_login_failures(key)

    token = secrets.token_urlsafe(32)
    SESSIONS[token] = {
        "user_id": user["user_id"],
        "username": user["username"],
        "roles": user["roles"],
        "exp": time.time() + SESSION_TTL_SECONDS,
    }

    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        max_age=SESSION_TTL_SECONDS,
        httponly=True,  # inaccesible desde JavaScript (mitiga XSS)
        samesite="lax",  # mitiga CSRF
        secure=COOKIE_SECURE,
        path="/",
    )
    return {
        "message": "Login exitoso",
        "user_id": user["user_id"],
        "username": user["username"],
        "roles": user["roles"],
    }


@app.post("/auth/introspect", response_model=IntrospectResponse)
def introspect(request: Request, body: IntrospectRequest | None = None):
    """Usado por el API Gateway. Acepta el token en el body o en la cookie."""
    token = (body.token if body else None) or request.cookies.get(COOKIE_NAME)
    session = _get_valid_session(token)

    if session is None:
        return IntrospectResponse(active=False)

    return IntrospectResponse(
        active=True,
        user_id=session["user_id"],  # NUEVO: identificador del usuario
        username=session["username"],
        roles=session["roles"],
        exp=int(session["exp"]),
    )

@app.get("/auth/me")
def get_current_user(request: Request):
    token = request.cookies.get(COOKIE_NAME)
    session = _get_valid_session(token)

    if session is None:
        raise HTTPException(
            status_code=401,
            detail="Sesión inválida o expirada",
        )

    return {
        "user_id": session["user_id"],
        "username": session["username"],
        "roles": session["roles"],
    }

@app.post("/auth/logout")
def logout(request: Request, response: Response):
    token = request.cookies.get(COOKIE_NAME)
    if token:
        SESSIONS.pop(token, None)
    response.delete_cookie(
        key=COOKIE_NAME,
        path="/",
        httponly=True,
        samesite="lax",
        secure=COOKIE_SECURE,
    )
# --------------------------------------------------
# REGISTRO DE USUARIOS - DOGGY'S
# --------------------------------------------------

class RegisterRequest(BaseModel):
    nombre: str = Field(min_length=2, max_length=80)
    correo: str = Field(
        min_length=5,
        max_length=254,
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    )
    telefono: str = Field(pattern=r"^\+569\d{8}$")
    clave: str = Field(min_length=8, max_length=72)
    aceptaTerminos: Literal[True]


@app.post("/auth/register", status_code=201)
def register(body: RegisterRequest):
    correo = body.correo.strip().lower()
    nombre = body.nombre.strip()
    collection = get_users_collection()

    if len(nombre) < 2:
        raise HTTPException(
            status_code=400,
            detail="Nombre demasiado corto",
        )

    try:
        usuario = collection.find_one({"correo": correo})

        if usuario is None:
            user_id = f"CLI-{uuid4().hex}"

            nuevo_usuario = {
                "user_id": user_id,
                "nombre": nombre,
                "correo": correo,
                "username": correo,
                "telefono": body.telefono,
                "password_hash": hash_password(body.clave),
                "roles": ["cliente"],
                "estado": "pendiente_perfil",
                "created_at": datetime.now(timezone.utc),
            }

            try:
                collection.insert_one(nuevo_usuario)
            except DuplicateKeyError:
                raise HTTPException(
                    status_code=409,
                    detail="El correo ya está registrado",
                )

        else:
            # Permitir reintentos de registros incompletos
            if (
                usuario.get("estado") != "pendiente_perfil"
                or not verify_password(
                    body.clave,
                    usuario.get("password_hash", ""),
                )
                or usuario.get("nombre") != nombre
                or usuario.get("telefono") != body.telefono
            ):
                raise HTTPException(
                    status_code=409,
                    detail="El correo ya está registrado",
                )

            user_id = usuario["user_id"]

    except PyMongoError as exc:
        raise HTTPException(
            status_code=503,
            detail="Base de datos no disponible",
        ) from exc

    # Crear el perfil en Clients Service
    try:
        crear_perfil_cliente(
            user_id=user_id,
            nombre=nombre,
            correo=correo,
            telefono=body.telefono,
        )

    except ClientsServiceError as exc:
        raise HTTPException(
            status_code=503,
            detail="Registro pendiente: no se pudo crear el perfil",
        ) from exc

    # Activar la cuenta después de confirmar el perfil
    try:
        resultado = collection.update_one(
            {
                "user_id": user_id,
                "estado": "pendiente_perfil",
            },
            {
                "$set": {
                    "estado": "activo",
                }
            },
        )

        if resultado.matched_count != 1:
            raise HTTPException(
                status_code=503,
                detail="No fue posible activar la cuenta",
            )

    except PyMongoError as exc:
        raise HTTPException(
            status_code=503,
            detail="No fue posible actualizar la identidad",
        ) from exc

    return {
        "clienteId": user_id,
        "correo": correo,
        "rol": "cliente",
    }

    return {"message": "Sesión cerrada"}