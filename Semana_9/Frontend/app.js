// URL base de tu API Gateway
const API_URL = "http://localhost:8000";

// 1. LOGIN
async function iniciarSesion() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const msg = document.getElementById("login-msg");

    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include", // CLAVE: Permite guardar la cookie HttpOnly
            body: JSON.stringify({ username, password })
        });

        if (response.ok) {
            document.getElementById("panel-login").style.display = "none";
            document.getElementById("panel-sistema").style.display = "block";
            document.getElementById("resultado").innerText = "¡Login exitoso! La cookie de sesión ha sido guardada.";
        } else {
            msg.innerText = "❌ Credenciales incorrectas";
            msg.style.color = "red";
        }
    } catch (error) {
        msg.innerText = "Error de red conectando al Gateway.";
    }
}

// 2. CONSULTAR PERFIL (Usuario actual)
async function consultarPerfil() {
    try {
        const response = await fetch(`${API_URL}/auth/me`, {
            credentials: "include" // Envía la cookie automáticamente
        });
        const data = await response.json();
        document.getElementById("resultado").innerText = JSON.stringify(data, null, 2);
    } catch (error) {
        document.getElementById("resultado").innerText = "Error al consultar perfil.";
    }
}

// 3. CONSULTAR PRODUCTOS
async function consultarProductos() {
    try {
        const response = await fetch(`${API_URL}/api/products`, {
            credentials: "include"
        });
        
        if (response.status === 401) {
            document.getElementById("resultado").innerText = "Error 401: No autorizado. Inicia sesión primero.";
            return;
        }

        const data = await response.json();
        document.getElementById("resultado").innerText = JSON.stringify(data, null, 2);
    } catch (error) {
        document.getElementById("resultado").innerText = "Error al consultar productos.";
    }
}

// 4. LOGOUT
async function cerrarSesion() {
    try {
        await fetch(`${API_URL}/auth/logout`, {
            method: "POST",
            credentials: "include"
        });
        
        // Volver al panel de login
        document.getElementById("panel-sistema").style.display = "none";
        document.getElementById("panel-login").style.display = "block";
        document.getElementById("username").value = "";
        document.getElementById("password").value = "";
        document.getElementById("login-msg").innerText = "Sesión cerrada correctamente.";
        document.getElementById("login-msg").style.color = "green";
    } catch (error) {
        console.error("Error en logout", error);
    }
}