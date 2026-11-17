import os

import httpx


class ClientsServiceError(Exception):
    """Error de comunicación o respuesta de Clients Service."""


def crear_perfil_cliente(
    user_id: str,
    nombre: str,
    correo: str,
    telefono: str,
) -> dict:
    """Crea el perfil mediante la API interna de Clients Service."""

    base_url = os.getenv("CLIENTS_SERVICE_URL")
    internal_key = os.getenv("CLIENTS_INTERNAL_KEY")

    if not base_url or not internal_key:
        raise ClientsServiceError(
            "Configuración interna de Clients Service incompleta"
        )

    payload = {
        "user_id": user_id,
        "nombre": nombre,
        "correo": correo,
        "telefono": telefono,
    }

    try:
        with httpx.Client(timeout=5.0, trust_env=False) as client:
            response = client.post(
                f"{base_url.rstrip('/')}/clientes/internal/register",
                json=payload,
                headers={
                    "X-Internal-Key": internal_key,
                },
            )

            if response.status_code not in (200, 201):
                raise ClientsServiceError(
                    f"Clients Service respondió HTTP {response.status_code}"
                )

            perfil = response.json()

            if (
                perfil.get("user_id") != user_id
                or perfil.get("email") != correo.strip().lower()
            ):
                raise ClientsServiceError(
                    "El perfil devuelto no coincide con la identidad"
                )

            return perfil

    except (httpx.RequestError, ValueError) as error:
        raise ClientsServiceError(
            "No se pudo completar el registro del perfil"
        ) from error