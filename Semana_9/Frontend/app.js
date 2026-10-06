// URL base de tu API Gateway local
const API_URL = "http://localhost:8000";

// Referencias a los elementos exactos de tu nuevo HTML
const formLogin = document.getElementById('formLogin');
const estadoLogin = document.getElementById('estadoLogin');
const estadoPanel = document.getElementById('estadoPanel');
const resultadoApi = document.getElementById('resultadoApi');
const nombreUsuarioSpan = document.getElementById('nombreUsuario');
const btnPerfil = document.getElementById('btnPerfil');
const btnProductos = document.getElementById('btnProductos');
const btnCerrarSesion = document.getElementById('btnCerrarSesion');

// 1. INICIAR SESIÓN (Manejando el "submit" del formulario)
formLogin.addEventListener('submit', async function(e) {
    e.preventDefault(); // Evita que la página se recargue al presionar el botón

    // Captura los valores de tus nuevos inputs
    const username = document.getElementById('usuario').value.trim();
    const password = document.getElementById('clave').value.trim();

    if (!username || !password) {
        alert("Por favor, ingresa el usuario y la contraseña.");
        return;
    }

    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include", // CLAVE: Permite guardar la cookie HttpOnly
            body: JSON.stringify({ username, password })
        });

        if (response.ok) {
            // Animación: Ocultar login y mostrar panel
            estadoLogin.classList.add('hidden');
            estadoPanel.classList.remove('hidden');
            
            // Actualizar nombre en la pantalla
            nombreUsuarioSpan.textContent = username;
            resultadoApi.textContent = "¡Login exitoso!\nLa cookie de seguridad se ha guardado correctamente.";
        } else {
            alert("❌ Credenciales incorrectas. (Recuerda usar ana o ernesto)");
        }
    } catch (error) {
        alert("Error de red conectando al Gateway en localhost:8000.");
    }
});

// 2. CONSULTAR PERFIL (Usuario actual)
btnPerfil.addEventListener('click', async function() {
    resultadoApi.textContent = "Consultando perfil al servidor...";
    try {
        const response = await fetch(`${API_URL}/auth/me`, {
            credentials: "include" // Envía la cookie automáticamente
        });
        const data = await response.json();
        resultadoApi.textContent = JSON.stringify(data, null, 2);
    } catch (error) {
        resultadoApi.textContent = "Error al consultar perfil.";
    }
});

// 3. CONSULTAR PRODUCTOS
btnProductos.addEventListener('click', async function() {
    resultadoApi.textContent = "Buscando productos en el Backend...";
    try {
        const response = await fetch(`${API_URL}/api/products`, {
            credentials: "include"
        });
        
        if (response.status === 401) {
            resultadoApi.textContent = "Error 401: No autorizado. La sesión es inválida.";
            return;
        }

        const data = await response.json();
        resultadoApi.textContent = JSON.stringify(data, null, 2);
    } catch (error) {
        resultadoApi.textContent = "Error al consultar productos.";
    }
});

// 4. CERRAR SESIÓN (LOGOUT)
btnCerrarSesion.addEventListener('click', async function() {
    try {
        await fetch(`${API_URL}/auth/logout`, {
            method: "POST",
            credentials: "include"
        });
        
        // Volver visualmente a la pantalla de login
        estadoPanel.classList.add('hidden');
        estadoLogin.classList.remove('hidden');
        formLogin.reset(); // Limpia los inputs
        
        alert("Sesión cerrada exitosamente.");
    } catch (error) {
        console.error("Error en logout", error);
    }
});