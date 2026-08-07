import httpx
from app.config import get_settings


async def validate_member(phone_number: str) -> bool:
    """Valida si un número de celular corresponde a un socio activo de CACF."""
    settings = get_settings()

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.cacf_socios_api_url}/validar",
                params={"telefono": phone_number},
                headers={"Authorization": f"Bearer {settings.cacf_socios_api_key}"},
                timeout=10.0,
            )
    except httpx.HTTPError:
        # Do not crash webhook processing if socios API is unavailable.
        return False

    if response.status_code == 200:
        data = response.json()
        return data.get("activo", False)

    return False
