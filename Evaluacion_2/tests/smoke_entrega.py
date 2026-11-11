
import getpass
import httpx

BASE = "http://127.0.0.1:8000"

SERVICIOS = {
    "API Gateway": "http://127.0.0.1:8000/health",
    "Inventory": "http://127.0.0.1:9102/health",
    "Orders": "http://127.0.0.1:9103/health",
    "Payments": "http://127.0.0.1:9104/health",
    "GraphQL": "http://127.0.0.1:9105/health",
}

print("\n=== DOGGY'S - PRUEBAS DE INTEGRACIÓN ===\n")

errores = []

for nombre, url in SERVICIOS.items():
    try:
        r = httpx.get(url, timeout=5)
        print(f"{nombre}: HTTP {r.status_code}")

        if r.status_code != 200:
            errores.append(f"{nombre}: HTTP {r.status_code}")

    except httpx.RequestError:
        print(f"{nombre}: SIN CONEXIÓN")
        errores.append(f"{nombre}: sin conexión")

with httpx.Client(base_url=BASE, timeout=15) as c:
    # Seguridad: rutas privadas sin sesión.
    for ruta, metodo, datos in [
        ("/api/v1/orders", "GET", None),
        ("/api/v1/payments", "POST", {
            "pedido_id": "000000000000000000000001"
        }),
        ("/graphql", "POST", {
            "query": "{ __typename }"
        }),
    ]:
        try:
            r = c.request(metodo, ruta, json=datos)
            print(f"Sin sesión {ruta}: HTTP {r.status_code}")

            if r.status_code != 401:
                errores.append(f"Ruta sin protección: {ruta}")

        except httpx.RequestError as exc:
            errores.append(f"{ruta}: {exc}")

    correo = input("\nCorreo registrado: ").strip()
    clave = getpass.getpass("Contraseña: ")

    login = c.post("/auth/login", json={
        "username": correo,
        "password": clave
    })

    print("LOGIN:", login.status_code)
    if login.status_code != 200:
        errores.append("Login incorrecto")
    else:
        # Catálogo real.
        catalogo = c.get("/api/v1/products")
        print("CATÁLOGO:", catalogo.status_code)

        if catalogo.status_code == 200:
            productos = catalogo.json().get("products", [])
            print("Productos disponibles:", len(productos))

            if not productos:
                errores.append("Catálogo vacío")
        else:
            errores.append("Catálogo no disponible")

        # Pedidos del usuario.
        respuesta = c.get("/api/v1/orders")
        print("PEDIDOS:", respuesta.status_code)

        if respuesta.status_code != 200:
            errores.append("No se pudieron consultar pedidos")
        else:
            pedidos = respuesta.json().get("orders", [])
            print("Pedidos del usuario:", len(pedidos))

            if pedidos:
                pedido_id = pedidos[0]["id"]

                query = """
                query ($id: String!) {
                    resumenPedido(pedidoId: $id) {
                        pedidoId
                        estado
                        total
                        producto {
                            nombre
                            precio
                        }
                    }
                }
                """

                graphql = c.post("/graphql", json={
                    "query": query,
                    "variables": {"id": pedido_id}
                })

                print("GRAPHQL:", graphql.status_code)

                if graphql.status_code != 200:
                    errores.append("GraphQL HTTP incorrecto")
                else:
                    datos = graphql.json()

                    if datos.get("errors"):
                        errores.append(
                            f"GraphQL: {datos['errors']}"
                        )
                    elif (
                        datos.get("data", {})
                        .get("resumenPedido", {})
                        .get("pedidoId") != pedido_id
                    ):
                        errores.append("GraphQL: datos incorrectos")
                    else:
                        print("GRAPHQL REAL: OK")
            else:
                errores.append("No hay pedidos para probar GraphQL")

        # Comprobar sesión.
        sesion = c.get("/auth/me")
        print("SESIÓN:", sesion.status_code)

        if sesion.status_code != 200:
            errores.append("Error de sesión")

        # Cerrar sesión.
        logout = c.post("/auth/logout")
        print("LOGOUT:", logout.status_code)

        if logout.status_code not in (200, 204):
            errores.append("Error cerrando sesión")
        else:
            posterior = c.get("/api/v1/orders")
            print("PEDIDOS DESPUÉS DE LOGOUT:", posterior.status_code)

            if posterior.status_code != 401:
                errores.append("La sesión sigue permitiendo acceso")

print("\n=== RESULTADO FINAL ===")

if errores:
    for error in errores:
        print("ERROR:", error)

    print("\nPRUEBAS NO SUPERADAS")
    raise SystemExit(1)

print("PRUEBAS DE INTEGRACIÓN OK")
