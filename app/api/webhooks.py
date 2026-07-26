import hashlib
import hmac
from fastapi import APIRouter, Request, Query, HTTPException
from app.config import get_settings
from app.auth.validator import validate_member
from app.whatsapp.client import send_text_message
from app.agent.router import process_message

router = APIRouter()


@router.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(alias="hub.mode", default=""),
    hub_verify_token: str = Query(alias="hub.verify_token", default=""),
    hub_challenge: str = Query(alias="hub.challenge", default=""),
):
    """Verificación del webhook de Meta (subscription)."""
    settings = get_settings()
    if hub_mode == "subscribe" and hub_verify_token == settings.whatsapp_verify_token:
        return int(hub_challenge)
    raise HTTPException(status_code=403, detail="Token de verificación inválido")


def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verifica la firma HMAC-SHA256 del webhook de Meta."""
    expected = hmac.HMAC(
        secret.encode(), payload, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)


@router.post("/webhook")
async def receive_webhook(request: Request):
    """Recibe mensajes de WhatsApp via webhook de Meta."""
    settings = get_settings()

    # Verificar firma del webhook
    signature = request.headers.get("x-hub-signature-256", "")
    body = await request.body()
    if not verify_signature(body, signature, settings.whatsapp_app_secret):
        raise HTTPException(status_code=401, detail="Firma inválida")

    data = await request.json()

    # Extraer mensaje del payload de Meta
    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]

        if "messages" not in value:
            return {"status": "no message"}

        message = value["messages"][0]
        phone_number = message["from"]
        message_text = message.get("text", {}).get("body", "")

        if not message_text:
            return {"status": "no text"}

    except (KeyError, IndexError):
        return {"status": "invalid payload"}

    # Validar que el usuario es socio
    is_valid = await validate_member(phone_number)
    if not is_valid:
        await send_text_message(
            phone_number,
            "Lo siento, este servicio está disponible solo para socios de CACF. "
            "Contacte a la cámara para más información."
        )
        return {"status": "unauthorized"}

    # Procesar mensaje y generar respuesta
    response_text = await process_message(phone_number, message_text)
    await send_text_message(phone_number, response_text)

    return {"status": "processed"}
