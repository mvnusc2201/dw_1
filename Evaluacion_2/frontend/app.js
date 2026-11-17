let carrito = JSON.parse(localStorage.getItem("carritoDoggys")) || [];

const contadorCarrito = document.getElementById("contadorCarrito");
const btnCarrito = document.getElementById("btnCarrito");
const cerrarCarrito = document.getElementById("cerrarCarrito");
const carritoPanel = document.getElementById("carritoPanel");
const contenidoCarrito = document.getElementById("contenidoCarrito");

function guardarCarrito() {
    localStorage.setItem("carritoDoggys", JSON.stringify(carrito));
}

function actualizarContador() {
    if (!contadorCarrito) return;
    contadorCarrito.textContent = carrito.length;
}

function mostrarCarrito() {
    if (!contenidoCarrito) return;
    if (carrito.length === 0) {
        // Vacío: el mensaje "Tu carrito está vacío" lo muestra el HTML (solo aparece si este contenedor está vacío)
        contenidoCarrito.innerHTML = "";
        return;
    }

    let total = 0;
    let html = '<div class="space-y-4">';

    carrito.forEach((producto, indice) => {
        total += producto.precio;
        html += `
            <div class="flex justify-between items-center border-b pb-3">
                <div>
                    <strong class="text-[var(--ink)] block">${producto.nombre}</strong>
                    <p class="text-[var(--doggis-red)] font-bold">$${producto.precio.toLocaleString("es-CL")}</p>
                </div>
                <button class="text-red-500 font-bold hover:text-red-700 text-lg cursor-pointer" onclick="eliminarProducto(${indice})">✕</button>
            </div>
        `;
    });

    html += `
        </div>
        <div class="mt-6 pt-4 border-t-2 border-[var(--doggis-yellow)] flex justify-between items-center">
            <strong class="text-xl text-[var(--ink)]">Total:</strong>
            <strong class="text-xl text-[var(--doggis-red)]">$${total.toLocaleString("es-CL")}</strong>
        </div>
        <button class="w-full mt-6 bg-[var(--doggis-red)] text-white py-3 rounded-full font-bold shadow-md hover:bg-[#D62828] cursor-pointer">Ir a pagar</button>
    `;
    contenidoCarrito.innerHTML = html;
}

function agregarProducto(nombre, precio) {
    carrito.push({ nombre: nombre, precio: precio });
    guardarCarrito();
    actualizarContador();
    mostrarCarrito();
    if (carritoPanel) carritoPanel.classList.remove("translate-x-full");
}

// Necesario en el objeto global para que funcione el onclick del botón eliminar
window.eliminarProducto = function(indice) {
    carrito.splice(indice, 1);
    guardarCarrito();
    actualizarContador();
    mostrarCarrito();
};

document.addEventListener("DOMContentLoaded", () => {
    actualizarContador();
    mostrarCarrito();

    const botonesAgregar = document.querySelectorAll(".btn-agregar");
    botonesAgregar.forEach((boton) => {
        boton.addEventListener("click", () => {
            const nombre = boton.dataset.nombre;
            const precio = Number(boton.dataset.precio);
            if (nombre && precio >= 0) {
                agregarProducto(nombre, precio);
            }
        });
    });

    if (btnCarrito) {
        btnCarrito.addEventListener("click", () => {
            carritoPanel.classList.remove("translate-x-full");
            mostrarCarrito();
        });
    }

    if (cerrarCarrito) {
        cerrarCarrito.addEventListener("click", () => {
            carritoPanel.classList.add("translate-x-full");
        });
    }
});
// ==========================================
// REGISTRO DE USUARIOS - DOGGY'S
// ==========================================

const btnMostrarRegistro = document.getElementById("btnMostrarRegistro");
const btnVolverLogin = document.getElementById("btnVolverLogin");
const registroPanel = document.getElementById("registroPanel");
const formRegistro = document.getElementById("formRegistro");
const mensajeRegistro = document.getElementById("mensajeRegistro");

// Mostrar el formulario de registro
if (btnMostrarRegistro && registroPanel && formLogin) {
    btnMostrarRegistro.addEventListener("click", () => {
        formLogin.style.display = "none";
        registroPanel.style.display = "block";

        mensajeLogin.textContent = "";
        mensajeRegistro.textContent = "";
    });
}

// Volver al formulario de login
if (btnVolverLogin && registroPanel && formLogin) {
    btnVolverLogin.addEventListener("click", () => {
        registroPanel.style.display = "none";
        formLogin.style.display = "";

        mensajeRegistro.textContent = "";
    });
}

// Registrar una cuenta nueva
if (formRegistro) {
    formRegistro.addEventListener("submit", async (evento) => {
        evento.preventDefault();

        const nombre = document.getElementById("registroNombre").value.trim();
        const correo = document.getElementById("registroCorreo").value.trim().toLowerCase();
        const telefono = document.getElementById("registroTelefono").value.trim();
        const clave = document.getElementById("registroClave").value;
        const aceptaTerminos = document.getElementById("registroTerminos").checked;

        const boton = formRegistro.querySelector('button[type="submit"]');

        if (!aceptaTerminos) {
            mensajeRegistro.textContent = "Debes aceptar los términos y condiciones.";
            mensajeRegistro.className = "mensaje-login error";
            return;
        }

        if (boton) boton.disabled = true;

        mensajeRegistro.textContent = "Creando tu cuenta...";
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
                    throw new Error("Este correo ya está registrado.");
                }

                if (respuesta.status === 422 || respuesta.status === 400) {
                    throw new Error("Revisa los datos ingresados, especialmente el teléfono y la contraseña.");
                }

                if (respuesta.status === 503) {
                    throw new Error("No se pudo completar el registro. Inténtalo nuevamente.");
                }

                throw new Error("Ocurrió un error al crear la cuenta.");
            }

            // Registro creado correctamente
            formRegistro.reset();

            registroPanel.style.display = "none";
            formLogin.style.display = "";

            // Completar automáticamente el correo del login
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