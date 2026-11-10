# Módulo 1 — Servicios derivados del frontend

**Proyecto:** Doggy's · **Caso 19** · **Equipo:** Cristopher y Manuel

## 1. Objetivo y alcance

Identificar las operaciones necesarias para que Doggy's permita consultar productos, registrar clientes y realizar pedidos. El análisis original contempla **37 servicios (S01–S37)** para tienda, carrito, checkout, seguimiento, operación y administración. La entrega implementa un **subconjunto funcional**; los restantes corresponden a ampliaciones previstas.

## 2. Pantallas y servicios principales

| Pantalla | Acción del usuario | Endpoint implementado | Sistema |
|---|---|---|---|
| Mi cuenta | Registrarse | `POST /auth/register` | Auth + Clients |
| Mi cuenta | Iniciar/cerrar sesión | `POST /auth/login`, `POST /auth/logout` | Auth |
| Mi cuenta | Consultar sesión | `GET /auth/me` | Auth |
| Catálogo | Consultar productos | `GET /api/v1/products` | Inventory |
| Carrito | Agregar/eliminar ítems | JavaScript + `localStorage` | Navegador |
| Checkout | Crear pedido | `POST /api/v1/orders` | Orders |
| Mis pedidos | Consultar pedidos propios | `GET /api/v1/orders` | Orders |
| Checkout | Registrar pago pendiente | `POST /api/v1/payments` | Payments |
| Consulta agregada | Consultar pedido y producto | `POST /graphql` | GraphQL + Orders + Inventory |

## 3. Contratos de ejemplo

**Crear pedido:**

```http
POST /api/v1/orders
Content-Type: application/json
Cookie: session_token=...
```

```json
{"producto_id": "<id_de_mongodb>", "cantidad": 1}
```

**Registrar pago pendiente:**

```json
{"pedido_id": "<id_del_pedido>"}
```

El servidor obtiene la identidad desde la sesión y calcula el monto usando los datos del pedido; **no confía en un precio enviado por el frontend**. La operación de Payments registra un estado `pendiente`, sin realizar cobros bancarios.

## 4. Reglas y validaciones

- `200/201`: consulta o creación exitosa; `401`: sin sesión; `403`: sin autorización; `409`: conflicto, como pago duplicado; `422`: datos incorrectos.
- Los productos públicos muestran nombre, descripción, precio y disponibilidad.
- Los pedidos y pagos requieren sesión; el cliente no debe acceder a pedidos ajenos.
- La contraseña no se devuelve al frontend y la sesión se conserva mediante cookie `HttpOnly`.

## 5. Alcance pendiente

El diseño original también considera recuperación de clave, direcciones de despacho, seguimiento detallado, roles operativos, administración y reportes. Esas capacidades **no se declaran implementadas** en este prototipo. La cobertura de reparto de 3 km en Maipú pertenece al caso de estudio, pero su validación geográfica no está demostrada.
