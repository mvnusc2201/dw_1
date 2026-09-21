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