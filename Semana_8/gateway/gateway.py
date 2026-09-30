import os
import secrets

import httpx

from dotenv import load_dotenv

from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    Request,
    Response
)

from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials
)


load_dotenv()


app = FastAPI(
    title="Secure Local API Gateway",
    description="API Gateway con Vault, Bearer Token y control de permisos"
)


security = HTTPBearer(auto_error=False)


VAULT_ADDR = os.getenv(
    "VAULT_ADDR",
    "http://127.0.0.1:8200"
)

VAULT_TOKEN = os.getenv("VAULT_TOKEN")

BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:9000"
)


if not VAULT_TOKEN:
    raise RuntimeError(
        "VAULT_TOKEN no configurado"
    )


async def get_gateway_secrets():

    url = f"{VAULT_ADDR}/v1/secret/data/gateway"

    headers = {
        "X-Vault-Token": VAULT_TOKEN
    }

    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(
            url,
            headers=headers
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=500,
            detail="No fue posible acceder a Vault"
        )

    vault_response = response.json()

    return vault_response["data"]["data"]


async def authenticate_client(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Bearer token requerido"
        )

    vault_secrets = await get_gateway_secrets()

    received_token = credentials.credentials

    user_token = vault_secrets["user_token"]
    admin_token = vault_secrets["admin_token"]


    if secrets.compare_digest(
        received_token,
        user_token
    ):
        return {
            "client_id": "usuario",
            "role": "user",
            "scopes": vault_secrets[
                "user_scopes"
            ].split(","),
            "backend_secret": vault_secrets[
                "backend_shared_secret"
            ]
        }


    if secrets.compare_digest(
        received_token,
        admin_token
    ):
        return {
            "client_id": "administrador",
            "role": "admin",
            "scopes": vault_secrets[
                "admin_scopes"
            ].split(","),
            "backend_secret": vault_secrets[
                "backend_shared_secret"
            ]
        }


    raise HTTPException(
        status_code=401,
        detail="Token invalido"
    )


@app.get("/health")
def health():

    return {
        "status": "OK",
        "service": "API Gateway"
    }


@app.api_route(
    "/api/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"]
)
async def proxy(
    path: str,
    request: Request,
    auth=Depends(authenticate_client)
):

    target_url = f"{BACKEND_URL}/{path}"


    required_scope = None


    if (
        request.method == "GET"
        and path == "products"
    ):
        required_scope = "products:read"


    elif (
        request.method == "GET"
        and path == "orders"
    ):
        required_scope = "orders:read"


    if (
        required_scope
        and required_scope not in auth["scopes"]
    ):
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos para acceder a este recurso"
        )


    body = await request.body()


    gateway_headers = {
        "X-Gateway-Secret": auth[
            "backend_secret"
        ],
        "X-Authenticated-Client": auth[
            "client_id"
        ]
    }


    content_type = request.headers.get(
        "content-type"
    )

    if content_type:
        gateway_headers[
            "content-type"
        ] = content_type


    try:

        async with httpx.AsyncClient(
            timeout=10.0
        ) as client:

            upstream = await client.request(
                method=request.method,
                url=target_url,
                params=request.query_params,
                content=body,
                headers=gateway_headers
            )


    except httpx.RequestError:

        raise HTTPException(
            status_code=502,
            detail="Backend no disponible"
        )


    response_headers = {}


    if "content-type" in upstream.headers:

        response_headers["content-type"] = (
            upstream.headers["content-type"]
        )


    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers=response_headers
    )