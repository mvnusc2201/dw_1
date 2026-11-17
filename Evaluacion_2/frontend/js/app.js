
let carrito = JSON.parse(localStorage.getItem("carritoDoggys")) || [];

const contadorCarrito = document.getElementById("contadorCarrito");
const btnCarrito = document.getElementById("btnCarrito");
const cerrarCarrito = document.getElementById("cerrarCarrito");
const carritoPanel = document.getElementById("carritoPanel");
const contenidoCarrito = document.getElementById("contenidoCarrito");

const fondoCarrito = document.getElementById("fondoCarrito");

function cambiarEstadoCarrito(abierto) {
    if (!carritoPanel) return;
    const abiertoNormalizado = Boolean(abierto);
    carritoPanel.classList.toggle("abierto", abiertoNormalizado);
    carritoPanel.setAttribute("aria-hidden", String(!abiertoNormalizado));
    document.body.classList.toggle("carrito-visible", abiertoNormalizado);
    if (btnCarrito) btnCarrito.setAttribute("aria-expanded", String(abiertoNormalizado));
    if (!abiertoNormalizado && btnCarrito) btnCarrito.focus({ preventScroll: true });
}


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

function formatoCLP(valor) {
    return "$" + Number(valor).toLocaleString("es-CL");
}

function escaparHTML(valor) {
    return String(valor).replace(/[&<>"']/g, (c) => (
        { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]
    ));
}

function mostrarCarrito() {
    if (!contenidoCarrito) return;

    if (carrito.length === 0) {
        // Vacío: el HTML muestra "Tu carrito está vacío" mientras este contenedor no tenga hijos.
        contenidoCarrito.innerHTML = "";
        return;
    }

    let total = 0;
    let html = "";

    carrito.forEach((producto, indice) => {
        total += producto.precio;

        html += `
            <div class="flex items-center justify-between gap-3 border-b border-gray-100 py-3">
                <div class="min-w-0">
                    <strong class="block text-[15px] text-[var(--ink)]">${escaparHTML(producto.nombre)}</strong>
                    <p class="font-bold text-[var(--doggis-red)]">${formatoCLP(producto.precio)}</p>
                </div>
                <button
                    type="button"
                    class="btn-eliminar cursor-pointer rounded-full px-2 py-1 text-lg font-bold text-gray-400 hover:text-[var(--doggis-red)]"
                    onclick="eliminarProducto(${indice})"
                    aria-label="Eliminar ${escaparHTML(producto.nombre)}"
                >✕</button>
            </div>
        `;
    });

    html += `
        <div class="total-carrito mt-5 flex items-center justify-between border-t-2 border-[var(--doggis-yellow)] pt-4">
            <strong class="text-xl">Total:</strong>
            <strong class="text-xl text-[var(--doggis-red)]">${formatoCLP(total)}</strong>
        </div>
        <button
            type="button"
            id="btnConfirmarPedidoReal"
            class="mt-6 w-full cursor-pointer rounded-full bg-[var(--doggis-red)] py-3 font-bold text-white shadow-md transition hover:brightness-90 disabled:cursor-wait disabled:opacity-60"
        >
            Pagar (simulado)
        </button>
    `;

    contenidoCarrito.innerHTML = html;
}

function mostrarEstadoPedido(texto, tipo) {
    const estado = document.getElementById("estadoPedido");
    if (!estado) return;
    estado.textContent = texto;
    estado.className = "estado-pedido" + (tipo ? " " + tipo : "");
}

function agregarProducto(nombre, precio) {
    carrito.push({
        nombre: nombre,
        precio: precio
    });

    guardarCarrito();
    actualizarContador();
    mostrarCarrito();

    mostrarEstadoPedido("");

    cambiarEstadoCarrito(true);
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
        cambiarEstadoCarrito(true);
        mostrarCarrito();
    });
}

if (cerrarCarrito) {
    cerrarCarrito.addEventListener("click", () => cambiarEstadoCarrito(false));
}

if (fondoCarrito) {
    fondoCarrito.addEventListener("click", () => cambiarEstadoCarrito(false));
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
            actualizarCabeceraSesion();

            // Si vino desde el carrito, regresar sin perder sus productos.
            const volver = new URLSearchParams(window.location.search).get("volver");
            if (volver === "/productos.html" || volver === "/index.html") {
                window.location.assign(volver);
            }

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

            actualizarCabeceraSesion();

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
    if (procesandoPedidoDoggys || carrito.length === 0) return;

    procesandoPedidoDoggys = true;
    const boton = contenidoCarrito?.querySelector("#btnConfirmarPedidoReal");
    if (boton) {
        boton.disabled = true;
        boton.textContent = "Procesando pedido...";
    }

    let pedidosCreados = 0;
    let pagosPendientes = 0;
    const comprobantes = [];

    try {
        // Una misma sesión permite comprar desde inicio o desde productos.
        const sesion = await fetch("/auth/me", {
            credentials: "same-origin",
            cache: "no-store"
        });

        if (sesion.status === 401) {
            mostrarEstadoPedido("Inicia sesión para continuar. El carrito se conserva.", "error");
            const destino = window.location.pathname.endsWith("/productos.html")
                ? "/productos.html"
                : "/index.html";
            window.location.assign(
                "/cuenta.html?volver=" + encodeURIComponent(destino)
            );
            return;
        }
        if (!sesion.ok) throw new Error("No se pudo verificar tu sesión.");

        const respuestaCatalogo = await fetch("/api/v1/products", {
            credentials: "same-origin",
            cache: "no-store"
        });
        if (!respuestaCatalogo.ok) {
            throw new Error("No se pudo consultar el catálogo de Inventory.");
        }
        const datos = await respuestaCatalogo.json();
        if (!Array.isArray(datos.products)) {
            throw new Error("El catálogo tiene un formato inválido.");
        }

        // Validar TODO el carrito antes de crear pedidos.
        const porNombre = new Map(
            datos.products.map(p => [normalizarNombreDoggys(p.name), p])
        );
        const grupos = new Map();

        for (const item of carrito) {
            const producto = porNombre.get(normalizarNombreDoggys(item.nombre));
            if (!producto || !producto.available) {
                throw new Error(`Producto no disponible: ${item.nombre}`);
            }
            if (!/^[a-f0-9]{24}$/i.test(String(producto.id || ""))) {
                throw new Error(`ID inválido para ${producto.name}`);
            }
            if (Number(item.precio) !== Number(producto.price_clp)) {
                throw new Error(`Cambió el precio de ${producto.name}. Actualiza el carrito.`);
            }
            const grupo = grupos.get(producto.id) || {
                id: producto.id,
                nombre: producto.name,
                cantidad: 0
            };
            grupo.cantidad++;
            if (grupo.cantidad > 50) {
                throw new Error(`Cantidad máxima superada: ${producto.name}`);
            }
            grupos.set(producto.id, grupo);
        }

        // Contrato real: cada producto distinto crea su propio pedido y pago.
        for (const grupo of grupos.values()) {
            const respuestaPedido = await fetch("/api/v1/orders", {
                method: "POST",
                credentials: "same-origin",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    producto_id: grupo.id,
                    cantidad: grupo.cantidad
                })
            });

            if (!respuestaPedido.ok) {
                const error = await respuestaPedido.json().catch(() => ({}));
                throw new Error(
                    typeof error.detail === "string"
                        ? error.detail
                        : `No se pudo crear el pedido (HTTP ${respuestaPedido.status}).`
                );
            }

            const datosPedido = await respuestaPedido.json();
            const pedido = datosPedido.created;
            if (!pedido || !/^[a-f0-9]{24}$/i.test(String(pedido.id || ""))) {
                throw new Error("La respuesta del pedido es inválida. Revisa tus pedidos antes de reintentar.");
            }
            pedidosCreados++;

            // El pedido YA se guardó: retirar del carrito para evitar duplicarlo.
            carrito = carrito.filter(item =>
                normalizarNombreDoggys(item.nombre) !==
                normalizarNombreDoggys(grupo.nombre)
            );
            guardarCarrito();
            actualizarContador();

            // Crear el registro de PAGO PENDIENTE en MongoDB, no un cobro bancario.
            const respuestaPago = await fetch("/api/v1/payments", {
                method: "POST",
                credentials: "same-origin",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ pedido_id: pedido.id })
            });
            if (!respuestaPago.ok) {
                const error = await respuestaPago.json().catch(() => ({}));
                const detalle = typeof error.detail === "string"
                    ? error.detail : `HTTP ${respuestaPago.status}`;
                throw new Error(
                    `Pedido ${pedido.id} guardado, pero no se pudo crear el pago pendiente: ${detalle}. No repitas el pedido.`
                );
            }

            const datosPago = await respuestaPago.json();
            const pago = datosPago.payment;
            if (!pago || pago.pedido_id !== pedido.id || pago.estado !== "pendiente") {
                throw new Error(
                    `Pedido ${pedido.id} creado, pero no se pudo validar el pago. Revisa MongoDB antes de reintentar.`
                );
            }
            pagosPendientes++;
            comprobantes.push(
                `${grupo.nombre} (${grupo.cantidad}): pedido ${pedido.id}, pago ${pago.id} — ${formatoCLP(pago.monto)} pendiente`
            );
        }

        mostrarEstadoPedido(
            `Pedido registrado correctamente. ${pagosPendientes} pago(s) pendiente(s) en MongoDB; no se ha cobrado dinero.\n` +
            comprobantes.join("\n"),
            "exito"
        );
    } catch (error) {
        mostrarEstadoPedido(
            `${error.message} Pedidos creados: ${pedidosCreados}; pagos pendientes registrados: ${pagosPendientes}. ` +
            "Si hubo un error de conexión, revisa tus pedidos antes de intentar nuevamente.",
            "error"
        );
        console.error("Error al registrar el pago pendiente:", error);
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

// ==========================================
// CABECERA: ESTADO DE SESIÓN (todas las páginas)
// ==========================================

async function actualizarCabeceraSesion() {
    const texto = document.getElementById("textoCuenta");
    if (!texto) return;

    try {
        const respuesta = await fetch("/auth/me", {
            method: "GET",
            credentials: "same-origin",
            cache: "no-store"
        });

        texto.textContent = respuesta.ok ? "Mi cuenta" : "Login";
    } catch (error) {
        texto.textContent = "Login";
    }
}

// ==========================================
// CATÁLOGO REAL: precios y disponibilidad desde el Gateway
// ==========================================

function marcarNoDisponible(boton, texto) {
    boton.disabled = true;
    boton.textContent = texto;
    boton.classList.add("opacity-50", "cursor-not-allowed");
}

async function sincronizarCatalogo() {
    const botones = document.querySelectorAll(".btn-agregar");
    if (botones.length === 0) return;

    const aviso = document.getElementById("avisoCatalogo");

    try {
        const respuesta = await fetch("/api/v1/products", {
            credentials: "same-origin",
            cache: "no-store"
        });

        if (!respuesta.ok) throw new Error("Catálogo no disponible");

        const datos = await respuesta.json();
        if (!Array.isArray(datos.products)) throw new Error("Formato inválido");

        const porNombre = new Map(
            datos.products.map((p) => [normalizarNombreDoggys(p.name), p])
        );

        botones.forEach((boton) => {
            const producto = porNombre.get(
                normalizarNombreDoggys(boton.dataset.nombre)
            );

            // Lo que no existe en Inventory no se puede pedir.
            if (!producto) return marcarNoDisponible(boton, "No disponible");
            if (!producto.available) return marcarNoDisponible(boton, "Agotado");

            const precio = Number(producto.price_clp);
            if (!Number.isFinite(precio) || precio < 0) return;

            boton.dataset.precio = String(precio);
            const etiqueta = boton
                .closest("[data-producto]")
                ?.querySelector(".js-precio");
            if (etiqueta) etiqueta.textContent = formatoCLP(precio);
        });

        if (aviso) aviso.hidden = true;
    } catch (error) {
        // Se mantiene el catálogo estático; el pedido se valida igualmente al confirmar.
        if (aviso) aviso.hidden = false;
    }
}

// ==========================================
// MENÚ HAMBURGUESA, ESCAPE Y BUSCADOR INFORMATIVO
// ==========================================

(function inicializarInterfaz() {
    const btnMenu = document.getElementById("btnMenu");
    const menu = document.getElementById("menuPrincipal");

    function abrirMenu(abierto) {
        if (!btnMenu || !menu) return;
        menu.setAttribute("data-open", abierto ? "true" : "false");
        btnMenu.setAttribute("aria-expanded", abierto ? "true" : "false");
    }

    const menuAbierto = () => menu && menu.getAttribute("data-open") === "true";

    if (btnMenu && menu) {
        btnMenu.addEventListener("click", (e) => {
            e.stopPropagation();
            abrirMenu(!menuAbierto());
        });

        menu.addEventListener("click", (e) => {
            if (e.target.closest("a")) abrirMenu(false);
        });

        document.addEventListener("click", (e) => {
            if (menuAbierto() && !menu.contains(e.target) && !btnMenu.contains(e.target)) {
                abrirMenu(false);
            }
        });
    }

    document.addEventListener("keydown", (e) => {
        if (e.key !== "Escape") return;

        if (menuAbierto()) {
            abrirMenu(false);
            btnMenu.focus();
        }

        if (carritoPanel && carritoPanel.classList.contains("abierto")) {
            cambiarEstadoCarrito(false);
        }
    });

    // Buscador de tiendas: solo informativo, no existe un servicio de tiendas.
    const formTiendas = document.getElementById("formTiendas");
    const mensajeTiendas = document.getElementById("mensajeTiendas");

    if (formTiendas) {
        formTiendas.addEventListener("submit", (e) => {
            e.preventDefault();
            if (mensajeTiendas) {
                mensajeTiendas.textContent =
                    "El buscador de tiendas aún no está disponible. Puedes hacer tu pedido desde esta web.";
            }
        });
    }
})();

actualizarCabeceraSesion();
sincronizarCatalogo();
