const responseAPI = {
    status: 200,
    message: "Productos obtenidos correctamente",
    data: [
        {
            id: 1,
            nombre: "Teclado",
            precio: 15990
        },
        {
            id: 2,
            nombre: "Mouse",
            precio: 9990
        },
        {
            id: 3,
            nombre: "Audifonos",
            precio: 24990
        }
    ]
};

let cmbProductos = document.getElementById("cmbProductos");

responseAPI.data.forEach((producto) => {
    let opcion = document.createElement("option");
    opcion.value = producto.id;
    opcion.innerText = producto.nombre;
    cmbProductos.appendChild(opcion);
});

cmbProductos.addEventListener("change", mostrarProducto);

function mostrarProducto() {
    let idSeleccionado = Number(cmbProductos.value);
    let productoEncontrado = responseAPI.data.find(
        producto => producto.id === idSeleccionado
    );
    let infoProducto = document.getElementById("infoProducto");
    infoProducto.innerText =
        "Producto: " + productoEncontrado.nombre +
        " | Precio: $" + productoEncontrado.precio;
    console.log(productoEncontrado);
}
