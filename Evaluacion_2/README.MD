# Doggy's — Evaluación 2

## 1. Descripción del proyecto

Doggy's es una aplicación web de pedidos de comida rápida que desarrollamos utilizando una arquitectura basada en microservicios.

La idea del proyecto es separar las distintas funciones del sistema para que cada servicio tenga una responsabilidad específica. De esta manera, la autenticación, los clientes, el inventario, los pedidos y los pagos pueden trabajar de forma independiente, pero comunicándose entre sí cuando sea necesario.

Para conectar estos componentes utilizamos un **API Gateway**, que actúa como punto de entrada para las solicitudes del frontend. También incorporamos **GraphQL** para obtener información de pedidos y productos mediante una sola consulta.

El proyecto cuenta con un frontend responsive que permite navegar por el catálogo, iniciar sesión, administrar un carrito y registrar pedidos utilizando los servicios del backend.

## 2. Tecnologías utilizadas

| Tecnología | Uso dentro del proyecto |
|---|---|
| Python 3.13 | Desarrollo de los servicios |
| FastAPI | Creación de las APIs REST |
| MongoDB | Almacenamiento de usuarios, productos, pedidos y pagos |
| PyMongo | Conexión entre Python y MongoDB |
| HTTPX | Comunicación HTTP entre microservicios |
| Strawberry GraphQL | Consultas que combinan información de distintos servicios |
| HTML, CSS y JavaScript | Interfaz web y funcionalidades del frontend |
| Tailwind CSS | Estilos y componentes responsivos |
| Argon2 | Almacenamiento seguro de contraseñas |
| Pytest | Pruebas del proyecto |

## 3. Arquitectura del sistema

Decidimos dividir el backend en servicios independientes, en lugar de concentrar toda la lógica en una sola aplicación.

La comunicación principal sigue esta estructura:

```text
                  FRONTEND DOGGY'S
                 HTML / CSS / JS
                        |
                        v
                 API GATEWAY
                   Puerto 8000
                        |
          +-------------+-------------+
          |             |             |
          v             v             v
     AUTH SERVICE   INVENTORY       ORDERS
       (8100)        (9102)         (9103)
          |             |             |
          v             |             v
    CLIENTS (8101)      |         PAYMENTS
          |             |          (9104)
          +-------------+-------------+
                        |
                      MongoDB

       GraphQL Gateway (9105)
       Consulta Orders + Inventory
```

El API Gateway recibe las peticiones externas, comprueba la sesión cuando corresponde y reenvía las solicitudes a los servicios internos.

### Servicios y responsabilidades

| Servicio | Puerto | Función |
|---|---|---|
| API Gateway | 8000 | Entrada principal, validación de sesión y comunicación con los servicios |
| Auth Service | 8100 | Registro, inicio y cierre de sesión |
| Clients Service | 8101 | Almacenamiento de información de clientes |
| Inventory Service | 9102 | Gestión y consulta de productos |
| Orders Service | 9103 | Creación y seguimiento de pedidos |
| Payments Service | 9104 | Registro de pagos pendientes |
| GraphQL Gateway | 9105 | Consulta combinada de pedidos y productos |
| MongoDB | 27017 | Persistencia de datos |

## 4. Funcionalidades desarrolladas

### 4.1. Registro e inicio de sesión

El módulo de autenticación permite crear cuentas, iniciar sesión y cerrar sesión.

Cuando un usuario se registra, Auth Service valida los datos y almacena sus credenciales. Las contraseñas no se guardan en texto plano, sino mediante **Argon2**.

Además, el sistema se comunica con Clients Service para crear el perfil del cliente.

Para mantener la sesión utilizamos una cookie `HttpOnly` llamada `session_token`. El frontend no necesita acceder directamente al contenido de esta cookie, ya que el navegador la envía al realizar las solicitudes correspondientes.

También incorporamos validaciones de entrada y un límite de intentos fallidos de inicio de sesión.

**Rutas principales:**

```http
POST /auth/register
POST /auth/login
GET  /auth/me
POST /auth/logout
```

### 4.2. Inventario de productos

Inventory Service se encarga de almacenar y consultar los productos disponibles.

Cada producto cuenta con información como:

- Identificador.
- Nombre y descripción.
- Precio.
- Stock.
- Disponibilidad.

El frontend obtiene los productos mediante el API Gateway, evitando conectarse directamente a la base de datos.

Por ejemplo:

```http
GET /api/v1/products
```

Durante las pruebas utilizamos un catálogo con **11 productos registrados en MongoDB**, incluidos los productos utilizados por el frontend de Doggy's.

### 4.3. Pedidos

Orders Service permite registrar pedidos asociados a usuarios autenticados.

Para crear un pedido se utiliza el identificador real del producto y la cantidad solicitada. El precio se obtiene desde Inventory Service, en lugar de confiar en el valor que envía el navegador.

Esto permite mantener una separación entre la información visual del carrito y los datos utilizados por el backend.

**Rutas:**

```http
GET  /api/v1/orders
POST /api/v1/orders
```

En el Gateway se verifica la identidad del usuario para consultar y registrar pedidos.

### 4.4. Pagos

Payments Service registra los pagos asociados a pedidos existentes.

Al crear un pago, el servicio consulta Orders para obtener el monto correspondiente. El registro se almacena inicialmente con el estado `pendiente`.

También incorporamos un índice único en MongoDB para evitar que un mismo pedido tenga varios registros de pago.

**Ruta principal:**

```http
POST /api/v1/payments
```

En esta evaluación los pagos son **simulados**. No se realizan transacciones bancarias ni cobros reales.

### 4.5. GraphQL

Implementamos GraphQL para consultar información que proviene de más de un servicio.

La consulta `resumenPedido` obtiene primero los datos del pedido desde Orders Service y después consulta Inventory Service para recuperar la información del producto asociado.

De esta manera, el cliente recibe una respuesta combinada sin realizar ambas consultas por separado.

Ejemplo:

```graphql
query {
  resumenPedido(pedidoId: "ID_DEL_PEDIDO") {
    pedidoId
    estado
    cantidad
    total
    producto {
      nombre
      precio
      disponible
    }
  }
}
```

Esta consulta se realiza mediante:

```http
POST /graphql
```

El acceso desde el API Gateway requiere una sesión válida.

## 5. Frontend

El frontend está desarrollado utilizando HTML, CSS y JavaScript, con un diseño adaptable a distintos tamaños de pantalla.

Incluye una página principal con las secciones comerciales de Doggy's, un catálogo de productos, formularios de cuenta y un carrito de compras.

Entre las funcionalidades trabajadas se encuentran:

- Navegación entre páginas.
- Registro e inicio de sesión.
- Consulta del catálogo.
- Agregar y eliminar productos del carrito.
- Actualización del contador y del total.
- Almacenamiento del carrito mediante `localStorage`.
- Registro de pedidos utilizando el API Gateway.

El frontend se sirve desde el mismo Gateway para facilitar la comunicación con el backend y el manejo de las cookies de sesión.

La pantalla de Centro de Operaciones también está incluida como parte visual del proyecto, pero no constituye un módulo administrativo completamente implementado.

## 6. Instalación y ejecución

### Requisitos

Para ejecutar el proyecto localmente necesitamos:

- Python 3.13.
- MongoDB instalado y en ejecución.
- Las dependencias indicadas en `requirements.txt`.
- Variables de entorno para las claves internas.
- Un navegador web.

Durante el desarrollo trabajamos con MongoDB ejecutándose localmente en Windows, sin depender de un contenedor Docker.

### 6.1. Preparar el entorno virtual

Desde PowerShell, entrar a la carpeta `Evaluacion_2`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 6.2. Configurar la comunicación interna

Algunos servicios necesitan compartir claves internas para aceptar solicitudes.

Las variables utilizadas son:

| Variable | Uso |
|---|---|
| `CLIENTS_INTERNAL_KEY` | Comunicación protegida con Clients Service |
| `PAYMENTS_INTERNAL_KEY` | Acceso interno a Payments Service |
| `GRAPHQL_INTERNAL_KEY` | Comunicación entre API Gateway y GraphQL |

Estas claves deben configurarse antes de iniciar los servicios correspondientes.

Por ejemplo, en PowerShell:

```powershell
$env:PAYMENTS_INTERNAL_KEY = "CLAVE_PRIVADA_CONFIGURADA"
```

Se debe utilizar el mismo valor en el servicio que valida la clave y en el componente autorizado que lo consume.

**Importante:** los valores reales de las claves no se incluyen en GitHub. Tampoco deben publicarse archivos `.env`, sesiones o credenciales.

### 6.3. Iniciar MongoDB

Comprobar que MongoDB esté funcionando en:

```text
mongodb://127.0.0.1:27017/
```

### 6.4. Iniciar los microservicios

Cada servicio debe ejecutarse en una terminal independiente, con sus variables de entorno previamente configuradas.

**Auth Service:**

```powershell
python -m uvicorn auth_service.main:app --host 127.0.0.1 --port 8100
```

**Clients Service:**

```powershell
python -m uvicorn services.clients.main:app --host 127.0.0.1 --port 8101
```

**Inventory Service:**

```powershell
python -m uvicorn services.inventory.main:app --host 127.0.0.1 --port 9102
```

**Orders Service:**

```powershell
python -m uvicorn services.orders.main:app --host 127.0.0.1 --port 9103
```

**Payments Service:**

```powershell
python -m uvicorn services.payments.main:app --host 127.0.0.1 --port 9104
```

**GraphQL Gateway:**

```powershell
python -m uvicorn graphql_gateway.main:app --host 127.0.0.1 --port 9105
```

**API Gateway:**

```powershell
python -m uvicorn api_gateway.main:app --host 127.0.0.1 --port 8000
```

Una vez iniciados los servicios, se puede acceder a la aplicación desde:

```text
http://127.0.0.1:8000/
```

Para revisar los endpoints del Gateway:

```text
http://127.0.0.1:8000/docs
```

Recomendamos utilizar siempre `127.0.0.1` durante las pruebas para evitar problemas con las cookies al alternar entre esa dirección y `localhost`.

## 7. Flujo general de una compra

El funcionamiento principal del sistema se puede resumir en los siguientes pasos:

1. El usuario crea una cuenta o inicia sesión.
2. Auth Service valida sus credenciales.
3. El frontend consulta los productos disponibles.
4. El usuario agrega productos al carrito.
5. Al confirmar, el Gateway valida la sesión.
6. Orders Service registra el pedido utilizando la información del inventario.
7. Payments Service puede registrar un pago asociado al pedido.
8. MongoDB mantiene los registros correspondientes.

Este flujo nos permitió probar la comunicación real entre varios microservicios utilizando datos persistentes.

## 8. Pruebas realizadas

Para comprobar la integración desarrollamos el archivo:

```text
tests/smoke_entrega.py
```

Se ejecuta desde la carpeta `Evaluacion_2` mediante:

```powershell
.\.venv\Scripts\python.exe .\tests\smoke_entrega.py
```

El script verifica:

- Disponibilidad de los servicios.
- Protección de rutas que requieren autenticación.
- Inicio de sesión.
- Consulta del catálogo.
- Consulta de pedidos asociados al usuario.
- Respuesta de GraphQL.
- Cierre de sesión.
- Rechazo del acceso después del logout.

### Resultado obtenido

Durante las pruebas de integración obtuvimos:

| Prueba | Resultado |
|---|---|
| API Gateway | HTTP 200 |
| Inventory Service | HTTP 200 |
| Orders Service | HTTP 200 |
| Payments Service | HTTP 200 |
| GraphQL Gateway | HTTP 200 |
| Rutas protegidas sin sesión | HTTP 401 |
| Inicio de sesión | HTTP 200 |
| Catálogo | 11 productos |
| Consulta GraphQL | HTTP 200 |
| Cierre de sesión | HTTP 200 |
| Acceso después de logout | HTTP 401 |

La ejecución finalizó con:

```text
PRUEBAS DE INTEGRACIÓN OK
```

También comprobamos de manera independiente la creación de pedidos, la persistencia de pagos pendientes en MongoDB y el rechazo de solicitudes directas a Payments Service cuando no se proporciona la clave interna.

## 9. Seguridad implementada

Durante el desarrollo incorporamos distintas medidas para proteger las funcionalidades principales.

Entre ellas:

- Contraseñas almacenadas mediante Argon2.
- Cookies `HttpOnly` para manejar sesiones.
- Validación de datos recibidos.
- Protección de endpoints mediante autenticación.
- Restricción de intentos fallidos de login.
- Claves internas para determinados servicios.
- Restricción de pagos duplicados mediante un índice único en MongoDB.
- Validación de propiedad del pedido en las rutas correspondientes del Gateway.

Estas medidas ayudan a reducir accesos y operaciones no autorizadas, aunque todavía existen aspectos de seguridad que requieren trabajo adicional.

## 10. Limitaciones del proyecto

Doggy's es un prototipo desarrollado con fines académicos.

El sistema permite demostrar la integración entre frontend, API Gateway, microservicios y MongoDB, pero todavía hay mejoras pendientes:

- Los pagos son simulados y no utilizan una pasarela bancaria real.
- Falta reforzar la autorización directamente en todos los microservicios internos.
- Las sesiones se administran en memoria y no mediante almacenamiento distribuido.
- No existe una reserva transaccional de stock para múltiples pedidos simultáneos.
- Es necesario mejorar el tratamiento de errores cuando una operación entre servicios se completa parcialmente.
- Algunas secciones comerciales del frontend son informativas y todavía no cuentan con servicios propios.

Estas mejoras serían necesarias antes de utilizar la aplicación en un entorno productivo.

## 11. Documentación y evidencias

Dentro de la carpeta `docs/` se encuentran los documentos del proyecto, incluyendo los módulos de arquitectura, integración, seguridad y diagramas UML.

Las capturas de ejecución se almacenan en:

```text
docs/evidencias/
```

Allí se incluyen evidencias de:

- Inicio de sesión.
- API Gateway.
- Inventario y pedidos en MongoDB.
- Pagos pendientes.
- Consultas GraphQL.
- Controles de seguridad.
- Ejecución de las pruebas de integración.
- Funcionamiento del frontend.

## 12. Conclusión

Con esta evaluación logramos integrar distintas partes del sistema que inicialmente trabajaban de manera separada.

Uno de los principales desafíos fue coordinar la comunicación entre los servicios, especialmente durante el registro de usuarios, la creación de pedidos y la validación de pagos. También tuvimos que ajustar varias rutas del API Gateway y comprobar que los datos realmente se almacenaran en MongoDB.

Las pruebas nos permitieron verificar que el flujo principal funciona y que los servicios pueden comunicarse correctamente.

Como resultado, contamos con una base funcional de Doggy's, con una estructura que permite seguir agregando funcionalidades y mejorando la seguridad sin concentrar toda la aplicación en un único servicio.
