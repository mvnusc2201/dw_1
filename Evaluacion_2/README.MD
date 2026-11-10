# DoggIs — Evaluación 2

## Descripción del proyecto

Doggy's es una aplicación web de pedidos de comida desarrollada mediante una arquitectura de microservicios.

El sistema integra autenticación de usuarios, gestión de clientes, catálogo de productos, pedidos y registro de pagos pendientes.

La comunicación externa se realiza mediante un API Gateway. Además, GraphQL permite consultar información agregada de pedidos y productos.

## Tecnologías utilizadas

- Python y FastAPI
- MongoDB y PyMongo
- HTTPX para comunicación entre servicios
- Strawberry GraphQL
- HTML, CSS y JavaScript
- Pytest para pruebas automatizadas
- Argon2 para almacenamiento seguro de contraseñas

## Arquitectura

| Componente | Puerto | Responsabilidad |
|---|---|---|
| API Gateway | 8000 | Entrada principal, autenticación y enrutamiento |
| Auth Service | 8100 | Registro, login y sesiones |
| Clients Service | 8101 | Gestión de clientes |
| Inventory Service | 9102 | Catálogo y stock |
| Orders Service | 9103 | Creación y seguimiento de pedidos |
| Payments Service | 9104 | Registro de pagos pendientes |
| GraphQL Gateway | 9105 | Agregación de pedidos y productos |
| MongoDB | 27017 | Persistencia de datos |

## Funcionalidades implementadas

1. Registro de usuarios y creación de perfil de cliente.
2. Inicio de sesión mediante cookies HTTP-only.
3. Almacenamiento de contraseñas mediante Argon2.
4. Consulta de productos desde MongoDB.
5. Creación y consulta de pedidos autenticados.
6. Registro de pagos pendientes asociados a pedidos.
7. Prevención de pagos duplicados mediante un índice único.
8. Consultas GraphQL que integran Orders e Inventory.
9. Protección de rutas del Gateway mediante autenticación.
10. Pruebas de integración del flujo principal.

## Requisitos de ejecución

- Python 3.13
- MongoDB funcionando localmente
- Dependencias Python del proyecto
- Variables de entorno y claves internas configuradas

El archivo `.venv` y las claves privadas no deben incorporarse al repositorio.

## Ejecución

Desde la carpeta raíz del proyecto, activar el entorno virtual:

```powershell
.\.venv\Scripts\Activate.ps1
```

Con MongoDB iniciado, ejecutar los servicios en terminales independientes:

```powershell
python -m uvicorn auth_service.main:app --port 8100
python -m uvicorn services.clients.main:app --port 8101
python -m uvicorn services.inventory.main:app --port 9102
python -m uvicorn services.orders.main:app --port 9103
python -m uvicorn services.payments.main:app --port 9104
python -m uvicorn graphql_gateway.main:app --port 9105
python -m uvicorn api_gateway.main:app --port 8000
```

Antes de iniciar los servicios correspondientes, configurar las variables `CLIENTS_INTERNAL_KEY`, `PAYMENTS_INTERNAL_KEY` y `GRAPHQL_INTERNAL_KEY` con valores consistentes entre los servicios que se comunican.

Las claves de Payments y GraphQL se mantienen en archivos locales excluidos de Git.

Acceder al frontend desde:

`http://127.0.0.1:8000/`

## Endpoints principales

| Método | Endpoint | Descripción |
|---|---|---|
| POST | `/auth/register` | Registrar usuario |
| POST | `/auth/login` | Iniciar sesión |
| GET | `/auth/me` | Consultar sesión |
| POST | `/auth/logout` | Cerrar sesión |
| GET | `/api/v1/products` | Consultar catálogo |
| GET | `/api/v1/orders` | Consultar pedidos propios |
| POST | `/api/v1/orders` | Crear pedido |
| POST | `/api/v1/payments` | Crear pago pendiente |
| POST | `/graphql` | Consultar información agregada |

## Pruebas

Ejecutar desde la raíz del proyecto:

```powershell
.\.venv\Scripts\python.exe .\tests\smoke_entrega.py
```

La prueba verifica:

- Disponibilidad de los servicios.
- Rechazo de solicitudes no autenticadas.
- Inicio de sesión.
- Consulta del catálogo.
- Consulta de pedidos.
- Integración GraphQL.
- Cierre y revocación de sesión.

**Resultado de la ejecución de integración anterior a los últimos cambios de Payments:** pruebas superadas.

## Seguridad

Se implementaron contraseñas con Argon2, sesiones mediante cookies HTTP-only, validación de solicitudes, protección de rutas y claves para comunicaciones internas específicas.

Payments utiliza un índice único por pedido para impedir múltiples registros de pago.

## Limitaciones conocidas

El proveedor de pagos es simulado: el sistema no realiza cobros bancarios reales.

Quedan pendientes el endurecimiento de todos los servicios internos, la persistencia distribuida de sesiones, la gestión robusta de operaciones parcialmente completadas, las reservas transaccionales de stock y la integración visual completa del catálogo con el frontend.

La solución corresponde a un prototipo académico y no debe desplegarse como plataforma de pagos de producción sin completar estas medidas.

## Evidencias de implementación

El proyecto cuenta con pruebas de autenticación, persistencia en MongoDB, consulta de productos, creación de pedidos, registro de pagos pendientes y agregación de servicios mediante GraphQL.