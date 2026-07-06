import httpx
from app.config import get_settings

WHATSAPP_API_URL = "https://graph.facebook.com/v21.0"


async def send_text_message(to: str, text: str) -> dict:
    """Envía un mensaje de texto via WhatsApp Cloud API."""
    settings = get_settings()
    url = f"{WHATSAPP_API_URL}/{settings.whatsapp_phone_number_id}/messages"

    # WhatsApp tiene límite de 4096 caracteres por mensaje
    if len(text) > 4096:
        text = text[:4090] + "\n..."

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {"preview_url": False, "body": text},
    }

    headers = {
        "Authorization": f"Bearer {settings.whatsapp_access_token}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers, timeout=30.0)
        return response.json()
