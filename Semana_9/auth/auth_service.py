import os
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
from dotenv import load_dotenv


load_dotenv()

app = FastAPI(
    title="Auth Service",
    description="Servicio de autenticacion, sesiones, introspection y logout"
)


AUTH_INTROSPECTION_SECRET = os.getenv(
    "AUTH_INTROSPECTION_SECRET"
)

if not AUTH_INTROSPECTION_SECRET:
    raise RuntimeError(
        "AUTH_INTROSPECTION_SECRET no esta configurado"
    )


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenRequest(BaseModel):
    token: str


USERS = {
    "ana": {
        "user_id": "USR-001",
        "password": "1234",
        "roles": ["user"]
    },
    "ernesto": {
        "user_id": "USR-003",
        "password": "admin123",
        "roles": ["user", "admin"]
    }
}


SESSIONS = {}


def verify_gateway(
    x_auth_secret: str = Header(default="")
):
    valid = secrets.compare_digest(
        x_auth_secret,
        AUTH_INTROSPECTION_SECRET
    )

    if not valid:
        raise HTTPException(
            status_code=403,
            detail="Gateway no autorizado"
        )


@app.get("/health")
def health():
    return {
        "status": "OK",
        "service": "Auth Service"
    }


@app.post("/login")
def login(data: LoginRequest):

    user = USERS.get(data.username)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Credenciales incorrectas"
        )

    if data.password != user["password"]:
        raise HTTPException(
            status_code=401,
            detail="Credenciales incorrectas"
        )

    token = secrets.token_urlsafe(32)

    expires_at = (
        datetime.now(timezone.utc)
        + timedelta(minutes=15)
    )

    SESSIONS[token] = {
        "user_id": user["user_id"],
        "username": data.username,
        "roles": user["roles"],
        "expires_at": expires_at
    }

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": 900
    }


@app.post(
    "/introspect",
    dependencies=[Depends(verify_gateway)]
)
def introspect(data: TokenRequest):

    session = SESSIONS.get(data.token)

    if not session:
        return {
            "active": False
        }

    if datetime.now(timezone.utc) >= session["expires_at"]:

        del SESSIONS[data.token]

        return {
            "active": False
        }

    return {
        "active": True,
        "user_id": session["user_id"],
        "username": session["username"],
        "roles": session["roles"]
    }


@app.post(
    "/logout",
    dependencies=[Depends(verify_gateway)]
)
def logout(data: TokenRequest):

    if data.token in SESSIONS:
        del SESSIONS[data.token]

    return {
        "message": "Sesion cerrada correctamente"
    }