# Módulo 7 — Datos sensibles y secretos del cliente

**Proyecto:** Doggy's · **Caso 19**

## 1. Clasificación de información

| Información | Clasificación | Tratamiento previsto o implementado |
|---|---|---|
| Nombre, correo y teléfono | Dato personal | Perfil del cliente en MongoDB; acceso restringido |
| Identificador e historial de pedidos | Dato personal/comercial | Orders; consulta de pedidos propios desde el Gateway |
| Catálogo y precios publicados | Público | Consulta sin iniciar sesión |
| Contraseña | Credencial sensible | Auth almacena un **hash Argon2**, no la contraseña legible |
| Cookie `session_token` | Credencial de sesión | `HttpOnly`, vencimiento y revocación al cerrar sesión |
| Claves internas de Payments, Clients y GraphQL | Secreto de servicio | Variables de entorno, excluidas del repositorio |
| Monto y estado del pago | Dato transaccional | Payments obtiene el monto desde Orders; proveedor simulado |

## 2. Recorrido de la contraseña

1. El usuario escribe su contraseña en el formulario de registro o login.
2. El navegador la envía a Auth mediante el API Gateway.
3. Auth valida las credenciales y almacena/verifica un **hash Argon2**.
4. Si el login es correcto, crea una sesión y envía una cookie `HttpOnly`.
5. El Gateway consulta Auth para validar solicitudes privadas; el cierre de sesión revoca la sesión.

La contraseña **no debe** aparecer en respuestas, URL, repositorios, capturas ni registros de actividad.

## 3. Minimización y protección

- No solicitar RUN ni datos de tarjetas bancarias para el prototipo.
- Mostrar solo los campos del cliente necesarios para cada operación.
- Evitar imprimir cookies, cabeceras de autenticación o claves internas en evidencias.
- Calcular precios y pagos en el servidor, nunca confiar en montos de JavaScript.
- Usar HTTPS y cookies con `Secure` en producción; la ejecución local por HTTP es solo de desarrollo.

## 4. Validación y límites conocidos

Las pruebas mostraron `401` para pedidos, pagos y GraphQL sin sesión; `403` para Payments directo sin clave; y acceso válido después del login. **Siguen pendientes** una política completa de retención y eliminación de datos, el endurecimiento de servicios internos y la persistencia compartida de sesiones. No existe cobro con tarjeta real.
