# Módulo 4 — Stakeholders y permisos HTTP

**Proyecto:** Doggy's · **Caso 19**

## 1. Identificación de actores

| Actor | Necesidad | Acceso previsto |
|---|---|---|
| Visitante | Consultar menú y precios | Catálogo público |
| Cliente | Registrarse, comprar y revisar pedidos | Solo sus datos y pedidos |
| Operador | Preparar pedidos y controlar disponibilidad | Pedidos asignados y operación interna |
| Despachos | Coordinar entregas | Datos necesarios para repartir |
| Administrador | Gestionar catálogo y usuarios | Funciones administrativas |
| Dueño | Revisar indicadores comerciales | Reportes agregados, solo lectura |

Los roles de **operador, despachos, administrador y dueño** pertenecen al diseño de permisos; su implementación completa no fue verificada en la versión actual.

## 2. Matriz resumida de permisos

| Operación | Visitante | Cliente autenticado | Personal autorizado (diseño) |
|---|---|---|---|
| `GET /api/v1/products` | Sí | Sí | Sí |
| `POST /auth/register` y `/auth/login` | Sí | Sí | No requiere rol especial |
| `GET /auth/me` | No | Sí | Sí, con sesión |
| `POST /api/v1/orders` | No (`401`) | Sí, pedido propio | Restringido |
| `GET /api/v1/orders` | No (`401`) | Sí, solo propios | Según rol y alcance |
| `POST /api/v1/payments` | No (`401`) | Sí, pedido propio | Restringido |
| `POST /graphql` | No (`401`) | Sí, pedido propio | Según rol y alcance |
| Cambiar productos o confirmar pagos | No | No | Solo personal autorizado; pendiente de endurecer |

## 3. Criterios de autorización

**Autenticación** responde «¿quién eres?»: el API Gateway valida la cookie mediante Auth Service. **Autorización** responde «¿qué puedes hacer?»: se verifica el rol y, para pedidos, la coincidencia entre `cliente_id` e identidad autenticada.

El Gateway construye las cabeceras internas de identidad y no debe aceptar `X-Authenticated-*` suministradas desde el navegador. Los servicios internos también deben aplicar sus controles propios.

## 4. Evidencia y limitaciones

Las pruebas de integración mostraron `401` al llamar sin sesión a pedidos, pagos y GraphQL; además, `/pagos` directo sin clave interna devolvió `403`. Esto demuestra controles concretos, **no una auditoría completa de permisos**, especialmente en Orders e Inventory.
