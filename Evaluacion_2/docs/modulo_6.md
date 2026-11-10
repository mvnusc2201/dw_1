# Módulo 6 — Rutas y secretos de integración

**Proyecto:** Doggy's · **Caso 19**

## 1. Objetivo

Documentar las rutas que atraviesan el Gateway y separar las **credenciales del cliente** de las **claves privadas entre servicios**. Ninguna clave interna debe enviarse al navegador.

## 2. Matriz de integración implementada

| Ruta externa | Destino interno | Acceso | Control principal |
|---|---|---|---|
| `POST /auth/register` | Auth → Clients | Público | Validación de datos y registro de identidad |
| `POST /auth/login` | Auth | Público | Credenciales y límite de intentos |
| `GET /auth/me` | Auth | Autenticado | Cookie de sesión |
| `GET /api/v1/products` | Inventory `GET /productos` | Público | Datos públicos del catálogo |
| `GET/POST /api/v1/orders` | Orders `/pedidos` | Autenticado | Usuario y propiedad del pedido |
| `POST /api/v1/payments` | Payments `POST /pagos` | Autenticado | Propiedad, monto y clave interna |
| `POST /graphql` | GraphQL `/graphql` | Autenticado | Sesión, clave interna y propiedad |

## 3. Secretos y configuración

| Variable o referencia | Uso | Dónde se configura |
|---|---|---|
| `CLIENTS_INTERNAL_KEY` | Auth → Clients | Variable de entorno compartida entre esos servicios |
| `PAYMENTS_INTERNAL_KEY` | Gateway → Payments | Variable de entorno; clave local excluida de Git |
| `GRAPHQL_INTERNAL_KEY` | Gateway → GraphQL | Variable de entorno; clave local excluida de Git |
| `AUTH_SERVICE_URL`, `ORDERS_SERVICE_URL`, etc. | Direcciones internas | Variables de entorno, sin secretos |
| `session_token` | Sesión de usuario | Cookie `HttpOnly`; no es una API key interna |

**Buenas prácticas:** no publicar claves en Git, capturas o logs; cambiarlas ante una filtración; utilizar claves distintas por destino; desplegar con HTTPS y una red interna cerrada.

## 4. Estado y riesgos

Se verificó que Payments sin clave respondiera `403`, y el Gateway sin sesión, `401`. GraphQL también cuenta con clave de integración. La autenticación de **Orders e Inventory** debe reforzarse antes de producción. No se afirma que exista Vault, mTLS ni un proveedor de pago real en el entorno académico.
