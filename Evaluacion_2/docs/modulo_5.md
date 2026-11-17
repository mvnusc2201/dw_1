# Módulo 5 — Estructura del API Gateway

**Proyecto:** Doggy's · **Caso 19**

## 1. Propósito

Utilizar **un único API Gateway FastAPI** como punto de entrada del frontend. Así se centralizan la validación de sesión, el enrutamiento, los errores de conexión y la protección de recursos privados.

## 2. Componentes principales

| Componente | Responsabilidad |
|---|---|
| `FastAPI app` | Publicar rutas HTTP y servir el frontend estático |
| `GraphQLRequest` | Validar la estructura de una consulta GraphQL |
| `CrearPedidoRequest` | Validar `producto_id` y cantidad |
| `CrearPagoRequest` | Validar el identificador del pedido |
| `AuthContext` y `require_auth` | Obtener identidad y roles desde Auth Service |
| `httpx.AsyncClient` | Comunicar el Gateway con los microservicios |

## 3. Flujo de una solicitud

```text
Navegador
   |
   v
API Gateway (8000)
   |-- /auth/* ----------> Auth (8100) ---> Clients (8101)
   |-- /api/v1/products -> Inventory (9102)
   |-- /api/v1/orders --> Orders (9103)
   |-- /api/v1/payments -> Payments (9104)
   `-- /graphql --------> GraphQL (9105)
                                |-- Orders
                                `-- Inventory
```

Las rutas protegidas verifican la sesión antes de consultar otros sistemas. Los servicios comerciales utilizan MongoDB; el Gateway **no modifica directamente sus colecciones**.

## 4. Fronteras de confianza

- El navegador solo envía datos de la solicitud y la cookie de sesión; no crea su propia identidad autorizada.
- Auth Service verifica la sesión y entrega el contexto autenticado.
- Los servicios dueños de los datos validan reglas de negocio y, donde corresponde, propiedad del recurso.
- Payments y GraphQL exigen una clave de servicio para las rutas internas protegidas.

## 5. Diseño y brechas

El diagrama detallado de clases y políticas se conserva en `docs/uml-gateway-politicas.puml` cuando ese archivo forme parte de la entrega. Queda por reforzar la autenticación entre **todos** los servicios y la gestión de errores de operaciones distribuidas.
