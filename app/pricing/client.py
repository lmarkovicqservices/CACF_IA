import httpx
from app.config import get_settings


class PricingClient:
    """Cliente para la API de Precios de CACF."""

    def __init__(self):
        settings = get_settings()
        self.base_url = settings.cacf_precios_api_url
        self.api_key = settings.cacf_precios_api_key

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.api_key}"}

    async def get_precios_referencia(self) -> dict:
        """Obtiene los precios de referencia actuales."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/precios-referencia",
                headers=self._headers(),
                timeout=10.0,
            )
            response.raise_for_status()
            return response.json()

    async def get_costos_silaje(self) -> dict:
        """Obtiene los costos de silaje."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/costos-silaje",
                headers=self._headers(),
                timeout=10.0,
            )
            response.raise_for_status()
            return response.json()

    async def get_costo_materia_seca(self) -> dict:
        """Obtiene el costo por materia seca."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/costo-materia-seca",
                headers=self._headers(),
                timeout=10.0,
            )
            response.raise_for_status()
            return response.json()

    async def get_costos_transporte_mv(self) -> dict:
        """Obtiene los costos de transporte de materia verde."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/costos-transporte-mv",
                headers=self._headers(),
                timeout=10.0,
            )
            response.raise_for_status()
            return response.json()


# Singleton
_client: PricingClient | None = None


def get_pricing_client() -> PricingClient:
    global _client
    if _client is None:
        _client = PricingClient()
    return _client
