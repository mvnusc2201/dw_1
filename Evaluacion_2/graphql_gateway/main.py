import httpx
import strawberry
import os
import secrets

from graphql import GraphQLError
from strawberry.types import Info
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter


ORDERS_URL = "http://127.0.0.1:9103"
INVENTORY_URL = "http://127.0.0.1:9102"


@strawberry.type
class Producto:
    id: str
    nombre: str
    descripcion: str | None
    precio: int
    stock: int
    disponible: bool


@strawberry.type
class Pedido:
    id: str
    cliente_id: str
    producto_id: str
    cantidad: int
    estado: str
    total: int


@strawberry.type
class ResumenPedido:
    pedido_id: str
    cliente_id: str
    cantidad: int
    estado: str
    total: int
    producto: Producto



@strawberry.type
class Query:

    @strawberry.field
    async def resumen_pedido(
        self,
        info: Info,
        pedido_id: str
    ) -> ResumenPedido:

        # Verificar que la petición venga del API Gateway.
        request = info.context["request"]

        clave_esperada = os.getenv("GRAPHQL_INTERNAL_KEY", "")
        clave_recibida = request.headers.get("X-Internal-Key", "")

        if (
            not clave_esperada
            or not secrets.compare_digest(
                clave_recibida,
                clave_esperada
            )
        ):
            raise GraphQLError("Acceso interno no autorizado")

        usuario_id = request.headers.get(
            "X-Authenticated-User", ""
        )

        if not usuario_id:
            raise GraphQLError("Usuario no autenticado")

        async with httpx.AsyncClient(timeout=5.0) as client:

            pedido_response = await client.get(
                f"{ORDERS_URL}/pedidos/{pedido_id}"
            )

            if pedido_response.status_code != 200:
                raise GraphQLError("Pedido no encontrado")

            pedido = pedido_response.json()

            # El cliente solo consulta sus propios pedidos.
            if pedido.get("cliente_id") != usuario_id:
                raise GraphQLError("Acceso denegado al pedido")

            producto_response = await client.get(
                f"{INVENTORY_URL}/productos/{pedido['producto_id']}"
            )

            if producto_response.status_code != 200:
                raise GraphQLError("Producto no encontrado")

            producto = producto_response.json()

        return ResumenPedido(
            pedido_id=pedido["id"],
            cliente_id=pedido["cliente_id"],
            cantidad=pedido["cantidad"],
            estado=pedido["estado"],
            total=pedido["total"],
            producto=Producto(
                id=producto["id"],
                nombre=producto["nombre"],
                descripcion=producto.get("descripcion"),
                precio=producto["precio"],
                stock=producto["stock"],
                disponible=producto["disponible"]
            )
        )


schema = strawberry.Schema(
    query=Query
)

graphql_app = GraphQLRouter(
    schema
)

app = FastAPI(
    title="GraphQL Gateway"
)

app.include_router(
    graphql_app,
    prefix="/graphql"
)


@app.get("/health")
def health():
    return {
        "status": "OK",
        "service": "graphql-gateway"
    }