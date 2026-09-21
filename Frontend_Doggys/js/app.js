let carrito = JSON.parse(localStorage.getItem("carritoDoggys")) || [];

const contadorCarrito = document.getElementById("contadorCarrito");
const btnCarrito = document.getElementById("btnCarrito");
const cerrarCarrito = document.getElementById("cerrarCarrito");
const carritoPanel = document.getElementById("carritoPanel");
const contenidoCarrito = document.getElementById("contenidoCarrito");


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
            <strong>
                Total:
            </strong>

            <strong>
                $${total.toLocaleString("es-CL")}
            </strong>
        </div>
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

const botonesAgregar = document.querySelectorAll(".btn-agregar");

botonesAgregar.forEach((boton) => {

    boton.addEventListener("click", () => {

        const nombre = boton.dataset.nombre;

        const precio = Number(
            boton.dataset.precio
        );


        agregarProducto(
            nombre,
            precio
        );

    });

});

if (btnCarrito) {

    btnCarrito.addEventListener("click", () => {

        carritoPanel.classList.add("abierto");

        mostrarCarrito();

    });

}

if (cerrarCarrito) {

    cerrarCarrito.addEventListener("click", () => {

        carritoPanel.classList.remove("abierto");

    });

}

const botonesFiltro = document.querySelectorAll(".filtro-btn");

const productos = document.querySelectorAll(".producto-card");


function filtrarProductos(categoria) {

    productos.forEach((producto) => {

        const categoriaProducto =
            producto.dataset.categoria;


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


        if (
            boton.dataset.categoria === categoria
        ) {

            boton.classList.add("activo");

        }

    });

}

botonesFiltro.forEach((boton) => {

    boton.addEventListener("click", () => {

        const categoria =
            boton.dataset.categoria;


        filtrarProductos(categoria);

    });

});

const parametros =
    new URLSearchParams(
        window.location.search
    );

const categoriaURL =
    parametros.get("categoria");


if (categoriaURL) {

    filtrarProductos(categoriaURL);

}

actualizarContador();

mostrarCarrito();

const formLogin = document.getElementById("formLogin");
const mensajeLogin = document.getElementById("mensajeLogin");


if (formLogin) {

    formLogin.addEventListener("submit", (evento) => {

        evento.preventDefault();

        const correo =
            document.getElementById("correo").value;

        const password =
            document.getElementById("password").value;


        if (
            correo.trim() === "" ||
            password.trim() === ""
        ) {

            mensajeLogin.textContent =
                "Debes completar todos los campos.";

            mensajeLogin.className =
                "mensaje-login error";

            return;
        }


        mensajeLogin.textContent =
            "Inicio de sesión realizado correctamente.";

        mensajeLogin.className =
            "mensaje-login exito";

        formLogin.reset();

    });

}