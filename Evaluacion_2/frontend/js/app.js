
let carrito = JSON.parse(localStorage.getItem("carritoDoggys")) || [];

const contadorCarrito = document.getElementById("contadorCarrito");
const btnCarrito = document.getElementById("btnCarrito");
const cerrarCarrito = document.getElementById("cerrarCarrito");
const carritoPanel = document.getElementById("carritoPanel");
const contenidoCarrito = document.getElementById("contenidoCarrito");

// ==========================================
// CARRITO DE COMPRAS
// ==========================================

function guardarCarrito() {
    localStorage.setItem(
        "carritoDoggys",
        JSON.stringify(carrito)
    );
}

function actualizarContador() {
    if (!contadorCarrito) return;

    contadorCarrito.textContent = carrito.length;
}

function mostrarCarrito() {
    if (!contenidoCarrito) return;

    if (carrito.length === 0) {
        contenidoCarrito.innerHTML = `
            <p>Tu carrito está vacío.</p>
        `;
        return;
    }

    let total = 0;
    let html = "";

    carrito.forEach((producto, indice) => {
        total += producto.precio;

        html += `
            <div class="item-carrito">
                <div>
                    <strong>
                        ${producto.nombre}
                    </strong>

                    <p>
                        $${producto.precio.toLocaleString("es-CL")}
                    </p>
                </div>

                <button
                    class="btn-eliminar"
                    onclick="eliminarProducto(${indice})"
                    aria-label="Eliminar producto"
                >
                    <i class="fa-solid fa-trash"></i>
                </button>
            </div>
        `;
    });

    html += `
        <div class="total-carrito">
            <strong>Total:</strong>
            <strong>
                $${total.toLocaleString("es-CL")}
            </strong>
        </div>
    `;

    // Botón para crear el pedido real.
    html += `
        <button
            type="button"
            id="btnConfirmarPedidoReal"
            class="w-full mt-6 bg-red-600 text-white py-3 rounded-full font-bold cursor-pointer"
        >
            Confirmar pedido
        </button>
    `;

    contenidoCarrito.innerHTML = html;
}

function agregarProducto(nombre, precio) {
    carrito.push({
        nombre: nombre,
        precio: precio
    });

    guardarCarrito();
    actualizarContador();
    mostrarCarrito();

    if (carritoPanel) {
        carritoPanel.classList.add("abierto");
    }
}

function eliminarProducto(indice) {
    carrito.splice(indice, 1);

    guardarCarrito();
    actualizarContador();
    mostrarCarrito();
}

// ==========================================
// BOTONES PARA AGREGAR PRODUCTOS
// ==========================================

const botonesAgregar = document.querySelectorAll(".btn-agregar");

botonesAgregar.forEach((boton) => {
    boton.addEventListener("click", () => {
        const nombre = boton.dataset.nombre;
        const precio = Number(boton.dataset.precio);

        if (!nombre || !Number.isFinite(precio) || precio < 0) {
            console.error("Producto inválido.");
            return;
        }

        agregarProducto(nombre, precio);
    });
});

// ==========================================
// ABRIR Y CERRAR CARRITO
// ==========================================

if (btnCarrito) {
    btnCarrito.addEventListener("click", () => {
        if (!carritoPanel) return;

        carritoPanel.classList.add("abierto");
        mostrarCarrito();
    });
}

if (cerrarCarrito) {
    cerrarCarrito.addEventListener("click", () => {
        if (carritoPanel) {
            carritoPanel.classList.remove("abierto");
        }
    });
}

// ==========================================
// FILTROS DE PRODUCTOS
// ==========================================

const botonesFiltro = document.querySelectorAll(".filtro-btn");
const productos = document.querySelectorAll(".producto-card");

function filtrarProductos(categoria) {
    productos.forEach((producto) => {
        const categoriaProducto = producto.dataset.categoria;

        if (
            categoria === "todos" ||
            categoriaProducto === categoria
        ) {
            producto.classList.remove("oculto");
        } else {
            producto.classList.add("oculto");
        }
    });

    botonesFiltro.forEach((boton) => {
        boton.classList.remove("activo");

        if (boton.dataset.categoria === categoria) {
            boton.classList.add("activo");
        }
    });
}

botonesFiltro.forEach((boton) => {
    boton.addEventListener("click", () => {
        const categoria = boton.dataset.categoria;
        filtrarProductos(categoria);
    });
});

const parametros = new URLSearchParams(window.location.search);
const categoriaURL = parametros.get("categoria");

if (categoriaURL) {
    filtrarProductos(categoriaURL);
}

actualizarContador();
mostrarCarrito();

// ==========================================
// LOGIN REAL - DOGGY'S
// ==========================================

const formLogin = document.getElementById("formLogin");
const mensajeLogin = document.getElementById("mensajeLogin");

if (formLogin) {
    formLogin.addEventListener("submit", async (evento) => {
        evento.preventDefault();

        const correo = document.getElementById("correo").value.trim();
        const password = document.getElementById("password").value;

        const boton = formLogin.querySelector(
            'button[type="submit"]'
        );

        if (!correo || !password.trim()) {
            mensajeLogin.textContent =
                "Debes completar todos los campos.";

            mensajeLogin.className = "mensaje-login error";
            return;
        }

        if (boton) boton.disabled = true;

        mensajeLogin.textContent = "Iniciando sesión...";
        mensajeLogin.className = "mensaje-login";

        try {
            const respuesta = await fetch("/auth/login", {
                method: "POST",
                credentials: "same-origin",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    username: correo,
                    password: password
                })
            });

            if (!respuesta.ok) {
                if (respuesta.status === 401) {
                    throw new Error(
                        "Correo o contraseña incorrectos."
                    );
                }

                if (respuesta.status === 429) {
                    throw new Error(
                        "Demasiados intentos fallidos. Intenta nuevamente más tarde."
                    );
                }

                if (respuesta.status === 503) {
                    throw new Error(
                        "Servicio de autenticación no disponible."
                    );
                }

                throw new Error(
                    "No fue posible iniciar sesión."
                );
            }

            mensajeLogin.textContent =
                "¡Inicio de sesión exitoso!";

            mensajeLogin.className = "mensaje-login exito";

            formLogin.reset();

            await actualizarEstadoSesion();

        } catch (error) {
            mensajeLogin.textContent = error.message;
            mensajeLogin.className = "mensaje-login error";

            formLogin.reset();

        } finally {
            if (boton) boton.disabled = false;
        }
    });
}

// ==========================================
// ESTADO DE SESIÓN Y LOGOUT
// ==========================================

const btnCerrarSesion = document.getElementById("btnCerrarSesion");

async function actualizarEstadoSesion() {
    if (!formLogin || !btnCerrarSesion) return;

    try {
        const respuesta = await fetch("/auth/me", {
            method: "GET",
            credentials: "same-origin",
            cache: "no-store"
        });

        if (respuesta.status === 401) {
            formLogin.style.display = "";
            btnCerrarSesion.style.display = "none";
            return;
        }

        if (!respuesta.ok) {
            throw new Error(
                "No se pudo comprobar la sesión."
            );
        }

        const usuario = await respuesta.json();

        formLogin.style.display = "none";
        btnCerrarSesion.style.display = "block";

        mensajeLogin.textContent =
            `Sesión iniciada: ${usuario.username}`;

        mensajeLogin.className = "mensaje-login exito";

    } catch (error) {
        mensajeLogin.textContent = error.message;
        mensajeLogin.className = "mensaje-login error";
    }
}

// ==========================================
// CERRAR SESIÓN
// ==========================================

if (btnCerrarSesion) {
    btnCerrarSesion.addEventListener("click", async () => {
        btnCerrarSesion.disabled = true;

        try {
            const respuesta = await fetch("/auth/logout", {
                method: "POST",
                credentials: "same-origin"
            });

            if (!respuesta.ok) {
                throw new Error(
                    "No se pudo cerrar la sesión."
                );
            }

            if (formLogin) {
                formLogin.style.display = "";
            }

            btnCerrarSesion.style.display = "none";

            mensajeLogin.textContent =
                "Sesión cerrada correctamente.";

            mensajeLogin.className = "mensaje-login exito";

        } catch (error) {
            mensajeLogin.textContent = error.message;
            mensajeLogin.className = "mensaje-login error";

        } finally {
            btnCerrarSesion.disabled = false;
        }
    });
}

if (formLogin) {
    actualizarEstadoSesion();
}

// ==========================================
// REGISTRO DE USUARIOS
// ==========================================

const btnMostrarRegistro = document.getElementById(
    "btnMostrarRegistro"
);

const btnVolverLogin = document.getElementById(
    "btnVolverLogin"
);

const registroPanel = document.getElementById(
    "registroPanel"
);

const formRegistro = document.getElementById(
    "formRegistro"
);

const mensajeRegistro = document.getElementById(
    "mensajeRegistro"
);

// ==========================================
// MOSTRAR FORMULARIO DE REGISTRO
// ==========================================

if (btnMostrarRegistro && registroPanel && formLogin) {
    btnMostrarRegistro.addEventListener("click", () => {
        formLogin.style.display = "none";
        registroPanel.style.display = "block";

        mensajeLogin.textContent = "";
        mensajeRegistro.textContent = "";
    });
}

// ==========================================
// VOLVER AL LOGIN
// ==========================================

if (btnVolverLogin && registroPanel && formLogin) {
    btnVolverLogin.addEventListener("click", () => {
        registroPanel.style.display = "none";
        formLogin.style.display = "";

        mensajeRegistro.textContent = "";
    });
}

// ==========================================
// REGISTRAR USUARIO
// ==========================================

if (formRegistro) {
    formRegistro.addEventListener("submit", async (evento) => {
        evento.preventDefault();

        const nombre = document
            .getElementById("registroNombre")
            .value.trim();

        const correo = document
            .getElementById("registroCorreo")
            .value.trim()
            .toLowerCase();

        const telefono = document
            .getElementById("registroTelefono")
            .value.trim();

        const clave = document
            .getElementById("registroClave")
            .value;

        const aceptaTerminos = document
            .getElementById("registroTerminos")
            .checked;

        const boton = formRegistro.querySelector(
            'button[type="submit"]'
        );

        if (!aceptaTerminos) {
            mensajeRegistro.textContent =
                "Debes aceptar los términos y condiciones.";

            mensajeRegistro.className =
                "mensaje-login error";

            return;
        }

        if (boton) boton.disabled = true;

        mensajeRegistro.textContent =
            "Creando tu cuenta...";

        mensajeRegistro.className = "mensaje-login";

        try {
            const respuesta = await fetch("/auth/register", {
                method: "POST",
                credentials: "same-origin",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    nombre,
                    correo,
                    telefono,
                    clave,
                    aceptaTerminos
                })
            });

            if (!respuesta.ok) {
                if (respuesta.status === 409) {
                    throw new Error(
                        "Este correo ya está registrado."
                    );
                }

                if (
                    respuesta.status === 422 ||
                    respuesta.status === 400
                ) {
                    throw new Error(
                        "Revisa los datos ingresados, especialmente el teléfono y la contraseña."
                    );
                }

                if (respuesta.status === 503) {
                    throw new Error(
                        "No se pudo completar el registro. Inténtalo nuevamente."
                    );
                }

                throw new Error(
                    "Ocurrió un error al crear la cuenta."
                );
            }

            formRegistro.reset();

            registroPanel.style.display = "none";
            formLogin.style.display = "";

            document.getElementById("correo").value = correo;

            mensajeLogin.textContent =
                "¡Cuenta creada correctamente! Ahora puedes iniciar sesión.";

            mensajeLogin.className = "mensaje-login exito";
            mensajeRegistro.textContent = "";

        } catch (error) {
            mensajeRegistro.textContent = error.message;
            mensajeRegistro.className = "mensaje-login error";

        } finally {
            if (boton) boton.disabled = false;
        }
    });
}

// ==========================================
// PEDIDOS REALES - DOGGY'S
// ==========================================

let procesandoPedidoDoggys = false;

function normalizarNombreDoggys(valor) {
    return String(valor || "")
        .trim()
        .toLocaleLowerCase("es-CL");
}

// ==========================================
// CONFIRMAR PEDIDO
// ==========================================

async function confirmarPedidoRealDoggys() {
    if (procesandoPedidoDoggys || carrito.length === 0) {
        return;
    }

    procesandoPedidoDoggys = true;

    const boton = contenidoCarrito?.querySelector(
        "#btnConfirmarPedidoReal"
    );

    if (boton) {
        boton.disabled = true;
        boton.textContent = "Registrando pedido...";
    }

    let pedidosCreados = 0;

    try {
        // 1. Verificar sesión del cliente.
        const sesion = await fetch("/auth/me", {
            method: "GET",
            credentials: "same-origin",
            cache: "no-store"
        });

        if (!sesion.ok) {
            throw new Error(
                "Debes iniciar sesión en cuenta.html antes de confirmar el pedido."
            );
        }

        // 2. Consultar catálogo real.
        const respuestaCatalogo = await fetch(
            "/api/v1/products",
            {
                credentials: "same-origin",
                cache: "no-store"
            }
        );

        if (!respuestaCatalogo.ok) {
            throw new Error(
                "No se pudo consultar el catálogo de productos."
            );
        }

        const datosCatalogo = await respuestaCatalogo.json();
        const catalogo = datosCatalogo.products;

        if (!Array.isArray(catalogo)) {
            throw new Error(
                "El catálogo tiene un formato inválido."
            );
        }

        // 3. Validar y agrupar productos.
        const grupos = new Map();

        for (const item of carrito) {
            const producto = catalogo.find((p) =>
                normalizarNombreDoggys(p.name) ===
                normalizarNombreDoggys(item.nombre)
            );

            if (!producto || !producto.available) {
                throw new Error(
                    `Producto no disponible: ${item.nombre}`
                );
            }

            if (
                typeof producto.id !== "string" ||
                !/^[a-f0-9]{24}$/i.test(producto.id)
            ) {
                throw new Error(
                    `ID inválido para ${producto.name}.`
                );
            }

            // Evitar enviar pedidos con precios desactualizados.
            if (
                Number(item.precio) !==
                Number(producto.price_clp)
            ) {
                throw new Error(
                    `El precio de ${producto.name} cambió. Actualiza el carrito antes de comprar.`
                );
            }

            const grupo = grupos.get(producto.id) || {
                id: producto.id,
                nombre: producto.name,
                cantidad: 0
            };

            grupo.cantidad++;

            if (grupo.cantidad > 50) {
                throw new Error(
                    `Cantidad máxima superada: ${producto.name}`
                );
            }

            grupos.set(producto.id, grupo);
        }

        // 4. Crear pedidos reales mediante API Gateway.
        for (const grupo of grupos.values()) {
            const respuestaPedido = await fetch(
                "/api/v1/orders",
                {
                    method: "POST",
                    credentials: "same-origin",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        producto_id: grupo.id,
                        cantidad: grupo.cantidad
                    })
                }
            );

            if (!respuestaPedido.ok) {
                const datosError = await respuestaPedido
                    .json()
                    .catch(() => ({}));

                throw new Error(
                    typeof datosError.detail === "string"
                        ? datosError.detail
                        : `No se pudo crear el pedido (HTTP ${respuestaPedido.status}).`
                );
            }

            pedidosCreados++;

            // Eliminar artículos confirmados.
            carrito = carrito.filter((item) =>
                normalizarNombreDoggys(item.nombre) !==
                normalizarNombreDoggys(grupo.nombre)
            );

            guardarCarrito();
            actualizarContador();
        }

        alert(
            `${pedidosCreados} pedido(s) registrado(s) correctamente. Pago pendiente.`
        );

    } catch (error) {
        const parcial = pedidosCreados > 0
            ? `\nPedidos ya registrados: ${pedidosCreados}.`
            : "";

        alert(
            `${error.message}${parcial}\nAntes de reintentar, revisa tus pedidos si hubo un error de conexión.`
        );

        console.error(
            "Error al confirmar pedido Doggy's:",
            error
        );

    } finally {
        procesandoPedidoDoggys = false;
        mostrarCarrito();
    }
}

// ==========================================
// EVENTO DEL BOTÓN CONFIRMAR PEDIDO
// ==========================================

// El botón se crea dinámicamente,
// por eso utilizamos delegación de eventos.

if (contenidoCarrito) {
    contenidoCarrito.addEventListener("click", (evento) => {
        const boton = evento.target.closest(
            "#btnConfirmarPedidoReal"
        );

        if (boton) {
            confirmarPedidoRealDoggys();
        }
    });
}
