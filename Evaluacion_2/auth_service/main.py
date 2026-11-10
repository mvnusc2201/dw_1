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

# --------------------------------------------------------------------------
# Configuración
# --------------------------------------------------------------------------
# En producción estos valores vendrían de Vault (p. ej. vault://doggys/auth/...).
COOKIE_NAME = "session_token"
SESSION_TTL_SECONDS = int(os.getenv("SESSION_TTL_SECONDS", "1800"))  # 30 min
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


def _make_user(password: str, roles: list[str]) -> dict:
    salt = os.urandom(16)
    return {"salt": salt, "hash": _hash_password(password, salt), "roles": roles}


USERS_DB: dict[str, dict] = {
    "cliente": _make_user("cliente123", ["cliente"]),
    "operador": _make_user("operador123", ["operador"]),
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
    username: str | None = None
    roles: list[str] = []
    exp: int | None = None


# --------------------------------------------------------------------------
# Lógica
# --------------------------------------------------------------------------


def _authenticate(username: str, password: str) -> dict | None:
    record = USERS_DB.get(username)
    if record is None:
        return None
    candidate = _hash_password(password, record["salt"])
    if hmac.compare_digest(candidate, record["hash"]):
        return record
    return None


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


@app.post("/auth/login")
def login(body: LoginRequest, response: Response):
    user = _authenticate(body.username, body.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    token = secrets.token_urlsafe(32)
    SESSIONS[token] = {
        "username": body.username,
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
        "username": body.username,
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
        username=session["username"],
        roles=session["roles"],
        exp=int(session["exp"]),
    )


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
    return {"message": "Sesión cerrada"}