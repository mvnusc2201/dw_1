import os
import secrets

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Depends


load_dotenv()

app = FastAPI(
    title="Backend API Semana 9",
    description="Backend protegido por API Gateway"
)


INTERNAL_GATEWAY_SECRET = os.getenv(
    "INTERNAL_GATEWAY_SECRET"
)

if not INTERNAL_GATEWAY_SECRET:
    raise RuntimeError(
        "INTERNAL_GATEWAY_SECRET no esta configurado"
    )


PRODUCTS = [
    {"id": 1, "name": "Completo Italiano", "price": 3200},
    {"id": 2, "name": "Completo Dinamico", "price": 3500},
    {"id": 3, "name": "Completo Mexicano", "price": 3800},
    {"id": 4, "name": "Papas Fritas", "price": 2500},
    {"id": 5, "name": "Bebida 350 ml", "price": 1500},
]


ORDERS = [
    {
        "id": 1001,
        "status": "paid"
    },
    {
        "id": 1002,
        "status": "pending"
    },
    {
        "id": 1003,
        "status": "pending"
    }
]


def verify_gateway(
    x_gateway_secret: str = Header(default="")
):
    valid = secrets.compare_digest(
        x_gateway_secret,
        INTERNAL_GATEWAY_SECRET
    )

    if not valid:
        raise HTTPException(
            status_code=403,
            detail="Solicitud no autorizada desde Gateway"
        )


@app.get("/health")
def health():
    return {
        "status": "OK",
        "service": "Backend API"
    }


@app.get(
    "/products",
    dependencies=[Depends(verify_gateway)]
)
def get_products(
    x_authenticated_user: str = Header(default=""),
    x_authenticated_username: str = Header(default=""),
    x_authenticated_roles: str = Header(default="")
):
    return {
        "authenticated_user": {
            "user_id": x_authenticated_user,
            "username": x_authenticated_username,
            "roles": x_authenticated_roles.split(",")
            if x_authenticated_roles
            else []
        },
        "products": PRODUCTS
    }


@app.get(
    "/orders",
    dependencies=[Depends(verify_gateway)]
)
def get_orders(
    x_authenticated_user: str = Header(default=""),
    x_authenticated_username: str = Header(default=""),
    x_authenticated_roles: str = Header(default="")
):
    return {
        "authenticated_user": {
            "user_id": x_authenticated_user,
            "username": x_authenticated_username,
            "roles": x_authenticated_roles.split(",")
            if x_authenticated_roles
            else []
        },
        "orders": ORDERS
    }


@app.delete(
    "/products/{product_id}",
    dependencies=[Depends(verify_gateway)]
)
def delete_product(
    product_id: int,
    x_authenticated_user: str = Header(default=""),
    x_authenticated_username: str = Header(default=""),
    x_authenticated_roles: str = Header(default="")
):
    roles = (
        x_authenticated_roles.split(",")
        if x_authenticated_roles
        else []
    )

    if "admin" not in roles:
        raise HTTPException(
            status_code=403,
            detail="Se requiere rol administrador"
        )

    product = next(
        (
            item
            for item in PRODUCTS
            if item["id"] == product_id
        ),
        None
    )

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado"
        )

    PRODUCTS.remove(product)

    return {
        "message": "Producto eliminado correctamente",
        "deleted_product": product,
        "authenticated_user": {
            "user_id": x_authenticated_user,
            "username": x_authenticated_username,
            "roles": roles
        }
    }