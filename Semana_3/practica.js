const productos = [];
function agregarProducto() {
    let id = document.getElementById("txtId").value;
    let nombre = document.getElementById("txtNombre").value;
    let precio = document.getElementById("txtPrecio").value;
    const producto = {
        id: id,
        nombre: nombre,
        precio: precio
    };
    productos.push(producto);
    let cmbProductos = document.getElementById("cmbProductos");
    let opcion = document.createElement("option");
    opcion.value = producto.id;
    opcion.innerText =
        producto.nombre + " - $" + producto.precio;
    cmbProductos.appendChild(opcion);
    console.log(producto);
    console.log(productos);
}