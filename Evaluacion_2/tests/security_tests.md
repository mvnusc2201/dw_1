# Pruebas de seguridad - Módulo 7

## Caso 1 - Acceso anónimo al catálogo

### Objetivo

Comprobar que el catálogo público puede consultarse sin exponer datos personales ni secretos.

### Solicitud

GET /api/productos

### Resultado esperado

200 OK

### Validación

La respuesta debe contener únicamente información de catálogo permitida, por ejemplo:

- id
- nombre
- descripción
- precio
- disponibilidad

No debe incluir:

- datos personales de clientes;
- secretos de integración;
- credenciales;
- tokens.

---

## Caso 2 - Operación protegida sin sesión válida

### Objetivo

Comprobar que una ruta protegida no permite acceso sin autenticación.

### Solicitud

GET /api/pedidos/{pedido_id}

sin cookie o token de sesión válido.

### Resultado esperado

401 Unauthorized

### Validación

El sistema no debe devolver información del pedido.

---

## Caso 3 - Operación administrativa con rol sin permiso

### Objetivo

Comprobar que un usuario autenticado sin rol administrativo no pueda ejecutar operaciones de administración.

### Solicitud

DELETE /api/productos/{producto_id}

Usuario autenticado con rol:

user

### Resultado esperado

403 Forbidden

### Validación

El producto debe seguir existiendo.

---

## Caso 4 - Consulta de pedido ajeno

### Objetivo

Comprobar autorización por propiedad del recurso.

### Escenario

Usuario A intenta consultar un pedido perteneciente a Usuario B.

### Solicitud

GET /api/pedidos/{pedido_id}

### Resultado esperado

403 Forbidden

### Validación

El sistema no debe devolver:

- cliente_id;
- productos;
- total;
- dirección;
- estado;
- información de pago.

---

## Caso 5 - Acceso directo al backend privado

### Objetivo

Comprobar que los servicios internos no acepten solicitudes externas sin identidad técnica autorizada.

### Solicitud

GET http://127.0.0.1:9103/pedidos

sin credencial interna válida.

### Resultado esperado

403 Forbidden

### Validación

El backend debe rechazar la solicitud directa.

---

## Caso 6 - Manipulación del precio desde frontend

### Objetivo

Comprobar que el navegador no pueda determinar el precio real del pedido.

### Datos manipulados enviados por el cliente

{
  "producto_id": "PRODUCTO_REAL",
  "cantidad": 2,
  "precio": 1,
  "total": 2
}

### Resultado esperado

El servidor debe ignorar precio y total enviados por el navegador.

Orders debe consultar Inventory y calcular:

precio_oficial × cantidad

### Validación

El total almacenado debe coincidir con el precio oficial de Inventory.

---

## Caso 7 - Manipulación de pago

### Objetivo

Comprobar que el frontend no pueda declarar un pedido como pagado.

### Solicitud manipulada

{
  "pedido_id": "PEDIDO_REAL",
  "monto": 1,
  "estado": "pagado"
}

### Resultado esperado

Payments debe obtener el monto desde Orders.

El estado inicial debe ser:

pendiente

La confirmación debe realizarse mediante el flujo autorizado del servicio de pagos.

---

## Caso 8 - Pago duplicado

### Objetivo

Evitar procesar dos veces la misma confirmación.

### Secuencia

1. Confirmar un pago válido.
2. Volver a confirmar el mismo pago.

### Resultado esperado

Primera solicitud:

200 OK

Segunda solicitud:

409 Conflict

### Validación

El pedido no debe recibir efectos duplicados.

---

# Evidencias

Para cada prueba se debe registrar:

- fecha;
- endpoint;
- usuario o identidad utilizada;
- entrada;
- código HTTP obtenido;
- respuesta;
- captura o salida de terminal;
- resultado: aprobado / rechazado.

# Resultados ejecutados

## Prueba de manipulación de precio

Resultado: APROBADA.

Se envió un pedido incluyendo valores manipulados de `precio` y `total`.

El servicio `orders` ignoró dichos valores y calculó el total utilizando el precio oficial obtenido desde `inventory`.

Esto demuestra que el navegador no es autoridad sobre precios ni totales.

---

## Prueba de manipulación de pago

Resultado: APROBADA.

Se intentó crear un pago enviando manualmente un monto alterado y estado `pagado`.

El servicio `payments` obtuvo el monto oficial desde `orders` y creó el pago con estado inicial `pendiente`.

El frontend no pudo declarar directamente un pedido como pagado.

---

## Prueba de pago duplicado

Resultado: APROBADA.

La primera confirmación del pago fue aceptada.

Una segunda confirmación del mismo pago fue rechazada con:

409 Conflict

Esto evita procesar dos veces una misma confirmación.