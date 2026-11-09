import httpx
import strawberry

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
        pedido_id: str
    ) -> ResumenPedido:

        async with httpx.AsyncClient() as client:

            pedido_response = await client.get(
                f"{ORDERS_URL}/pedidos/{pedido_id}"
            )

            if pedido_response.status_code != 200:
                raise Exception(
                    "Pedido no encontrado"
                )

            pedido = pedido_response.json()

            producto_response = await client.get(
                f"{INVENTORY_URL}/productos/{pedido['producto_id']}"
            )

            if producto_response.status_code != 200:
                raise Exception(
                    "Producto no encontrado"
                )

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